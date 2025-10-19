#!/usr/bin/env python3
"""
Silksong ML Controller with Real-time Dashboard (ASYNC STREAMING VERSION)

- Implements async/await streaming patterns for better responsiveness
- Fixed race conditions in Actor state management
- Optimized pynput usage to reduce blocking
- Turn gestures now set a direction state instead of being treated as actions.
- Action queue correctly filters idle predictions.
- Robust, non-blocking, and ready for gameplay.
"""
import socket
import json
import time
import os
import asyncio
from collections import deque
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from scipy.fft import rfft
from scipy.stats import skew, kurtosis
from pynput.keyboard import Controller, Key
from zeroconf import ServiceInfo
from zeroconf.asyncio import AsyncZeroconf


# --- Import local modules ---
def extract_features_from_dataframe(df):
    """
    Extract features from a DataFrame containing sensor readings.

    Args:
        df: DataFrame with columns: accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z

    Returns:
        Dictionary of extracted features
    """
    features = {}
    for axis in ["accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z"]:
        signal = df[axis].dropna()
        if len(signal) > 0:
            features[f"{axis}_mean"] = signal.mean()
            features[f"{axis}_std"] = signal.std()
            features[f"{axis}_min"] = signal.min()
            features[f"{axis}_max"] = signal.max()
            features[f"{axis}_skew"] = skew(signal)
            features[f"{axis}_kurtosis"] = kurtosis(signal)
            if len(signal) > 2:
                fft_vals = np.abs(rfft(signal.to_numpy()))[: len(signal) // 2]
                if len(fft_vals) > 0:
                    features[f"{axis}_fft_max"] = fft_vals.max()
                    features[f"{axis}_fft_mean"] = fft_vals.mean()
    return features


import network_utils


# --- ANSI Colors ---
class Colors:
    GREEN, RED, YELLOW, BLUE, CYAN, RESET, BOLD = (
        "\033[92m",
        "\033[91m",
        "\033[93m",
        "\033[94m",
        "\033[96m",
        "\033[0m",
        "\033[1m",
    )


# --- Shared State for Dashboard ---
class SharedState:
    def __init__(self):
        self.watch_connected = False
        self.last_watch_data_time = 0
        self.sensor_data_rate = 0.0
        self.last_locomotion_pred = ("-", 0.0)
        self.last_action_pred = ("-", 0.0)
        self.current_actor_state = "Idle"


# --- Configuration & Setup ---
config = network_utils.setup_config()
LISTEN_IP, LISTEN_PORT = (
    config["network"]["listen_ip"],
    config["network"]["listen_port"],
)
KEY_MAP = {"left": Key.left, "right": Key.right, "jump": "z", "attack": "x"}
ML_CONFIDENCE_THRESHOLD = 0.50  # Reduced from 0.60 for better responsiveness
CONSENSUS_WINDOW = 2  # Reduced from 3 - require 2 matching predictions

MODELS_DIR = Path(__file__).resolve().parents[1] / "models"
# Binary classifier: simple walk vs idle (no noise needed here)
BINARY_CLASSES = ["walk", "idle"]
# Multiclass: all actions including noise filtering
MULTI_CLASSES = ["jump", "punch", "turn_left", "turn_right", "idle", "noise"]

# --- Model Loading ---
models_binary = joblib.load(MODELS_DIR / "gesture_classifier_binary.pkl")
scaler_binary = joblib.load(MODELS_DIR / "feature_scaler_binary.pkl")
features_binary = joblib.load(MODELS_DIR / "feature_names_binary.pkl")
models_multiclass = joblib.load(MODELS_DIR / "gesture_classifier_multiclass.pkl")
scaler_multiclass = joblib.load(MODELS_DIR / "feature_scaler_multiclass.pkl")
features_multiclass = joblib.load(MODELS_DIR / "feature_names_multiclass.pkl")


# --- Worker Coroutines ---
async def distributor(sensor_queues, state):
    """Async distributor that streams sensor data to queues"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((LISTEN_IP, LISTEN_PORT))
    sock.setblocking(False)

    rate_tracker = deque(maxlen=100)
    latest_accel = {"x": 0, "y": 0, "z": 0}
    latest_gyro = {"x": 0, "y": 0, "z": 0}

    while True:
        try:
            data, _ = sock.recvfrom(2048)
            msg = json.loads(data.decode())
            sensor_type, values = msg.get("sensor"), msg.get("values", {})

            if sensor_type == "linear_acceleration":
                latest_accel = values
            elif sensor_type == "gyroscope":
                latest_gyro = values
            else:
                await asyncio.sleep(0)
                continue

            combined_reading = {
                "accel_x": latest_accel.get("x", 0),
                "accel_y": latest_accel.get("y", 0),
                "accel_z": latest_accel.get("z", 0),
                "gyro_x": latest_gyro.get("x", 0),
                "gyro_y": latest_gyro.get("y", 0),
                "gyro_z": latest_gyro.get("z", 0),
            }

            # Stream to all queues without blocking
            for q in sensor_queues:
                if q.qsize() < q.maxsize:
                    await q.put(combined_reading)

            now = time.time()
            rate_tracker.append(now)
            state.last_watch_data_time = now
            if len(rate_tracker) > 1:
                state.sensor_data_rate = len(rate_tracker) / (
                    rate_tracker[-1] - rate_tracker[0]
                )
        except BlockingIOError:
            # No data available, yield control
            await asyncio.sleep(0.001)
        except (json.JSONDecodeError, KeyError):
            await asyncio.sleep(0)
            continue


async def predictor(
    sensor_queue,
    result_queue,
    model,
    scaler,
    feature_names,
    classes,
    window_size,
    state,
    pred_type,
):
    """Async predictor that streams predictions"""
    buffer = deque(maxlen=window_size)
    prediction_history = deque(maxlen=CONSENSUS_WINDOW)

    while True:
        try:
            # Non-blocking get with timeout
            reading = await asyncio.wait_for(sensor_queue.get(), timeout=1.0)
            buffer.append(reading)

            if len(buffer) == window_size:
                features_dict = extract_features_from_dataframe(
                    pd.DataFrame(list(buffer))
                )
                features_vec = np.array(
                    [features_dict.get(name, 0) for name in feature_names]
                ).reshape(1, -1)
                features_scaled = scaler.transform(features_vec)
                probs = model.predict_proba(features_scaled)[0]
                confidence, gesture_idx = probs.max(), probs.argmax()
                gesture = classes[gesture_idx]

                if pred_type == "loco":
                    state.last_locomotion_pred = (gesture, confidence)
                else:
                    state.last_action_pred = (gesture, confidence)

                if confidence >= ML_CONFIDENCE_THRESHOLD:
                    prediction_history.append(gesture)
                    # Require CONSENSUS_WINDOW matching predictions
                    if (
                        len(prediction_history) == CONSENSUS_WINDOW
                        and len(set(prediction_history)) == 1
                    ):
                        if result_queue.qsize() < result_queue.maxsize:
                            await result_queue.put((gesture, confidence))
                        prediction_history.clear()
        except asyncio.TimeoutError:
            await asyncio.sleep(0)
            continue


async def actor(locomotion_queue, action_queue, state):
    """Async actor that streams actions to keyboard"""
    keyboard = Controller()
    is_walking = False
    facing_direction = "right"  # Start by facing right
    last_action_time = {}
    last_walk_confirmation = time.time()  # Track last walk signal
    WALK_TIMEOUT = 0.8  # Auto-stop walking after 0.8s without confirmation (faster)

    # Track which keys are currently pressed
    pressed_keys = set()

    try:
        while True:
            now = time.time()

            # Process actions FIRST - can stop walking and update direction
            facing_direction, is_walking = await handle_action(
                action_queue,
                keyboard,
                facing_direction,
                is_walking,
                last_action_time,
                state,
                pressed_keys,
            )

            # THEN, process locomotion based on the (potentially new) state
            is_walking, facing_direction, walk_confirmed = await handle_locomotion(
                locomotion_queue,
                keyboard,
                is_walking,
                facing_direction,
                state,
                pressed_keys,
            )

            # Update walk confirmation timestamp if walking was confirmed
            if walk_confirmed:
                last_walk_confirmation = now

            # AUTO-STOP: If walking but no confirmation for WALK_TIMEOUT seconds
            if is_walking and (now - last_walk_confirmation) > WALK_TIMEOUT:
                is_walking = False
                for direction in ["left", "right"]:
                    if direction in pressed_keys:
                        keyboard.release(KEY_MAP[direction])
                        pressed_keys.discard(direction)
                state.current_actor_state = "Idle (timeout)"
                print(f"{Colors.YELLOW}⏱️  Walk timeout - auto-stopping{Colors.RESET}")

            # Yield control to allow other coroutines to run
            await asyncio.sleep(0.02)
    finally:
        # Cleanup - release all pressed keys
        for key in pressed_keys:
            try:
                keyboard.release(KEY_MAP.get(key, key))
            except Exception:
                pass


async def handle_locomotion(
    locomotion_queue, keyboard, is_walking, facing_direction, state, pressed_keys
):
    """Handle locomotion commands from queue - REAL-TIME ONLY"""
    walk_confirmed = False

    # CLEAR OLD PREDICTIONS - Only use the latest one
    latest_gesture = None
    while True:
        try:
            latest_gesture, _ = locomotion_queue.get_nowait()
        except asyncio.QueueEmpty:
            break

    # Process only the most recent prediction
    if latest_gesture:
        state_changed = False

        # Noise or idle while walking = stop walking
        if (latest_gesture == "noise" or latest_gesture == "idle") and is_walking:
            is_walking = False
            # Release both direction keys to ensure clean state
            for direction in ["left", "right"]:
                if direction in pressed_keys:
                    keyboard.release(KEY_MAP[direction])
                    pressed_keys.discard(direction)
            state_changed = True
        elif latest_gesture == "walk" and not is_walking:
            is_walking = True
            key = KEY_MAP[facing_direction]
            keyboard.press(key)
            pressed_keys.add(facing_direction)
            state_changed = True
            walk_confirmed = True
        elif latest_gesture == "walk" and is_walking:
            # Already walking - this is a confirmation
            walk_confirmed = True

        if state_changed:
            state.current_actor_state = (
                f"Walking {facing_direction}" if is_walking else "Idle"
            )

    return is_walking, facing_direction, walk_confirmed


async def handle_action(
    action_queue,
    keyboard,
    facing_direction,
    is_walking,
    last_action_time,
    state,
    pressed_keys,
):
    """Handle action commands from queue - REAL-TIME ONLY"""

    # CLEAR OLD PREDICTIONS - Only use the latest one
    latest_gesture = None
    latest_confidence = 0.0
    while True:
        try:
            latest_gesture, latest_confidence = action_queue.get_nowait()
        except asyncio.QueueEmpty:
            break

    # Process only the most recent prediction
    if latest_gesture:
        # Filter out noise predictions
        if latest_gesture == "noise":
            return facing_direction, is_walking

        now = time.time()

        # Handle STATE changes (turns) immediately. No cooldown.
        if latest_gesture in ["turn_left", "turn_right"]:
            new_direction = latest_gesture.split("_")[1]
            if facing_direction != new_direction:
                # Update direction
                old_direction = facing_direction
                facing_direction = new_direction

                # If walking, swap the pressed keys
                if is_walking:
                    if old_direction in pressed_keys:
                        keyboard.release(KEY_MAP[old_direction])
                        pressed_keys.discard(old_direction)
                    keyboard.press(KEY_MAP[facing_direction])
                    pressed_keys.add(facing_direction)
                    state.current_actor_state = f"Walking {facing_direction}"

        # Handle INSTANT actions (punch/jump) - THESE STOP WALKING
        elif latest_gesture in ["jump", "punch"]:
            cooldown = last_action_time.get(latest_gesture, 0)
            if now - cooldown > 0.3:  # 300ms cooldown per action type
                # CRITICAL FIX: Stop walking when performing actions
                if is_walking:
                    is_walking = False
                    for direction in ["left", "right"]:
                        if direction in pressed_keys:
                            keyboard.release(KEY_MAP[direction])
                            pressed_keys.discard(direction)
                    print(f"{Colors.CYAN}🛑 Stopped walking to perform action{Colors.RESET}")

                # Perform the action
                if latest_gesture == "jump":
                    keyboard.press(KEY_MAP["jump"])
                    keyboard.release(KEY_MAP["jump"])
                elif latest_gesture == "punch":
                    keyboard.press(KEY_MAP["attack"])
                    keyboard.release(KEY_MAP["attack"])

                last_action_time[latest_gesture] = now
                state.current_actor_state = f"{latest_gesture.capitalize()}!"

    return facing_direction, is_walking


async def dashboard(state, queues):
    """Async dashboard display"""
    while True:
        state.watch_connected = (time.time() - state.last_watch_data_time) < 2.0
        os.system("cls" if os.name == "nt" else "clear")
        print(
            f"{Colors.BOLD}{Colors.CYAN}{'='*60}\n      Silksong ML Controller - Live Dashboard (STREAMING)\n{'='*60}{Colors.RESET}"
        )
        watch_status = (
            f"{Colors.GREEN}✓ CONNECTED{Colors.RESET}"
            if state.watch_connected
            else f"{Colors.RED}✗ DISCONNECTED{Colors.RESET}"
        )
        print(
            f"\n{Colors.BOLD}Watch Status: {watch_status}  |  Data Rate: {state.sensor_data_rate:.1f} Hz"
        )
        loco_pred, loco_conf = state.last_locomotion_pred
        act_pred, act_conf = state.last_action_pred
        print(f"\n{Colors.BOLD}--- LATEST PREDICTION (Live) ---{Colors.RESET}")
        print(
            f"Locomotion : {Colors.YELLOW}{loco_pred.upper():<12}{Colors.RESET} (Conf: {loco_conf:.0%})"
        )
        print(
            f"Action     : {Colors.YELLOW}{act_pred.upper():<12}{Colors.RESET} (Conf: {act_conf:.0%})"
        )
        print(f"\n{Colors.BOLD}--- CONTROLLER STATE ---{Colors.RESET}")
        print(f"Actor State: {Colors.GREEN}{state.current_actor_state}{Colors.RESET}")
        print(f"\n{Colors.BOLD}--- INTERNAL QUEUES ---{Colors.RESET}")
        print(
            f"Locomotion Results: {queues['result_loco'].qsize()}  |  Action Results: {queues['result_action'].qsize()}"
        )
        print(f"\n{Colors.BOLD}Press Ctrl+C to stop.{Colors.RESET}")
        await asyncio.sleep(0.2)


async def main_async():
    shared_state = SharedState()

    # Create async queues
    queues = {
        "sensor_loco": asyncio.Queue(500),
        "sensor_action": asyncio.Queue(200),
        "result_loco": asyncio.Queue(10),
        "result_action": asyncio.Queue(10),
    }

    # Use AsyncZeroconf for async context
    aiozc = AsyncZeroconf()
    service_info = ServiceInfo(
        "_silksong._udp.local.",
        "SilksongController._silksong._udp.local.",
        addresses=[socket.inet_aton(LISTEN_IP)],
        port=LISTEN_PORT,
    )

    try:
        await aiozc.async_register_service(service_info)
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  Service registration skipped: {e}{Colors.RESET}")
        # Continue anyway - the UDP listener will still work

    try:
        # Create and run all async tasks concurrently
        await asyncio.gather(
            distributor([queues["sensor_loco"], queues["sensor_action"]], shared_state),
            predictor(
                queues["sensor_loco"],
                queues["result_loco"],
                models_binary,
                scaler_binary,
                features_binary,
                BINARY_CLASSES,
                250,
                shared_state,
                "loco",
            ),
            predictor(
                queues["sensor_action"],
                queues["result_action"],
                models_multiclass,
                scaler_multiclass,
                features_multiclass,
                MULTI_CLASSES,
                75,
                shared_state,
                "action",
            ),
            actor(queues["result_loco"], queues["result_action"], shared_state),
            dashboard(shared_state, queues),
        )
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    finally:
        await aiozc.async_unregister_service(service_info)
        await aiozc.async_close()
        print("✅ Controller stopped.")


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
