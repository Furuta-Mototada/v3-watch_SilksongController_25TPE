"""
Feature Extractor for IMU Gesture Recognition

This module provides feature extraction functions used by both:
1. Training pipeline (CS156_Silksong_Watch.ipynb)
2. Real-time controller (udp_listener.py - Phase IV)

The extract_window_features() function computes ~60+ features from
a time window of sensor data for gesture classification.
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.fft import fft


def rotate_vector_by_quaternion(vector, quat):
    """Rotates a 3D vector by a quaternion using standard quaternion rotation formula.
    
    This transforms device-local coordinates to world coordinates, making features
    orientation-invariant.
    
    Parameters:
    -----------
    vector : list or array
        3D vector [x, y, z] to rotate
    quat : dict
        Quaternion with keys 'x', 'y', 'z', 'w'
        
    Returns:
    --------
    list
        Rotated 3D vector [x', y', z']
        
    Example:
    --------
    >>> device_accel = [10, 0, 0]  # Forward in device coords
    >>> quat = {'x': 0, 'y': 0, 'z': 0, 'w': 1}  # No rotation
    >>> world_accel = rotate_vector_by_quaternion(device_accel, quat)
    >>> print(world_accel)  # [10, 0, 0]
    """
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


def extract_window_features(window_df):
    """Extract comprehensive features from a time window of sensor data.
    
    This function extracts time-domain and frequency-domain features from
    IMU sensor data (acceleration, gyroscope, rotation) for gesture recognition.
    
    Parameters:
    -----------
    window_df : pd.DataFrame
        DataFrame containing sensor readings with columns:
        - sensor: Sensor type ('linear_acceleration', 'gyroscope', 'rotation_vector')
        - accel_x/y/z: Linear acceleration (m/s²)
        - gyro_x/y/z: Angular velocity (rad/s)
        - rot_x/y/z/w: Rotation quaternion
        
    Returns:
    --------
    dict
        Dictionary of extracted features (~60+ features):
        - Time-domain: mean, std, min, max, range, median, skew, kurtosis, peaks
        - Frequency-domain: FFT max, dominant frequency
        - Cross-sensor: magnitude features
        
    Notes:
    ------
    - Missing data is handled by filling with 0
    - Feature names match those used in training
    - Designed for 3-second windows at ~50Hz (150 samples)
    
    Example:
    --------
    >>> buffer_df = pd.DataFrame(list(sensor_buffer))
    >>> features = extract_window_features(buffer_df)
    >>> print(len(features))  # ~60+ features
    """
    features = {}
    
    # Separate by sensor type
    accel = window_df[window_df['sensor'] == 'linear_acceleration'].copy()
    gyro = window_df[window_df['sensor'] == 'gyroscope']
    rot = window_df[window_df['sensor'] == 'rotation_vector']
    
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
        for axis in ['accel_x', 'accel_y', 'accel_z']:
            values = accel[axis].dropna()
            
            if len(values) > 0:
                # Time-domain statistics
                features[f'{axis}_mean'] = values.mean()
                features[f'{axis}_std'] = values.std()
                features[f'{axis}_max'] = values.max()
                features[f'{axis}_min'] = values.min()
                features[f'{axis}_range'] = values.max() - values.min()
                features[f'{axis}_median'] = values.median()
                
                # Distribution shape
                features[f'{axis}_skew'] = stats.skew(values)
                features[f'{axis}_kurtosis'] = stats.kurtosis(values)
                
                # Peak detection
                threshold = values.mean() + 2 * values.std()
                features[f'{axis}_peak_count'] = len(values[values > threshold])
                
                # Frequency domain (FFT)
                if len(values) > 2:
                    fft_vals = np.abs(fft(values))[:len(values)//2]
                    if len(fft_vals) > 0:
                        features[f'{axis}_fft_max'] = fft_vals.max()
                        features[f'{axis}_dominant_freq'] = fft_vals.argmax()
                        features[f'{axis}_fft_mean'] = fft_vals.mean()
        
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
        for axis in ['gyro_x', 'gyro_y', 'gyro_z']:
            values = gyro[axis].dropna()
            
            if len(values) > 0:
                # Time-domain statistics
                features[f'{axis}_mean'] = values.mean()
                features[f'{axis}_std'] = values.std()
                features[f'{axis}_max_abs'] = values.abs().max()
                features[f'{axis}_range'] = values.max() - values.min()
                
                # Distribution shape
                features[f'{axis}_skew'] = stats.skew(values)
                features[f'{axis}_kurtosis'] = stats.kurtosis(values)
                
                # RMS (root mean square)
                features[f'{axis}_rms'] = np.sqrt(np.mean(values**2))
                
                # Frequency domain
                if len(values) > 2:
                    fft_vals = np.abs(fft(values))[:len(values)//2]
                    if len(fft_vals) > 0:
                        features[f'{axis}_fft_max'] = fft_vals.max()
    
    # ========== ROTATION FEATURES ==========
    if len(rot) > 0:
        for axis in ['rot_x', 'rot_y', 'rot_z', 'rot_w']:
            values = rot[axis].dropna()
            
            if len(values) > 0:
                features[f'{axis}_mean'] = values.mean()
                features[f'{axis}_std'] = values.std()
                features[f'{axis}_range'] = values.max() - values.min()
    
    # ========== CROSS-SENSOR FEATURES ==========
    # Acceleration magnitude
    if len(accel) > 0:
        accel_mag = np.sqrt(
            accel['accel_x'].fillna(0)**2 + 
            accel['accel_y'].fillna(0)**2 + 
            accel['accel_z'].fillna(0)**2
        )
        features['accel_magnitude_mean'] = accel_mag.mean()
        features['accel_magnitude_max'] = accel_mag.max()
        features['accel_magnitude_std'] = accel_mag.std()
    
    # Gyroscope magnitude
    if len(gyro) > 0:
        gyro_mag = np.sqrt(
            gyro['gyro_x'].fillna(0)**2 + 
            gyro['gyro_y'].fillna(0)**2 + 
            gyro['gyro_z'].fillna(0)**2
        )
        features['gyro_magnitude_mean'] = gyro_mag.mean()
        features['gyro_magnitude_max'] = gyro_mag.max()
        features['gyro_magnitude_std'] = gyro_mag.std()
    
    return features


def prepare_feature_vector(features, feature_names):
    """Convert feature dictionary to properly ordered DataFrame for prediction.
    
    Parameters:
    -----------
    features : dict
        Dictionary of extracted features
    feature_names : list
        List of feature names in the correct order (from training)
        
    Returns:
    --------
    pd.DataFrame
        Single-row DataFrame with features in correct order, filled with 0 for missing
        
    Example:
    --------
    >>> features = extract_window_features(buffer_df)
    >>> feature_names = joblib.load('models/feature_names.pkl')
    >>> X = prepare_feature_vector(features, feature_names)
    >>> X_scaled = scaler.transform(X)
    >>> prediction = model.predict(X_scaled)
    """
    # Create DataFrame from features
    feature_df = pd.DataFrame([features]).fillna(0)
    
    # Reindex to match training feature order
    feature_df = feature_df.reindex(columns=feature_names, fill_value=0)
    
    return feature_df


def main():
    """Example usage of feature extraction."""
    print("Feature Extractor Module")
    print("========================")
    print()
    print("This module provides feature extraction for gesture recognition.")
    print()
    print("Usage in Jupyter Notebook:")
    print("  from src.feature_extractor import extract_window_features")
    print("  features = extract_window_features(sample_data)")
    print()
    print("Usage in Real-time Controller:")
    print("  from src.feature_extractor import extract_window_features, prepare_feature_vector")
    print("  import joblib")
    print()
    print("  # Load models")
    print("  model = joblib.load('models/gesture_classifier.pkl')")
    print("  scaler = joblib.load('models/feature_scaler.pkl')")
    print("  feature_names = joblib.load('models/feature_names.pkl')")
    print()
    print("  # Extract and predict")
    print("  features = extract_window_features(buffer_df)")
    print("  X = prepare_feature_vector(features, feature_names)")
    print("  X_scaled = scaler.transform(X)")
    print("  prediction = model.predict(X_scaled)")
    print("  confidence = model.predict_proba(X_scaled).max()")


if __name__ == "__main__":
    main()
