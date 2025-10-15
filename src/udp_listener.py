import socket
import json
import time
import math
import threading
from collections import deque
from pynput.keyboard import Controller, Key
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
last_step_time = 0
walking_thread = None
stop_walking_event = threading.Event()
# The core state for our character's direction
facing_direction = "right"
# A variable to store the phone's current orientation
last_known_orientation = {"x": 0, "y": 0, "z": 0, "w": 1}

# --- NEW: Walk Fuel System ---
walk_fuel_seconds = 0.0
last_frame_time = time.time()

# --- NEW: Attack debouncing to prevent rapid-fire attacks ---
last_attack_time = 0
ATTACK_COOLDOWN_SEC = 0.3  # Minimum time between attacks


# --- NEW: The core mathematical helper function ---
def rotate_vector_by_quaternion(vector, quat):
    """Rotates a 3D vector by a quaternion using standard quaternion rotation formula."""
    q_vec = [quat["x"], quat["y"], quat["z"]]
    q_scalar = quat["w"]

    # Standard formula for vector rotation by quaternion
    a = [
        2 * (q_vec[1] * vector[2] - q_vec[2] * vector[1]),
        2 * (q_vec[2] * vector[0] - q_vec[0] * vector[2]),
        2 * (q_vec[0] * vector[1] - q_vec[1] * vector[0]),
    ]

    b = [q_scalar * a[0], q_scalar * a[1], q_scalar * a[2]]

    c = [
        q_vec[1] * a[2] - q_vec[2] * a[1],
        q_vec[2] * a[0] - q_vec[0] * a[2],
        q_vec[0] * a[1] - q_vec[1] * a[0],
    ]

    rotated_vector = [
        vector[0] + b[0] + c[0],
        vector[1] + b[1] + c[1],
        vector[2] + b[2] + c[2],
    ]

    return rotated_vector


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
# Reload config to get the updated IP
config = load_config()

# Extract configuration values
LISTEN_IP = config["network"]["listen_ip"]
LISTEN_PORT = config["network"]["listen_port"]
FUEL_ADDED_PER_STEP = config["thresholds"]["fuel_added_per_step_sec"]
MAX_FUEL_CAPACITY = config["thresholds"]["max_fuel_sec"]
PUNCH_THRESHOLD = config["thresholds"]["punch_threshold_xy_accel"]
JUMP_THRESHOLD = config["thresholds"]["jump_threshold_z_accel"]
TURN_THRESHOLD = config["thresholds"]["turn_threshold_degrees"]
# NEW: Hardcoded stability threshold for pitch/roll stability check
STABILITY_THRESHOLD_DEGREES = 50.0
# NEW: Z-axis stability factor for attack detection (prevents attack during jumps)
ATTACK_Z_STABILITY_FACTOR = 0.7  # Z-axis must be < punch_threshold * this factor

# Load key mappings from config
KEY_MAP = {
    "left": get_key(config["keyboard_mappings"]["left"]),
    "right": get_key(config["keyboard_mappings"]["right"]),
    "jump": get_key(config["keyboard_mappings"]["jump"]),
    "attack": get_key(config["keyboard_mappings"]["attack"]),
}

# Load hybrid system configuration
HYBRID_ENABLED = config.get("hybrid_system", {}).get("enabled", False)
REFLEX_JUMP_THRESHOLD = config.get("hybrid_system", {}).get("reflex_layer", {}).get("jump_threshold", 15.0)
REFLEX_ATTACK_THRESHOLD = config.get("hybrid_system", {}).get("reflex_layer", {}).get("attack_threshold", 12.0)
REFLEX_STABILITY_THRESHOLD = config.get("hybrid_system", {}).get("reflex_layer", {}).get("stability_threshold", 5.0)
REFLEX_COOLDOWN = config.get("hybrid_system", {}).get("reflex_layer", {}).get("cooldown_seconds", 0.3)


# --- ML Model Loading ---
def load_ml_models():
    """Load trained ML models for gesture recognition."""
    try:
        model = joblib.load("models/gesture_classifier.pkl")
        scaler = joblib.load("models/feature_scaler.pkl")
        feature_names = joblib.load("models/feature_names.pkl")
        print("✓ ML models loaded successfully")
        return model, scaler, feature_names
    except FileNotFoundError as e:
        print(f"⚠️  ML model files not found: {e}")
        print("   Running in threshold-based mode (legacy)")
        return None, None, None


def extract_window_features(window_df):
    """Extract comprehensive features from a time window of sensor data.

    This is the same function used during training.
    """
    features = {}

    # Separate by sensor type
    accel = window_df[window_df["sensor"] == "linear_acceleration"].copy()
    gyro = window_df[window_df["sensor"] == "gyroscope"]
    rot = window_df[window_df["sensor"] == "rotation_vector"]
    
    # ========== WORLD-COORDINATE TRANSFORMATION ==========
    # Transform acceleration to world coordinates for orientation invariance
    if len(accel) > 0 and len(rot) > 0:
        for idx in accel.index:
            # Find closest rotation reading by timestamp/index
            if idx in rot.index:
                rot_idx = idx
            else:
                # Find nearest rotation reading
                rot_idx = rot.index[np.argmin(np.abs(rot.index - idx))]
            
            if rot_idx in rot.index:
                # Get device-local acceleration
                device_accel = [
                    accel.loc[idx, 'accel_x'],
                    accel.loc[idx, 'accel_y'],
                    accel.loc[idx, 'accel_z']
                ]
                
                # Get rotation quaternion
                quaternion = {
                    'x': rot.loc[rot_idx, 'rot_x'],
                    'y': rot.loc[rot_idx, 'rot_y'],
                    'z': rot.loc[rot_idx, 'rot_z'],
                    'w': rot.loc[rot_idx, 'rot_w']
                }
                
                # Transform to world coordinates
                try:
                    world_accel = rotate_vector_by_quaternion(device_accel, quaternion)
                    accel.loc[idx, 'world_accel_x'] = world_accel[0]
                    accel.loc[idx, 'world_accel_y'] = world_accel[1]
                    accel.loc[idx, 'world_accel_z'] = world_accel[2]
                except (KeyError, IndexError, TypeError):
                    # If transformation fails, leave world coords as NaN
                    pass

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
        
        # World-coordinate acceleration features (orientation-invariant)
        for axis in ['world_accel_x', 'world_accel_y', 'world_accel_z']:
            if axis in accel.columns:
                values = accel[axis].dropna()
                
                if len(values) > 0:
                    # Time-domain statistics
                    features[f'{axis}_mean'] = values.mean()
                    features[f'{axis}_std'] = values.std()
                    features[f'{axis}_max'] = values.max()
                    features[f'{axis}_min'] = values.min()
                    features[f'{axis}_range'] = values.max() - values.min()
                    
                    # Distribution shape
                    features[f'{axis}_skew'] = stats.skew(values)
                    features[f'{axis}_kurtosis'] = stats.kurtosis(values)

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


# --- Hybrid System: Reflex Layer ---
class ExecutionArbitrator:
    """Coordinates action execution between reflex and ML layers."""
    
    def __init__(self, cooldown_seconds=0.3):
        self.last_action_time = {}
        self.cooldown = cooldown_seconds
    
    def can_execute(self, action):
        """Check if action can be executed (cooldown check)."""
        now = time.time()
        last_time = self.last_action_time.get(action, 0)
        return now - last_time >= self.cooldown
    
    def execute(self, action, source='unknown'):
        """Execute action if cooldown has elapsed."""
        if not self.can_execute(action):
            return False
        
        # Execute keyboard action
        if action == 'jump':
            print(f"[{source.upper()}] JUMP")
            keyboard.press(KEY_MAP["jump"])
            time.sleep(0.1)
            keyboard.release(KEY_MAP["jump"])
        elif action == 'attack':
            print(f"[{source.upper()}] ATTACK")
            keyboard.press(KEY_MAP["attack"])
            time.sleep(0.1)
            keyboard.release(KEY_MAP["attack"])
        elif action == 'turn':
            global facing_direction
            print(f"[{source.upper()}] TURN")
            facing_direction = "left" if facing_direction == "right" else "right"
        
        # Update last action time
        self.last_action_time[action] = time.time()
        return True


def detect_reflex_actions(accel_values, rotation_quaternion):
    """Fast threshold-based detection in world coordinates.
    
    Parameters:
    -----------
    accel_values : dict
        Device-local acceleration values {'x': float, 'y': float, 'z': float}
    rotation_quaternion : dict
        Rotation quaternion {'x': float, 'y': float, 'z': float, 'w': float}
        
    Returns:
    --------
    tuple : (action, confidence)
        action: str or None - 'jump', 'attack', or None
        confidence: float - normalized confidence score (0.0 to 2.0+)
    """
    # Transform to world coordinates
    device_accel = [
        accel_values.get('x', 0),
        accel_values.get('y', 0),
        accel_values.get('z', 0)
    ]
    
    try:
        world_accel = rotate_vector_by_quaternion(device_accel, rotation_quaternion)
    except (KeyError, TypeError, ZeroDivisionError):
        # If transformation fails, can't do reflex detection
        return None, 0.0
    
    # Jump: Strong upward motion in world Z-axis
    if world_accel[2] > REFLEX_JUMP_THRESHOLD:
        confidence = world_accel[2] / REFLEX_JUMP_THRESHOLD
        return 'jump', confidence
    
    # Attack: Forward motion with stable base
    forward_mag = math.sqrt(world_accel[0]**2 + world_accel[1]**2)
    if (forward_mag > REFLEX_ATTACK_THRESHOLD and 
        abs(world_accel[2]) < REFLEX_STABILITY_THRESHOLD):
        confidence = forward_mag / REFLEX_ATTACK_THRESHOLD
        return 'attack', confidence
    
    return None, 0.0


# Load ML models
ml_model, ml_scaler, ml_feature_names = load_ml_models()
ML_ENABLED = ml_model is not None

# Create sensor data buffer for ML predictions (~2.5 seconds at 50Hz)
sensor_buffer = deque(maxlen=125)
ML_CONFIDENCE_THRESHOLD = config.get("hybrid_system", {}).get("ml_layer", {}).get("confidence_threshold", 0.7)
last_prediction_time = 0
PREDICTION_INTERVAL = config.get("hybrid_system", {}).get("ml_layer", {}).get("prediction_interval", 0.5)

# Create execution arbitrator for hybrid system
arbitrator = ExecutionArbitrator(cooldown_seconds=REFLEX_COOLDOWN)


# --- Walker Thread ---
def walker_thread_func():
    global is_walking
    is_walking = True

    # Press left or right arrow based on facing direction
    key_to_press = KEY_MAP["right"] if facing_direction == "right" else KEY_MAP["left"]
    keyboard.press(key_to_press)

    stop_walking_event.wait()

    keyboard.release(key_to_press)
    is_walking = False


# --- Helper Functions ---
def quaternion_to_roll(qx, qy, qz, qw):
    """Convert quaternion to roll angle in degrees."""
    # Roll (x-axis rotation)
    sinr_cosp = 2 * (qw * qx + qy * qz)
    cosr_cosp = 1 - 2 * (qx * qx + qy * qy)
    roll = math.atan2(sinr_cosp, cosr_cosp)
    return math.degrees(roll)


def quaternion_to_euler(q):
    """Converts a quaternion dict into yaw, pitch, roll in degrees."""
    x, y, z, w = q["x"], q["y"], q["z"], q["w"]

    # Roll (x-axis rotation)
    sinr_cosp = 2 * (w * x + y * z)
    cosr_cosp = 1 - 2 * (x * x + y * y)
    roll = math.degrees(math.atan2(sinr_cosp, cosr_cosp))

    # Pitch (y-axis rotation)
    sinp = 2 * (w * y - z * x)
    if abs(sinp) >= 1:
        pitch = math.degrees(math.copysign(math.pi / 2, sinp))
    else:
        pitch = math.degrees(math.asin(sinp))

    # Yaw (z-axis rotation) - This is our Azimuth
    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    yaw = math.degrees(math.atan2(siny_cosp, cosy_cosp))

    return yaw, pitch, roll


# --- Main Listener Logic ---
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((LISTEN_IP, LISTEN_PORT))

# --- Network Service Discovery Setup ---
print("🔗 Registering service for automatic discovery...")
zeroconf = Zeroconf()
service_type = "_silksong._udp.local."
service_name = f"SilksongController.{service_type}"

# Convert IP address to bytes for ServiceInfo
ip_bytes = socket.inet_aton(LISTEN_IP)

service_info = ServiceInfo(
    service_type,
    service_name,
    addresses=[ip_bytes],
    port=LISTEN_PORT,
    properties={"version": "1.0"},
)

zeroconf.register_service(service_info)
print(f"✓ Service registered as '{service_name}'")

if HYBRID_ENABLED and ML_ENABLED:
    ml_mode = "HYBRID (Reflex + ML)"
elif ML_ENABLED:
    ml_mode = "ML-POWERED"
else:
    ml_mode = "THRESHOLD-BASED"

print(f"--- Silksong Controller v2.0 ({ml_mode}) ---")
print(f"Listening on {LISTEN_IP}:{LISTEN_PORT}")

if HYBRID_ENABLED:
    print(f"✓ Hybrid System Active")
    print(f"  Reflex Layer: Jump & Attack (<50ms latency)")
    print(f"  ML Layer: Turn & Complex Gestures (~500ms)")
    print(f"  Reflex Cooldown: {REFLEX_COOLDOWN}s")
elif ML_ENABLED:
    print(f"✓ Machine Learning Model Active")
    print(f"  Confidence Threshold: {ML_CONFIDENCE_THRESHOLD:.0%}")
    print(f"  Prediction Interval: {PREDICTION_INTERVAL}s")
print("Official Hollow Knight/Silksong key mappings:")
print(
    f"  Movement: {config['keyboard_mappings']['left']}/{config['keyboard_mappings']['right']} (direction-based)"
)
print(
    f"  Jump: {config['keyboard_mappings']['jump']} | Attack: {config['keyboard_mappings']['attack']}"
)
print("---------------------------------------")

current_roll = 0.0
current_tilt_state = "CENTERED"
# --- NEW: Separate peak accel trackers for tuning ---
peak_z_accel = 0.0
peak_xy_accel = 0.0
peak_yaw_rate = 0.0  # NEW: for tuning the turn
# NEW: A buffer to store recent orientation history for turn detection
# We'll store ~0.5 seconds of data (at 50Hz, that's 25 samples)
# Modified to store full orientation tuples (yaw, pitch, roll)
orientation_history = deque(maxlen=25)

try:
    while True:
        data, addr = sock.recvfrom(2048)

        # --- NEW: Walk Fuel System Logic ---
        current_time = time.time()
        delta_time = current_time - last_frame_time
        last_frame_time = current_time

        # Deplete fuel over time
        walk_fuel_seconds = max(0.0, walk_fuel_seconds - delta_time)

        # Start walking if we have fuel and aren't already walking
        if walk_fuel_seconds > 0 and not is_walking and walking_thread is None:
            stop_walking_event.clear()
            walking_thread = threading.Thread(target=walker_thread_func)
            walking_thread.start()

        # Stop walking if we're out of fuel
        elif walk_fuel_seconds <= 0 and is_walking:
            stop_walking_event.set()
            if walking_thread is not None:
                walking_thread.join()
                walking_thread = None

        try:
            parsed_json = json.loads(data.decode())
            sensor_type = parsed_json.get("sensor")

            # --- REFLEX LAYER: Fast threshold-based detection ---
            if HYBRID_ENABLED and sensor_type == "linear_acceleration":
                accel_values = parsed_json.get("values", {})
                
                # Try reflex detection using world coordinates
                reflex_action, confidence = detect_reflex_actions(
                    accel_values,
                    last_known_orientation
                )
                
                if reflex_action:
                    arbitrator.execute(reflex_action, 'reflex')

            # --- ML PREDICTION LOGIC ---
            if ML_ENABLED:
                # Add sensor reading to buffer
                sensor_reading = {
                    "timestamp": current_time,
                    "sensor": sensor_type,
                    "gesture": "unknown",
                    "stance": "neutral",
                    "sample": 1,
                }

                # Add sensor-specific values
                if sensor_type == "linear_acceleration":
                    vals = parsed_json.get("values", {})
                    sensor_reading.update(
                        {
                            "accel_x": vals.get("x", 0),
                            "accel_y": vals.get("y", 0),
                            "accel_z": vals.get("z", 0),
                        }
                    )
                elif sensor_type == "gyroscope":
                    vals = parsed_json.get("values", {})
                    sensor_reading.update(
                        {
                            "gyro_x": vals.get("x", 0),
                            "gyro_y": vals.get("y", 0),
                            "gyro_z": vals.get("z", 0),
                        }
                    )
                elif sensor_type == "rotation_vector":
                    vals = parsed_json.get("values", {})
                    sensor_reading.update(
                        {
                            "rot_x": vals.get("x", 0),
                            "rot_y": vals.get("y", 0),
                            "rot_z": vals.get("z", 0),
                            "rot_w": vals.get("w", 1),
                        }
                    )

                sensor_buffer.append(sensor_reading)

                # Run prediction if buffer is full and enough time has passed
                if (
                    len(sensor_buffer) >= 100
                    and current_time - last_prediction_time > PREDICTION_INTERVAL
                ):

                    try:
                        # Convert buffer to DataFrame
                        buffer_df = pd.DataFrame(list(sensor_buffer))

                        # Extract features
                        features = extract_window_features(buffer_df)

                        # Create feature vector matching training format
                        feature_vector = pd.DataFrame([features])
                        feature_vector = feature_vector.reindex(
                            columns=ml_feature_names, fill_value=0
                        )

                        # Scale features
                        features_scaled = ml_scaler.transform(feature_vector)

                        # Predict gesture
                        prediction = ml_model.predict(features_scaled)[0]
                        confidence = ml_model.predict_proba(features_scaled).max()

                        # Execute gesture if confidence is high enough
                        if confidence >= ML_CONFIDENCE_THRESHOLD:
                            # In hybrid mode, ML only handles complex gestures (turn)
                            # Jump and attack are handled by reflex layer for speed
                            if HYBRID_ENABLED:
                                # ML layer only handles turn in hybrid mode
                                if prediction == "turn":
                                    arbitrator.execute('turn', 'ml')
                                    print(f"  Confidence: {confidence:.2f}")
                            else:
                                # Legacy mode: ML handles all gestures
                                if prediction == "jump":
                                    print(f"\n[ML] JUMP ({confidence:.2f})")
                                    keyboard.press(KEY_MAP["jump"])
                                    time.sleep(0.1)
                                    keyboard.release(KEY_MAP["jump"])
                                elif prediction == "punch":
                                    print(f"\n[ML] ATTACK ({confidence:.2f})")
                                    keyboard.press(KEY_MAP["attack"])
                                    time.sleep(0.1)
                                    keyboard.release(KEY_MAP["attack"])
                                elif prediction == "turn":
                                    print(f"\n[ML] TURN ({confidence:.2f})")
                                    facing_direction = (
                                        "left" if facing_direction == "right" else "right"
                                    )
                            # walk is handled by step detector
                            # noise is ignored

                        last_prediction_time = current_time

                    except Exception as e:
                        # Silently handle prediction errors
                        pass

            # NEW: Rotation vector now used for turn detection with stability check
            if sensor_type == "rotation_vector":
                vals = parsed_json["values"]

                # Store the orientation for world coordinate transformation
                last_known_orientation.update(vals)

                # Convert quaternion to all three Euler angles
                yaw, pitch, roll = quaternion_to_euler(vals)

                # Add current orientation to our history
                orientation_history.append({"yaw": yaw, "pitch": pitch, "roll": roll})

                # Check for a turn only if our history buffer is full
                if len(orientation_history) == orientation_history.maxlen:
                    oldest_orientation = orientation_history[0]
                    current_orientation = orientation_history[-1]

                    # Calculate change in all three angles
                    yaw_diff = 180 - abs(
                        abs(current_orientation["yaw"] - oldest_orientation["yaw"])
                        - 180
                    )
                    pitch_diff = abs(
                        current_orientation["pitch"] - oldest_orientation["pitch"]
                    )
                    roll_diff = abs(
                        current_orientation["roll"] - oldest_orientation["roll"]
                    )

                    # NEW: The Stability Check
                    is_stable = (pitch_diff < STABILITY_THRESHOLD_DEGREES) and (
                        roll_diff < STABILITY_THRESHOLD_DEGREES
                    )

                    if yaw_diff > TURN_THRESHOLD and is_stable:
                        print("\n--- STABLE TURN DETECTED! ---")
                        if facing_direction == "right":
                            facing_direction = "left"
                        else:
                            facing_direction = "right"
                        print(f"Now facing {facing_direction.upper()}")

                        # --- NEW: Deplete walk fuel for a sharp turn ---
                        walk_fuel_seconds = 0.2
                        # Clear to prevent multiple triggers
                        orientation_history.clear()

            elif sensor_type == "step_detector":
                # --- NEW: Simple fuel addition system ---
                # Add fuel to the tank, capping at maximum capacity
                new_fuel = walk_fuel_seconds + FUEL_ADDED_PER_STEP
                walk_fuel_seconds = min(MAX_FUEL_CAPACITY, new_fuel)
                # Note: Walking start/stop logic is now handled in main loop

            # --- REFACTORED: Acceleration logic now uses world coordinates ---
            elif sensor_type == "linear_acceleration":
                vals = parsed_json["values"]
                accel_vector = [vals["x"], vals["y"], vals["z"]]

                # Perform the transformation to world coordinates
                world_accel = rotate_vector_by_quaternion(
                    accel_vector, last_known_orientation
                )
                world_x, world_y, world_z = (
                    world_accel[0],
                    world_accel[1],
                    world_accel[2],
                )

                # In standard East-North-Up frame, XY plane is horizontal, Z is up
                world_xy_magnitude = math.sqrt(world_x**2 + world_y**2)

                # Update dashboard peaks with world coordinates
                peak_z_accel = max(peak_z_accel, world_z)
                peak_xy_accel = max(peak_xy_accel, world_xy_magnitude)

                # Detection logic uses the new world values
                current_time = time.time()

                if world_z > JUMP_THRESHOLD:
                    print("\n--- JUMP DETECTED! ---")
                    keyboard.press(KEY_MAP["jump"])
                    time.sleep(0.1)
                    keyboard.release(KEY_MAP["jump"])
                    # Reset peaks after an action
                    peak_z_accel, peak_xy_accel = 0.0, 0.0

                # Attack detection with improved conditions to prevent conflicts with jumps
                elif (
                    world_xy_magnitude > PUNCH_THRESHOLD
                    and abs(world_z) < PUNCH_THRESHOLD * ATTACK_Z_STABILITY_FACTOR
                    and current_time - last_attack_time > ATTACK_COOLDOWN_SEC
                ):
                    print(
                        f"\n--- ATTACK DETECTED! --- (XY: {world_xy_magnitude:.1f}, Z: {world_z:.1f})"
                    )
                    keyboard.press(KEY_MAP["attack"])
                    time.sleep(0.1)
                    keyboard.release(KEY_MAP["attack"])
                    # Update last attack time for debouncing
                    last_attack_time = current_time
                    # Reset peaks after an action
                    peak_z_accel, peak_xy_accel = 0.0, 0.0

            # OLD: Gyroscope-based turn detection (replaced with rotation_vector)
            # elif sensor_type == 'gyroscope':
            #     vals = parsed_json['values']
            #     yaw_rate = vals['z']
            #     # Track peak for tuning
            #     peak_yaw_rate = max(peak_yaw_rate, abs(yaw_rate))
            #
            #     if abs(yaw_rate) > TURN_THRESHOLD:
            #         # Flip the direction
            #         if facing_direction == 'right':
            #             facing_direction = 'left'
            #         else:
            #             facing_direction = 'right'
            #         print(f"\n--- TURN DETECTED! Now facing "
            #               f"{facing_direction.upper()} ---")
            #         # Add a small cooldown to prevent multiple flips
            #         time.sleep(0.5)
            #         peak_yaw_rate = 0.0  # Reset after action

            walk_status = "WALKING" if is_walking else "IDLE"

            # Create walk fuel bar visualization
            fuel_percentage = walk_fuel_seconds / MAX_FUEL_CAPACITY
            fuel_bar_length = 8
            filled_bars = int(fuel_percentage * fuel_bar_length)
            empty_bars = fuel_bar_length - filled_bars
            fuel_bar = "[" + "#" * filled_bars + "-" * empty_bars + "]"

            # Updated dashboard to show world coordinates and walk fuel
            dashboard_string = (
                f"\rFacing: {facing_direction.upper().ljust(7)} | "
                f"Walk: {walk_status.ljust(7)} | "
                f"Fuel: {fuel_bar} {walk_fuel_seconds:.1f}s | "
                f"World Z-A:{peak_z_accel:4.1f} | "
                f"World XY-A:{peak_xy_accel:4.1f} | "
                f"Yaw:{peak_yaw_rate:3.1f}"
            )
            print(dashboard_string, end="")

        except (json.JSONDecodeError, KeyError):
            # Temporarily print errors to see if we have issues
            # print(f"Error processing packet: {e}")
            pass

except KeyboardInterrupt:
    print("\nController stopped.")
finally:
    if is_walking and walking_thread is not None:
        stop_walking_event.set()
        walking_thread.join()
    print("🔗 Unregistering service...")
    zeroconf.unregister_service(service_info)
    zeroconf.close()
    sock.close()
