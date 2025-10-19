import socket
import json
import time
import math
import threading
from collections import deque
from queue import Queue, Empty
from pynput.keyboard import Controller, Key
import sys
import os
# Add shared_utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared_utils'))
import network_utils
from zeroconf import ServiceInfo, Zeroconf
import joblib
import pandas as pd
import numpy as np
from scipy import stats
from scipy.fft import fft

# --- Global State ---
keyboard = Controller()
is_walking = False
facing_direction = "right"

# --- Configuration Loading ---
def load_config():
    """Load configuration from config.json file"""
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("ERROR: config.json not found! Please create the configuration file.")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in config.json: {e}")
        exit(1)


def get_key(key_string):
    """Converts a string from config to a pynput Key object if needed."""
    if key_string.startswith("Key."):
        key_name = key_string.split(".")[-1]
        if hasattr(Key, key_name):
            return getattr(Key, key_name)
    return key_string


# Load configuration at startup
config = load_config()

# Auto-detect and update IP address
print("🔍 Auto-detecting IP address...")
network_utils.update_config_ip()
config = load_config()

# Extract configuration values
LISTEN_IP = config["network"]["listen_ip"]
LISTEN_PORT = config["network"]["listen_port"]

# Load key mappings from config
KEY_MAP = {
    "left": get_key(config["keyboard_mappings"]["left"]),
    "right": get_key(config["keyboard_mappings"]["right"]),
    "jump": get_key(config["keyboard_mappings"]["jump"]),
    "attack": get_key(config["keyboard_mappings"]["attack"]),
}


# --- ML Model Loading (PARALLEL CLASSIFIERS) ---
def load_parallel_models():
    """Load parallel classifier models: Binary (locomotion) + Multiclass (actions)."""
    from pathlib import Path

    # Find models directory (look in parent directories)
    current_dir = Path(__file__).parent
    models_dir = None

    # Try multiple locations
    search_paths = [
        current_dir / "models",           # Same directory
        current_dir.parent / "models",    # One level up (src/models)
        current_dir.parent.parent / "models",  # Two levels up (project root/models)
    ]

    for path in search_paths:
        if path.exists():
            models_dir = path
            break

    if models_dir is None:
        print("⚠️  Models directory not found. Searched:")
        for path in search_paths:
            print(f"     {path}")
        return None

    models = {}

    # Load Binary Classifier (walk vs idle)
    try:
        models['binary_classifier'] = joblib.load(models_dir / "gesture_classifier_binary.pkl")
        models['binary_scaler'] = joblib.load(models_dir / "feature_scaler_binary.pkl")
        models['binary_feature_names'] = joblib.load(models_dir / "feature_names_binary.pkl")
        print("✅ Binary Classifier loaded (walk vs idle)")
    except FileNotFoundError as e:
        print(f"⚠️  Binary classifier not found: {e}")
        return None

    # Load Multiclass Classifier (jump, punch, turn_left, turn_right)
    try:
        models['multi_classifier'] = joblib.load(models_dir / "gesture_classifier_multiclass.pkl")
        models['multi_scaler'] = joblib.load(models_dir / "feature_scaler_multiclass.pkl")
        models['multi_feature_names'] = joblib.load(models_dir / "feature_names_multiclass.pkl")
        print("✅ Multiclass Classifier loaded (jump, punch, turn_left, turn_right)")
    except FileNotFoundError as e:
        print(f"⚠️  Multiclass classifier not found: {e}")
        return None

    return models


def extract_window_features(window_df):
    """Extract comprehensive features from a time window of sensor data."""
    features = {}

    # Separate by sensor type
    accel = window_df[window_df["sensor"] == "linear_acceleration"]
    gyro = window_df[window_df["sensor"] == "gyroscope"]
    rot = window_df[window_df["sensor"] == "rotation_vector"]

    # ========== ACCELERATION FEATURES ==========
    if len(accel) > 0:
        for axis in ["accel_x", "accel_y", "accel_z"]:
            values = accel[axis].dropna()

            if len(values) > 0:
                features[f"{axis}_mean"] = values.mean()
                features[f"{axis}_std"] = values.std()
                features[f"{axis}_max"] = values.max()
                features[f"{axis}_min"] = values.min()
                features[f"{axis}_range"] = values.max() - values.min()
                features[f"{axis}_median"] = values.median()
                features[f"{axis}_skew"] = stats.skew(values)
                features[f"{axis}_kurtosis"] = stats.kurtosis(values)

                threshold = values.mean() + 2 * values.std()
                features[f"{axis}_peak_count"] = len(values[values > threshold])

                if len(values) > 2:
                    fft_vals = np.abs(fft(values))[: len(values) // 2]
                    if len(fft_vals) > 0:
                        features[f"{axis}_fft_max"] = fft_vals.max()
                        features[f"{axis}_dominant_freq"] = fft_vals.argmax()
                        features[f"{axis}_fft_mean"] = fft_vals.mean()

    # ========== GYROSCOPE FEATURES ==========
    if len(gyro) > 0:
        for axis in ["gyro_x", "gyro_y", "gyro_z"]:
            values = gyro[axis].dropna()

            if len(values) > 0:
                features[f"{axis}_mean"] = values.mean()
                features[f"{axis}_std"] = values.std()
                features[f"{axis}_max_abs"] = values.abs().max()
                features[f"{axis}_range"] = values.max() - values.min()
                features[f"{axis}_skew"] = stats.skew(values)
                features[f"{axis}_kurtosis"] = stats.kurtosis(values)
                features[f"{axis}_rms"] = np.sqrt(np.mean(values**2))

                if len(values) > 2:
                    fft_vals = np.abs(fft(values))[: len(values) // 2]
                    if len(fft_vals) > 0:
                        features[f"{axis}_fft_max"] = fft_vals.max()

    # ========== ROTATION FEATURES ==========
    if len(rot) > 0:
        for axis in ["rot_x", "rot_y", "rot_z", "rot_w"]:
            values = rot[axis].dropna()

            if len(values) > 0:
                features[f"{axis}_mean"] = values.mean()
                features[f"{axis}_std"] = values.std()
                features[f"{axis}_range"] = values.max() - values.min()

    # ========== CROSS-SENSOR FEATURES ==========
    if len(accel) > 0:
        accel_mag = np.sqrt(
            accel["accel_x"].fillna(0) ** 2
            + accel["accel_y"].fillna(0) ** 2
            + accel["accel_z"].fillna(0) ** 2
        )
        features["accel_magnitude_mean"] = accel_mag.mean()
        features["accel_magnitude_max"] = accel_mag.max()
        features["accel_magnitude_std"] = accel_mag.std()

    if len(gyro) > 0:
        gyro_mag = np.sqrt(
            gyro["gyro_x"].fillna(0) ** 2
            + gyro["gyro_y"].fillna(0) ** 2
            + gyro["gyro_z"].fillna(0) ** 2
        )
        features["gyro_magnitude_mean"] = gyro_mag.mean()
        features["gyro_magnitude_max"] = gyro_mag.max()
        features["gyro_magnitude_std"] = gyro_mag.std()

    return features


# Load parallel models
parallel_models = load_parallel_models()
ML_ENABLED = parallel_models is not None

# Configuration for parallel classifiers
# Binary classifier: 5s windows for locomotion (walk vs idle)
# Multiclass classifier: 1-2s windows for actions (jump, punch, turn_left, turn_right)
BINARY_WINDOW_SEC = 5.0  # Walk detection needs longer windows
MULTI_WINDOW_SEC = 1.5   # Actions are quick gestures

BINARY_WINDOW_SAMPLES = int(BINARY_WINDOW_SEC * 50)  # ~250 samples
MULTI_WINDOW_SAMPLES = int(MULTI_WINDOW_SEC * 50)    # ~75 samples

ML_CONFIDENCE_THRESHOLD = 0.6  # Lower threshold for faster response
CONFIDENCE_GATING_COUNT = 3    # Reduced for faster response

# Thread-safe queues
sensor_queue = Queue(maxsize=1000)
locomotion_queue = Queue(maxsize=100)  # Binary predictions
action_queue = Queue(maxsize=100)      # Multiclass predictions

# Gesture name mappings
BINARY_GESTURES = ['walk', 'idle']
MULTI_GESTURES = ['jump', 'punch', 'turn_left', 'turn_right']


# ========================================================================
# PARALLEL ARCHITECTURE: Collector → (Locomotion Predictor + Action Predictor) → Actor
# ========================================================================

def collector_thread(sock, sensor_queue, stop_event):
    """Thread 1: Collect sensor data from UDP and push to queue."""
    print("[COLLECTOR] Thread started")

    while not stop_event.is_set():
        try:
            sock.settimeout(0.1)
            data, addr = sock.recvfrom(2048)

            try:
                parsed_json = json.loads(data.decode())
                current_time = time.time()

                sensor_type = parsed_json.get("sensor")
                sensor_reading = {
                    "timestamp": current_time,
                    "sensor": sensor_type,
                }

                # Add sensor-specific values
                if sensor_type == "linear_acceleration":
                    vals = parsed_json.get("values", {})
                    sensor_reading.update({
                        "accel_x": vals.get("x", 0),
                        "accel_y": vals.get("y", 0),
                        "accel_z": vals.get("z", 0),
                    })
                elif sensor_type == "gyroscope":
                    vals = parsed_json.get("values", {})
                    sensor_reading.update({
                        "gyro_x": vals.get("x", 0),
                        "gyro_y": vals.get("y", 0),
                        "gyro_z": vals.get("z", 0),
                    })
                elif sensor_type == "rotation_vector":
                    vals = parsed_json.get("values", {})
                    sensor_reading.update({
                        "rot_x": vals.get("x", 0),
                        "rot_y": vals.get("y", 0),
                        "rot_z": vals.get("z", 0),
                        "rot_w": vals.get("w", 1),
                    })

                # Push to queue
                try:
                    sensor_queue.put(sensor_reading, timeout=0.01)
                except:
                    pass  # Queue full, drop packet

            except json.JSONDecodeError:
                pass

        except socket.timeout:
            continue
        except Exception as e:
            if not stop_event.is_set():
                print(f"[COLLECTOR] Error: {e}")
            break

    print("[COLLECTOR] Thread stopped")


def locomotion_predictor_thread(models, sensor_queue, locomotion_queue, stop_event):
    """Thread 2a: Binary classifier for locomotion (walk vs idle) with 5s windows."""
    print("[LOCOMOTION] Thread started (5s windows)")

    # Large buffer for walk detection
    sensor_buffer = deque(maxlen=BINARY_WINDOW_SAMPLES)
    prediction_count = 0

    while not stop_event.is_set():
        try:
            # Collect data
            try:
                sensor_reading = sensor_queue.get(timeout=0.01)
                sensor_buffer.append(sensor_reading)
            except Empty:
                pass

            # Predict every N iterations to avoid overwhelming the actor
            prediction_count += 1
            if prediction_count < 10:  # Predict every ~10 iterations
                continue
            prediction_count = 0

            # Run prediction if buffer is sufficiently full
            if len(sensor_buffer) >= int(BINARY_WINDOW_SAMPLES * 0.6):  # 60% full
                try:
                    buffer_df = pd.DataFrame(list(sensor_buffer))
                    features = extract_window_features(buffer_df)

                    # Create feature vector
                    feature_vector = pd.DataFrame([features])
                    feature_vector = feature_vector.reindex(
                        columns=models['binary_feature_names'], fill_value=0
                    )

                    # Scale and predict
                    features_scaled = models['binary_scaler'].transform(feature_vector)
                    prediction = models['binary_classifier'].predict(features_scaled)[0]
                    probabilities = models['binary_classifier'].predict_proba(features_scaled)[0]
                    confidence = probabilities[prediction]

                    # Map prediction to gesture name
                    gesture = BINARY_GESTURES[prediction]

                    # Push to locomotion queue
                    if confidence >= ML_CONFIDENCE_THRESHOLD:
                        locomotion_action = {
                            "gesture": gesture,
                            "confidence": confidence,
                            "timestamp": time.time()
                        }
                        try:
                            locomotion_queue.put(locomotion_action, timeout=0.01)
                        except:
                            pass

                except Exception as e:
                    pass  # Silently handle errors

        except Exception as e:
            if not stop_event.is_set():
                print(f"[LOCOMOTION] Error: {e}")

    print("[LOCOMOTION] Thread stopped")


def action_predictor_thread(models, sensor_queue, action_queue, stop_event):
    """Thread 2b: Multiclass classifier for actions (jump/punch/turn) with 1.5s windows."""
    print("[ACTION] Thread started (1.5s windows)")

    # Smaller buffer for quick actions
    sensor_buffer = deque(maxlen=MULTI_WINDOW_SAMPLES)
    prediction_count = 0

    while not stop_event.is_set():
        try:
            # Collect data
            try:
                sensor_reading = sensor_queue.get(timeout=0.01)
                sensor_buffer.append(sensor_reading)
            except Empty:
                pass

            # Predict more frequently for actions (every ~5 iterations)
            prediction_count += 1
            if prediction_count < 5:
                continue
            prediction_count = 0

            # Run prediction if buffer is sufficiently full
            if len(sensor_buffer) >= int(MULTI_WINDOW_SAMPLES * 0.7):  # 70% full
                try:
                    buffer_df = pd.DataFrame(list(sensor_buffer))
                    features = extract_window_features(buffer_df)

                    # Create feature vector
                    feature_vector = pd.DataFrame([features])
                    feature_vector = feature_vector.reindex(
                        columns=models['multi_feature_names'], fill_value=0
                    )

                    # Scale and predict
                    features_scaled = models['multi_scaler'].transform(feature_vector)
                    prediction = models['multi_classifier'].predict(features_scaled)[0]
                    probabilities = models['multi_classifier'].predict_proba(features_scaled)[0]
                    confidence = probabilities[prediction]

                    # Map prediction to gesture name
                    gesture = MULTI_GESTURES[prediction]

                    # Push to action queue
                    if confidence >= ML_CONFIDENCE_THRESHOLD:
                        action_result = {
                            "gesture": gesture,
                            "confidence": confidence,
                            "timestamp": time.time()
                        }
                        try:
                            action_queue.put(action_result, timeout=0.01)
                        except:
                            pass

                except Exception as e:
                    pass

        except Exception as e:
            if not stop_event.is_set():
                print(f"[ACTION] Error: {e}")

    print("[ACTION] Thread stopped")


def actor_thread(locomotion_queue, action_queue, stop_event):
    """Thread 3: Execute keyboard actions based on parallel predictions.

    Locomotion (walk/idle) controls arrow keys (hold/release).
    Actions (jump/punch/turn) are momentary key presses.
    Both run independently!
    """
    print("[ACTOR] Thread started")

    global is_walking, facing_direction

    # State management
    locomotion_history = deque(maxlen=CONFIDENCE_GATING_COUNT)
    action_history = deque(maxlen=CONFIDENCE_GATING_COUNT)

    # Current locomotion state
    current_locomotion = "idle"

    # Debouncing for actions
    last_action_time = {"jump": 0, "punch": 0, "turn": 0}
    ACTION_COOLDOWN = 0.5  # Seconds between same action

    while not stop_event.is_set():
        try:
            # === PROCESS LOCOMOTION ===
            try:
                loco_action = locomotion_queue.get_nowait()
                locomotion_history.append(loco_action["gesture"])

                # Check for consensus
                if len(locomotion_history) == CONFIDENCE_GATING_COUNT:
                    if len(set(locomotion_history)) == 1:  # All agree
                        predicted_loco = locomotion_history[0]

                        # State change needed?
                        if predicted_loco != current_locomotion:
                            current_locomotion = predicted_loco

                            if predicted_loco == "walk":
                                # Start walking
                                if not is_walking:
                                    is_walking = True
                                    walk_key = KEY_MAP["right"] if facing_direction == "right" else KEY_MAP["left"]
                                    keyboard.press(walk_key)
                                    print(f"\n🚶 [LOCOMOTION] WALKING {facing_direction.upper()} ({loco_action['confidence']:.2f})")
                            else:  # idle
                                # Stop walking
                                if is_walking:
                                    is_walking = False
                                    walk_key = KEY_MAP["right"] if facing_direction == "right" else KEY_MAP["left"]
                                    keyboard.release(walk_key)
                                    print(f"\n⏸️  [LOCOMOTION] IDLE ({loco_action['confidence']:.2f})")
            except Empty:
                pass

            # === PROCESS ACTIONS ===
            try:
                action_result = action_queue.get_nowait()
                action_gesture = action_result["gesture"]
                action_history.append(action_gesture)

                # Check for consensus
                if len(action_history) == CONFIDENCE_GATING_COUNT:
                    if len(set(action_history)) == 1:  # All agree
                        predicted_action = action_history[0]
                        current_time = time.time()

                        # Check cooldown
                        action_type = "turn" if "turn" in predicted_action else predicted_action
                        if current_time - last_action_time[action_type] < ACTION_COOLDOWN:
                            continue  # Still on cooldown

                        last_action_time[action_type] = current_time

                        # Execute action
                        if predicted_action == "jump":
                            print(f"\n⬆️  [ACTION] JUMP ({action_result['confidence']:.2f})")
                            keyboard.press(KEY_MAP["jump"])
                            time.sleep(0.05)
                            keyboard.release(KEY_MAP["jump"])

                        elif predicted_action == "punch":
                            print(f"\n👊 [ACTION] PUNCH ({action_result['confidence']:.2f})")
                            keyboard.press(KEY_MAP["attack"])
                            time.sleep(0.05)
                            keyboard.release(KEY_MAP["attack"])

                        elif predicted_action == "turn_left":
                            print(f"\n↪️  [ACTION] TURN LEFT ({action_result['confidence']:.2f})")
                            facing_direction = "left"
                            # Update walking key if currently walking
                            if is_walking:
                                keyboard.release(KEY_MAP["right"])
                                keyboard.press(KEY_MAP["left"])

                        elif predicted_action == "turn_right":
                            print(f"\n↩️  [ACTION] TURN RIGHT ({action_result['confidence']:.2f})")
                            facing_direction = "right"
                            # Update walking key if currently walking
                            if is_walking:
                                keyboard.release(KEY_MAP["left"])
                                keyboard.press(KEY_MAP["right"])

                        # Clear history after executing
                        action_history.clear()

            except Empty:
                pass

            # Small sleep to prevent busy-waiting
            time.sleep(0.01)

        except Exception as e:
            if not stop_event.is_set():
                print(f"[ACTOR] Error: {e}")

    # Cleanup: release any held keys
    if is_walking:
        keyboard.release(KEY_MAP["left"])
        keyboard.release(KEY_MAP["right"])

    print("[ACTOR] Thread stopped")


# --- Main Listener Logic ---
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((LISTEN_IP, LISTEN_PORT))

# --- Network Service Discovery Setup ---
print("🔗 Registering service for automatic discovery...")
zeroconf = Zeroconf()
service_type = "_silksong._udp.local."
service_name = f"SilksongController.{service_type}"

ip_bytes = socket.inet_aton(LISTEN_IP)
service_info = ServiceInfo(
    service_type,
    service_name,
    addresses=[ip_bytes],
    port=LISTEN_PORT,
    properties={"version": "2.0-parallel"},
)

zeroconf.register_service(service_info)
print(f"✓ Service registered as '{service_name}'")

print(f"\n{'='*60}")
print(f"🎮 Silksong Controller v2.0 - PARALLEL CLASSIFIERS")
print(f"{'='*60}")
print(f"Listening on {LISTEN_IP}:{LISTEN_PORT}")

if ML_ENABLED:
    print(f"\n✅ PARALLEL ML ARCHITECTURE ACTIVE")
    print(f"   📊 Binary Classifier: Walk vs Idle ({BINARY_WINDOW_SEC}s windows)")
    print(f"   🎯 Multiclass Classifier: Jump/Punch/Turn ({MULTI_WINDOW_SEC}s windows)")
    print(f"   🔄 Both run simultaneously for parallel detection!")
    print(f"\n   Confidence Threshold: {ML_CONFIDENCE_THRESHOLD:.0%}")
    print(f"   Confidence Gating: {CONFIDENCE_GATING_COUNT} consecutive predictions")

    print(f"\n🎮 Key Mappings:")
    print(f"   Movement: {config['keyboard_mappings']['left']}/{config['keyboard_mappings']['right']}")
    print(f"   Jump: {config['keyboard_mappings']['jump']} | Attack: {config['keyboard_mappings']['attack']}")
    print(f"{'='*60}\n")

    # ========================================================================
    # MAIN: Start Parallel Multi-Threaded Architecture
    # ========================================================================

    stop_event = threading.Event()

    # Start the FOUR threads (Collector + 2 Predictors + Actor)
    collector = threading.Thread(
        target=collector_thread,
        args=(sock, sensor_queue, stop_event),
        name="Collector"
    )

    locomotion_predictor = threading.Thread(
        target=locomotion_predictor_thread,
        args=(parallel_models, sensor_queue, locomotion_queue, stop_event),
        name="LocomotionPredictor"
    )

    action_predictor = threading.Thread(
        target=action_predictor_thread,
        args=(parallel_models, sensor_queue, action_queue, stop_event),
        name="ActionPredictor"
    )

    actor = threading.Thread(
        target=actor_thread,
        args=(locomotion_queue, action_queue, stop_event),
        name="Actor"
    )

    # Start all threads
    collector.start()
    locomotion_predictor.start()
    action_predictor.start()
    actor.start()

    print("✅ All threads started successfully:")
    print("   1️⃣  Collector: UDP → Queue")
    print("   2️⃣  Locomotion Predictor: Queue → Binary ML → Locomotion Actions")
    print("   3️⃣  Action Predictor: Queue → Multiclass ML → Action Gestures")
    print("   4️⃣  Actor: Both Queues → Keyboard Control")
    print(f"\n{'='*60}")
    print("🎮 Ready to play! Wave your watch to control the game.")
    print("   Press Ctrl+C to stop...")
    print(f"{'='*60}\n")

    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        stop_event.set()

        # Wait for threads to finish
        print("   Stopping collector...")
        collector.join(timeout=2)
        print("   Stopping locomotion predictor...")
        locomotion_predictor.join(timeout=2)
        print("   Stopping action predictor...")
        action_predictor.join(timeout=2)
        print("   Stopping actor...")
        actor.join(timeout=2)

    finally:
        print("🔗 Unregistering service...")
        zeroconf.unregister_service(service_info)
        zeroconf.close()
        sock.close()
        print("✅ Controller stopped.\n")

else:
    print("\n❌ ML models not available!")
    print("   Please train models first:")
    print("   1. Run: python src/organize_training_data.py")
    print("   2. Run: jupyter notebook notebooks/SVM_Local_Training.ipynb")
    print("   3. Or run: python notebooks/SVM_Local_Training.py\n")
    zeroconf.unregister_service(service_info)
    zeroconf.close()
    sock.close()
