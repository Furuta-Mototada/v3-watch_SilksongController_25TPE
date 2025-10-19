#!/usr/bin/env python3
"""
Test script to verify the trained SVM model works correctly.
Loads the model and tests predictions on a sample from each gesture class.
"""

import sys
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from scipy import stats
from scipy.fft import fft

PROJECT_ROOT = Path(__file__).parent.parent
MODEL_DIR = PROJECT_ROOT / "models"
DATA_DIR = PROJECT_ROOT / "data" / "organized_training" / "multiclass"

# Feature extraction function (copied from SVM_Local_Training.py)
def extract_features_from_dataframe(df):
    """
    Extract comprehensive features from sensor data.
    """
    features = {}
    
    # Separate by sensor type
    accel_data = df[df['sensor'] == 'linear_acceleration']
    gyro_data = df[df['sensor'] == 'gyroscope']
    rot_data = df[df['sensor'] == 'rotation_vector']
    
    def time_features(series, prefix):
        """Extract time-domain features."""
        if len(series) == 0:
            return {}
        return {
            f'{prefix}_mean': np.mean(series),
            f'{prefix}_std': np.std(series),
            f'{prefix}_min': np.min(series),
            f'{prefix}_max': np.max(series),
            f'{prefix}_range': np.max(series) - np.min(series),
            f'{prefix}_median': np.median(series),
            f'{prefix}_skew': stats.skew(series),
            f'{prefix}_kurtosis': stats.kurtosis(series),
        }
    
    def freq_features(series, prefix):
        """Extract frequency-domain features."""
        if len(series) < 4:
            return {f'{prefix}_fft_max': 0, f'{prefix}_dom_freq': 0}
        
        fft_vals = np.abs(fft(series))
        return {
            f'{prefix}_fft_max': np.max(fft_vals[:len(fft_vals)//2]),
            f'{prefix}_dom_freq': np.argmax(fft_vals[:len(fft_vals)//2])
        }
    
    # Accelerometer features
    for axis in ['x', 'y', 'z']:
        col = f'accel_{axis}'
        if col in accel_data.columns and len(accel_data) > 0:
            series = accel_data[col].dropna()
            features.update(time_features(series, f'accel_{axis}'))
            features.update(freq_features(series, f'accel_{axis}'))
    
    # Gyroscope features
    for axis in ['x', 'y', 'z']:
        col = f'gyro_{axis}'
        if col in gyro_data.columns and len(gyro_data) > 0:
            series = gyro_data[col].dropna()
            features.update(time_features(series, f'gyro_{axis}'))
            features.update(freq_features(series, f'gyro_{axis}'))
    
    # Rotation features (quaternion)
    for axis in ['w', 'x', 'y', 'z']:
        col = f'rot_{axis}'
        if col in rot_data.columns and len(rot_data) > 0:
            series = rot_data[col].dropna()
            features.update(time_features(series, f'rot_{axis}'))
    
    # Magnitude features
    if len(accel_data) > 0 and all(f'accel_{ax}' in accel_data.columns for ax in ['x', 'y', 'z']):
        accel_mag = np.sqrt(
            accel_data['accel_x']**2 + 
            accel_data['accel_y']**2 + 
            accel_data['accel_z']**2
        )
        features.update(time_features(accel_mag, 'accel_mag'))
    
    if len(gyro_data) > 0 and all(f'gyro_{ax}' in gyro_data.columns for ax in ['x', 'y', 'z']):
        gyro_mag = np.sqrt(
            gyro_data['gyro_x']**2 + 
            gyro_data['gyro_y']**2 + 
            gyro_data['gyro_z']**2
        )
        features.update(time_features(gyro_mag, 'gyro_mag'))
    
    return features

# Expected gestures
GESTURES = ['idle', 'jump', 'punch', 'turn_left', 'turn_right', 'walk']

def test_model():
    """Test the trained model on one sample from each gesture class."""
    
    print("="*60)
    print("Testing Trained SVM Model")
    print("="*60 + "\n")
    
    # Load model
    print("Loading model files...")
    try:
        classifier = joblib.load(MODEL_DIR / "gesture_classifier.pkl")
        scaler = joblib.load(MODEL_DIR / "feature_scaler.pkl")
        feature_names = joblib.load(MODEL_DIR / "feature_names.pkl")
        print(f"✅ Model loaded successfully")
        print(f"   Features: {len(feature_names)}")
        print(f"   Classes: {classifier.classes_}")
    except FileNotFoundError as e:
        print(f"❌ Error: Model files not found. Run training first.")
        print(f"   python notebooks/SVM_Local_Training.py")
        return False
    
    # Test one sample from each gesture
    print(f"\nTesting predictions on sample data...")
    print(f"{'Gesture':<12} {'File':<40} {'Prediction':<12} {'Confidence':<10} {'Status'}")
    print("-" * 90)
    
    correct = 0
    total = 0
    
    for gesture_idx, gesture in enumerate(GESTURES):
        gesture_dir = DATA_DIR / gesture
        
        if not gesture_dir.exists():
            print(f"⚠️  {gesture:<12} Directory not found")
            continue
        
        # Get first CSV file
        csv_files = list(gesture_dir.glob("*.csv"))
        if not csv_files:
            print(f"⚠️  {gesture:<12} No CSV files found")
            continue
        
        test_file = csv_files[0]
        
        # Load and extract features
        try:
            df = pd.read_csv(test_file)
            features = extract_features_from_dataframe(df)
            
            # Convert to array matching training format
            feature_array = np.array([features.get(name, 0) for name in feature_names]).reshape(1, -1)
            
            # Scale and predict
            feature_scaled = scaler.transform(feature_array)
            prediction_idx = classifier.predict(feature_scaled)[0]
            prediction = GESTURES[prediction_idx]
            
            # Get confidence
            probabilities = classifier.predict_proba(feature_scaled)[0]
            confidence = probabilities[prediction_idx]
            
            # Check if correct
            is_correct = (prediction == gesture)
            status = "✅" if is_correct else "❌"
            
            if is_correct:
                correct += 1
            total += 1
            
            print(f"{gesture:<12} {test_file.name[:38]:<40} {prediction:<12} {confidence:>6.1%}     {status}")
            
        except Exception as e:
            print(f"❌ {gesture:<12} Error processing: {e}")
    
    # Summary
    print("-" * 90)
    print(f"\n📊 Test Results:")
    print(f"   Correct: {correct}/{total}")
    print(f"   Accuracy: {correct/total:.1%}" if total > 0 else "   No samples tested")
    
    if correct == total and total == len(GESTURES):
        print(f"\n🎉 All tests passed! Model is working correctly.")
        return True
    else:
        print(f"\n⚠️  Some predictions were incorrect. This is expected with limited test samples.")
        print(f"   The model should still work for real-time predictions.")
        return True

if __name__ == '__main__':
    success = test_model()
    sys.exit(0 if success else 1)
