#!/usr/bin/env python3
"""
Phase VI: SVM Controller with Two-Stage Classification

Architecture:
1. Stage 1 (Binary): Walking vs Not-Walking
2. Stage 2 (Multi-class): Jump/Punch/Turn_Left/Turn_Right/Idle

This controller expects trained models in:
- models/binary_classifier.pkl (SVM for walking detection)
- models/multiclass_classifier.pkl (SVM for action recognition)
- models/binary_scaler.pkl (StandardScaler for Stage 1)
- models/multiclass_scaler.pkl (StandardScaler for Stage 2)
- models/feature_names.pkl (Feature list for validation)

Data organization:
- Train binary model on: data/organized_training/binary_classification/
- Train multiclass model on: data/organized_training/multiclass_classification/

Usage:
    python phase_vi_svm_controller.py
"""

import socket
import json
import time
import threading
from collections import deque
from queue import Queue
from pynput.keyboard import Controller
import joblib
import numpy as np
from scipy import stats
from scipy.fft import fft
import sys
import os
from pathlib import Path

# Add shared_utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared_utils'))
import network_utils

# --- Configuration ---
UDP_PORT = 12345
WINDOW_SIZE_SEC = 0.3  # 300ms windows for prediction
SAMPLE_RATE = 50  # Hz
WINDOW_SIZE_SAMPLES = int(WINDOW_SIZE_SEC * SAMPLE_RATE)
CONFIDENCE_THRESHOLD = 5  # Require 5 consecutive matching predictions

# Model paths (relative to project root)
PROJECT_ROOT = Path(__file__).parent.parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
BINARY_MODEL_PATH = MODELS_DIR / "binary_classifier.pkl"
MULTICLASS_MODEL_PATH = MODELS_DIR / "multiclass_classifier.pkl"
BINARY_SCALER_PATH = MODELS_DIR / "binary_scaler.pkl"
MULTICLASS_SCALER_PATH = MODELS_DIR / "multiclass_scaler.pkl"
FEATURE_NAMES_PATH = MODELS_DIR / "feature_names.pkl"

# --- Global State ---
keyboard = Controller()
sensor_buffer = deque(maxlen=int(2 * SAMPLE_RATE))  # 2-second buffer
prediction_history = deque(maxlen=CONFIDENCE_THRESHOLD)
current_action = "idle"
is_walking = False

# ML Models (loaded at startup)
binary_classifier = None
multiclass_classifier = None
binary_scaler = None
multiclass_scaler = None
feature_names = None

# Thread control
running = True


def load_models():
    """Load trained SVM models and scalers"""
    global binary_classifier, multiclass_classifier
    global binary_scaler, multiclass_scaler, feature_names

    print("\n🤖 Loading ML Models...")

    try:
        if BINARY_MODEL_PATH.exists():
            binary_classifier = joblib.load(BINARY_MODEL_PATH)
            print(f"  ✅ Binary classifier loaded from {BINARY_MODEL_PATH}")
        else:
            print(f"  ⚠️  Binary classifier not found: {BINARY_MODEL_PATH}")
            print(f"      Train it using: notebooks/SVM_Local_Training.ipynb")

        if MULTICLASS_MODEL_PATH.exists():
            multiclass_classifier = joblib.load(MULTICLASS_MODEL_PATH)
            print(f"  ✅ Multi-class classifier loaded from {MULTICLASS_MODEL_PATH}")
        else:
            print(f"  ⚠️  Multi-class classifier not found: {MULTICLASS_MODEL_PATH}")
            print(f"      Train it using: notebooks/SVM_Local_Training.ipynb")

        if BINARY_SCALER_PATH.exists():
            binary_scaler = joblib.load(BINARY_SCALER_PATH)
            print(f"  ✅ Binary scaler loaded")

        if MULTICLASS_SCALER_PATH.exists():
            multiclass_scaler = joblib.load(MULTICLASS_SCALER_PATH)
            print(f"  ✅ Multi-class scaler loaded")

        if FEATURE_NAMES_PATH.exists():
            feature_names = joblib.load(FEATURE_NAMES_PATH)
            print(f"  ✅ Feature names loaded ({len(feature_names)} features)")

        # Check if we have enough to run
        models_ready = (binary_classifier is not None and
                       multiclass_classifier is not None and
                       binary_scaler is not None and
                       multiclass_scaler is not None)

        if models_ready:
            print("\n✨ All models loaded successfully!")
            return True
        else:
            print("\n⚠️  Some models are missing. Controller will run in demo mode.")
            print("   Train models using: notebooks/SVM_Local_Training.ipynb")
            return False

    except Exception as e:
        print(f"  ❌ Error loading models: {e}")
        return False


def extract_features(window_data):
    """
    Extract time-domain and frequency-domain features from sensor window.

    Features per axis (accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z):
    - mean, std, min, max, range
    - median, skewness, kurtosis
    - FFT dominant frequency, FFT max magnitude

    Total: ~60 features
    """
    features = {}

    # Convert to numpy arrays
    accel_x = np.array([d['accel_x'] for d in window_data])
    accel_y = np.array([d['accel_y'] for d in window_data])
    accel_z = np.array([d['accel_z'] for d in window_data])
    gyro_x = np.array([d['gyro_x'] for d in window_data])
    gyro_y = np.array([d['gyro_y'] for d in window_data])
    gyro_z = np.array([d['gyro_z'] for d in window_data])

    sensors = {
        'accel_x': accel_x, 'accel_y': accel_y, 'accel_z': accel_z,
        'gyro_x': gyro_x, 'gyro_y': gyro_y, 'gyro_z': gyro_z
    }

    for name, data in sensors.items():
        # Time-domain features
        features[f'{name}_mean'] = np.mean(data)
        features[f'{name}_std'] = np.std(data)
        features[f'{name}_min'] = np.min(data)
        features[f'{name}_max'] = np.max(data)
        features[f'{name}_range'] = np.ptp(data)
        features[f'{name}_median'] = np.median(data)
        features[f'{name}_skew'] = stats.skew(data)
        features[f'{name}_kurtosis'] = stats.kurtosis(data)

        # Frequency-domain features (FFT)
        fft_vals = np.abs(fft(data))
        features[f'{name}_fft_max'] = np.max(fft_vals)

        # Dominant frequency
        freqs = np.fft.fftfreq(len(data), 1/SAMPLE_RATE)
        dominant_freq_idx = np.argmax(fft_vals[1:len(fft_vals)//2]) + 1
        features[f'{name}_dominant_freq'] = abs(freqs[dominant_freq_idx])

    # Magnitude features
    accel_mag = np.sqrt(accel_x**2 + accel_y**2 + accel_z**2)
    gyro_mag = np.sqrt(gyro_x**2 + gyro_y**2 + gyro_z**2)

    features['accel_mag_mean'] = np.mean(accel_mag)
    features['accel_mag_std'] = np.std(accel_mag)
    features['gyro_mag_mean'] = np.mean(gyro_mag)
    features['gyro_mag_std'] = np.std(gyro_mag)

    return features


def predict_action(window_data):
    """
    Two-stage classification:
    1. Binary: Walking vs Not-Walking
    2. Multi-class: If not walking, classify action

    Returns: (action, confidence)
    """
    global binary_classifier, multiclass_classifier
    global binary_scaler, multiclass_scaler

    if binary_classifier is None or multiclass_classifier is None:
        return "idle", 0.0

    try:
        # Extract features
        features_dict = extract_features(window_data)

        # Convert to DataFrame for consistent feature ordering
        import pandas as pd
        features_df = pd.DataFrame([features_dict])

        # Ensure feature order matches training
        if feature_names is not None:
            features_df = features_df[feature_names]

        features = features_df.values

        # Stage 1: Binary classification (Walking vs Not-Walking)
        if binary_scaler:
            features_binary = binary_scaler.transform(features)
        else:
            features_binary = features

        binary_pred = binary_classifier.predict(features_binary)[0]
        binary_proba = binary_classifier.predict_proba(features_binary)[0]
        binary_confidence = np.max(binary_proba)

        # If walking, return immediately
        if binary_pred == 1:  # Assuming 1 = walking
            return "walk", binary_confidence

        # Stage 2: Multi-class classification (Action recognition)
        if multiclass_scaler:
            features_multi = multiclass_scaler.transform(features)
        else:
            features_multi = features

        action_pred = multiclass_classifier.predict(features_multi)[0]
        action_proba = multiclass_classifier.predict_proba(features_multi)[0]
        action_confidence = np.max(action_proba)

        return action_pred, action_confidence

    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return "idle", 0.0


def execute_action(action):
    """Execute keyboard action based on prediction"""
    global current_action, is_walking

    if action == current_action:
        return  # Already doing this action

    # Stop previous action
    if current_action == "walk":
        is_walking = False
        # Release arrow keys
        keyboard.release('left')
        keyboard.release('right')

    # Execute new action
    current_action = action

    if action == "walk":
        is_walking = True
        keyboard.press('right')  # Default walk right
        print("🚶 Walking")

    elif action == "jump":
        keyboard.press('z')
        time.sleep(0.05)
        keyboard.release('z')
        print("🦘 Jump")

    elif action == "punch":
        keyboard.press('x')
        time.sleep(0.05)
        keyboard.release('x')
        print("👊 Punch")

    elif action == "turn_left":
        keyboard.press('left')
        time.sleep(0.1)
        keyboard.release('left')
        print("↪️  Turn Left")

    elif action == "turn_right":
        keyboard.press('right')
        time.sleep(0.1)
        keyboard.release('right')
        print("↩️  Turn Right")

    elif action == "idle":
        print("💤 Idle")

    # Reset to idle after discrete actions
    if action in ["jump", "punch", "turn_left", "turn_right"]:
        current_action = "idle"


def predictor_thread(data_queue):
    """Background thread that runs ML predictions"""
    global prediction_history, running

    print("🧠 Predictor thread started")

    while running:
        time.sleep(0.05)  # Check every 50ms

        # Need enough data for a window
        if len(sensor_buffer) < WINDOW_SIZE_SAMPLES:
            continue

        # Get most recent window
        window = list(sensor_buffer)[-WINDOW_SIZE_SAMPLES:]

        # Run prediction
        action, confidence = predict_action(window)

        # Add to history
        prediction_history.append(action)

        # Execute if we have enough confidence (all predictions match)
        if len(prediction_history) == CONFIDENCE_THRESHOLD:
            if len(set(prediction_history)) == 1:  # All match
                execute_action(action)


def collector_thread(data_queue):
    """Background thread that collects UDP sensor data"""
    global sensor_buffer, running

    print(f"📡 Collector thread started on port {UDP_PORT}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', UDP_PORT))
    sock.settimeout(1.0)

    packet_count = 0
    last_print = time.time()

    while running:
        try:
            data, addr = sock.recvfrom(4096)
            message = data.decode('utf-8')

            try:
                msg = json.loads(message)

                # Only process sensor data (not button events)
                if msg.get('sensor'):
                    sensor_entry = {
                        'accel_x': msg.get('accel_x', 0.0),
                        'accel_y': msg.get('accel_y', 0.0),
                        'accel_z': msg.get('accel_z', 0.0),
                        'gyro_x': msg.get('gyro_x', 0.0),
                        'gyro_y': msg.get('gyro_y', 0.0),
                        'gyro_z': msg.get('gyro_z', 0.0),
                        'rot_x': msg.get('rot_x', 0.0),
                        'rot_y': msg.get('rot_y', 0.0),
                        'rot_z': msg.get('rot_z', 0.0),
                        'rot_w': msg.get('rot_w', 1.0),
                        'timestamp': msg.get('timestamp', time.time())
                    }

                    sensor_buffer.append(sensor_entry)
                    packet_count += 1

                    # Status update every 2 seconds
                    if time.time() - last_print > 2.0:
                        print(f"📊 Received {packet_count} packets | Buffer: {len(sensor_buffer)}/{sensor_buffer.maxlen}")
                        last_print = time.time()

            except json.JSONDecodeError:
                pass

        except socket.timeout:
            continue
        except Exception as e:
            print(f"❌ Collector error: {e}")

    sock.close()


def main():
    """Main entry point"""
    global running

    print("="*60)
    print("Phase VI: SVM Controller - Two-Stage Classification")
    print("="*60)

    # Load ML models
    models_loaded = load_models()

    if not models_loaded:
        print("\n⚠️  Running in DEMO MODE (models not fully loaded)")
        print("To train models:")
        print("  1. Organize data: python src/organize_training_data.py")
        print("  2. Train SVM: Open notebooks/SVM_Local_Training.ipynb")
        print()

    # Start threads
    data_queue = Queue()

    collector = threading.Thread(target=collector_thread, args=(data_queue,), daemon=True)
    predictor = threading.Thread(target=predictor_thread, args=(data_queue,), daemon=True)

    collector.start()
    predictor.start()

    print("\n✅ Controller started!")
    print("Press Ctrl+C to stop\n")

    try:
        while running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping controller...")
        running = False
        collector.join(timeout=2.0)
        predictor.join(timeout=2.0)
        print("✅ Controller stopped")


if __name__ == "__main__":
    main()
