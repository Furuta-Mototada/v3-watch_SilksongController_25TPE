# Two-Stage Controller Integration Guide

## Overview

This guide explains how to integrate the two-stage classification system into the existing `udp_listener.py` controller.

## Architecture

### Current Controller (Phase IV)
- Single classifier predicts one of 5 gestures: walk, jump, punch, turn, idle
- Confidence gating with deque history
- Issues: Walking data dominates, actions confused

### New Two-Stage Controller
- **Stage 1 (Binary)**: Walking vs Not-Walking (94% accuracy)
- **Stage 2 (Multi-class)**: Jump, Punch, Turn, Idle (when not walking)
- Benefits: Better accuracy, logical game control, avoids data dominance

## Implementation Steps

### Step 1: Load Both Models

Modify the model loading section in `src/phase_iv_ml_controller/udp_listener.py`:

```python
import joblib
import numpy as np
from pathlib import Path

# Model paths
MODEL_DIR = Path(__file__).parent.parent.parent / "models"

# Load binary classifier (Stage 1)
try:
    binary_classifier = joblib.load(MODEL_DIR / "gesture_classifier_binary.pkl")
    binary_scaler = joblib.load(MODEL_DIR / "feature_scaler_binary.pkl")
    binary_feature_names = joblib.load(MODEL_DIR / "feature_names_binary.pkl")
    print("✅ Binary classifier loaded (Walking vs Not-Walking)")
except Exception as e:
    print(f"❌ Error loading binary classifier: {e}")
    binary_classifier = None

# Load multi-class classifier (Stage 2)
try:
    multiclass_classifier = joblib.load(MODEL_DIR / "gesture_classifier_multiclass.pkl")
    multiclass_scaler = joblib.load(MODEL_DIR / "feature_scaler_multiclass.pkl")
    multiclass_feature_names = joblib.load(MODEL_DIR / "feature_names_multiclass.pkl")
    print("✅ Multi-class classifier loaded (Jump, Punch, Turn, Idle)")
except Exception as e:
    print(f"❌ Error loading multi-class classifier: {e}")
    multiclass_classifier = None

# Gesture mappings
BINARY_GESTURES = ['walking', 'not_walking']
MULTICLASS_GESTURES = ['jump', 'punch', 'turn', 'idle']
```

### Step 2: Create Two-Stage Prediction Function

Add this function to the Predictor thread class:

```python
def predict_two_stage(self, features_dict):
    """
    Two-stage gesture prediction.
    
    Stage 1: Binary classifier (Walking vs Not-Walking)
    Stage 2: Multi-class classifier (Jump, Punch, Turn, Idle)
    
    Args:
        features_dict: Dictionary of extracted features
    
    Returns:
        (gesture, confidence) tuple
    """
    # Convert features to array in correct order
    binary_features = [features_dict.get(fname, 0) for fname in binary_feature_names]
    binary_features = np.array(binary_features).reshape(1, -1)
    
    # Stage 1: Binary classification
    binary_features_scaled = binary_scaler.transform(binary_features)
    binary_prediction = binary_classifier.predict(binary_features_scaled)[0]
    binary_probs = binary_classifier.predict_proba(binary_features_scaled)[0]
    
    if binary_prediction == 0:  # Walking
        gesture = 'walk'
        confidence = binary_probs[0]
    else:  # Not walking - go to Stage 2
        # Stage 2: Multi-class classification
        multi_features = [features_dict.get(fname, 0) for fname in multiclass_feature_names]
        multi_features = np.array(multi_features).reshape(1, -1)
        multi_features_scaled = multiclass_scaler.transform(multi_features)
        
        multi_prediction = multiclass_classifier.predict(multi_features_scaled)[0]
        multi_probs = multiclass_classifier.predict_proba(multi_features_scaled)[0]
        
        # Map to gesture name
        gesture = MULTICLASS_GESTURES[multi_prediction]
        confidence = multi_probs[multi_prediction]
    
    return gesture, confidence
```

### Step 3: Update Prediction Logic

Modify the Predictor thread's run method:

```python
def run(self):
    """Predictor thread - runs ML inference continuously."""
    print(f"🧠 Predictor thread started (PID: {os.getpid()})")
    
    prediction_history = deque(maxlen=5)  # Confidence gating
    
    while self.running:
        try:
            # Get sensor buffer from queue (non-blocking)
            sensor_buffer = self.buffer_queue.get(timeout=0.1)
            
            # Extract features
            features = extract_features_from_buffer(sensor_buffer)
            
            # Two-stage prediction
            gesture, confidence = self.predict_two_stage(features)
            
            # Confidence gating
            if confidence > 0.6:  # Minimum confidence threshold
                prediction_history.append(gesture)
                
                # Require 5 consecutive matching predictions
                if len(prediction_history) == 5 and len(set(prediction_history)) == 1:
                    # Send to Actor thread
                    self.action_queue.put((gesture, confidence))
                    print(f"🎯 Predicted: {gesture} (confidence: {confidence:.2f})")
            
        except queue.Empty:
            continue
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            continue
```

### Step 4: Update Configuration

Add two-stage configuration options to `config.json`:

```json
{
  "two_stage_classification": {
    "enabled": true,
    "binary_confidence_threshold": 0.6,
    "multiclass_confidence_threshold": 0.7,
    "use_separate_thresholds": true
  },
  "confidence_gating": {
    "history_length": 5,
    "require_unanimous": true
  }
}
```

### Step 5: Enhanced Confidence Thresholds

Implement different thresholds for each stage:

```python
def predict_two_stage_with_thresholds(self, features_dict, config):
    """Two-stage prediction with separate confidence thresholds."""
    
    # Stage 1: Binary
    binary_features = [features_dict.get(fname, 0) for fname in binary_feature_names]
    binary_features_scaled = binary_scaler.transform([binary_features])
    binary_prediction = binary_classifier.predict(binary_features_scaled)[0]
    binary_probs = binary_classifier.predict_proba(binary_features_scaled)[0]
    binary_confidence = binary_probs[binary_prediction]
    
    # Check binary confidence threshold
    binary_threshold = config['two_stage_classification']['binary_confidence_threshold']
    if binary_confidence < binary_threshold:
        return None, 0.0  # Not confident enough
    
    if binary_prediction == 0:  # Walking
        return 'walk', binary_confidence
    
    # Stage 2: Multi-class
    multi_features = [features_dict.get(fname, 0) for fname in multiclass_feature_names]
    multi_features_scaled = multiclass_scaler.transform([multi_features])
    multi_prediction = multiclass_classifier.predict(multi_features_scaled)[0]
    multi_probs = multiclass_classifier.predict_proba(multi_features_scaled)[0]
    multi_confidence = multi_probs[multi_prediction]
    
    # Check multi-class confidence threshold
    multi_threshold = config['two_stage_classification']['multiclass_confidence_threshold']
    if multi_confidence < multi_threshold:
        return None, 0.0  # Not confident enough
    
    gesture = MULTICLASS_GESTURES[multi_prediction]
    return gesture, multi_confidence
```

## Testing

### Test Script

Create `src/test_two_stage_classifier.py`:

```python
#!/usr/bin/env python3
"""Test two-stage classifier with sample data."""

import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))
from feature_extractor import extract_features_from_dataframe

# Load models
MODEL_DIR = Path(__file__).parent.parent / "models"
binary_clf = joblib.load(MODEL_DIR / "gesture_classifier_binary.pkl")
multi_clf = joblib.load(MODEL_DIR / "gesture_classifier_multiclass.pkl")
binary_scaler = joblib.load(MODEL_DIR / "feature_scaler_binary.pkl")
multi_scaler = joblib.load(MODEL_DIR / "feature_scaler_multiclass.pkl")
binary_features = joblib.load(MODEL_DIR / "feature_names_binary.pkl")
multi_features = joblib.load(MODEL_DIR / "feature_names_multiclass.pkl")

def test_csv_file(csv_path):
    """Test two-stage prediction on a CSV file."""
    print(f"\n📁 Testing: {csv_path.name}")
    
    # Load data
    df = pd.read_csv(csv_path)
    
    # Extract features
    features_dict = extract_features_from_dataframe(df)
    
    # Stage 1: Binary
    binary_feat = [features_dict.get(f, 0) for f in binary_features]
    binary_scaled = binary_scaler.transform([binary_feat])
    binary_pred = binary_clf.predict(binary_scaled)[0]
    binary_prob = binary_clf.predict_proba(binary_scaled)[0]
    
    print(f"  Stage 1 (Binary): {'Walking' if binary_pred == 0 else 'Not Walking'} ({binary_prob[binary_pred]:.2%})")
    
    if binary_pred == 1:  # Not walking
        # Stage 2: Multi-class
        multi_feat = [features_dict.get(f, 0) for f in multi_features]
        multi_scaled = multi_scaler.transform([multi_feat])
        multi_pred = multi_clf.predict(multi_scaled)[0]
        multi_prob = multi_clf.predict_proba(multi_scaled)[0]
        
        gestures = ['Jump', 'Punch', 'Turn', 'Idle']
        print(f"  Stage 2 (Action): {gestures[multi_pred]} ({multi_prob[multi_pred]:.2%})")
        
        # Show all probabilities
        print(f"  All probabilities:")
        for i, (gesture, prob) in enumerate(zip(gestures, multi_prob)):
            print(f"    {gesture}: {prob:.2%}")

# Test on sample files
data_dir = Path(__file__).parent.parent / "data" / "organized_training"

print("=" * 60)
print("Two-Stage Classifier Test")
print("=" * 60)

# Test binary
print("\n--- Testing Binary Classification ---")
test_csv_file(data_dir / "binary_classification" / "walking" / "walk_1760841422893_to_1760841428419.csv")
test_csv_file(data_dir / "binary_classification" / "not_walking" / "jump_1760841417930_to_1760841419042.csv")

# Test multi-class
print("\n--- Testing Multi-class Classification ---")
for gesture in ['jump', 'punch', 'turn', 'idle']:
    csv_files = list((data_dir / "multiclass_classification" / gesture).glob("*.csv"))
    if csv_files:
        test_csv_file(csv_files[0])

print("\n" + "=" * 60)
```

Run test:
```bash
python src/test_two_stage_classifier.py
```

## Performance Monitoring

Add logging to track two-stage performance:

```python
import logging

# Setup logging
logging.basicConfig(
    filename='two_stage_predictions.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def log_prediction(binary_pred, binary_conf, multi_pred, multi_conf, final_gesture):
    """Log two-stage prediction details."""
    logging.info(f"Binary: {binary_pred} ({binary_conf:.2f}) | "
                f"Multi: {multi_pred} ({multi_conf:.2f}) | "
                f"Final: {final_gesture}")
```

## Fallback Strategy

Handle missing models gracefully:

```python
def predict_with_fallback(self, features_dict):
    """Predict with fallback to single-stage if two-stage fails."""
    
    if binary_classifier and multiclass_classifier:
        # Try two-stage
        try:
            return self.predict_two_stage(features_dict)
        except Exception as e:
            print(f"⚠️  Two-stage failed: {e}, falling back to single-stage")
    
    # Fallback to single-stage (if available)
    if hasattr(self, 'single_classifier'):
        return self.predict_single_stage(features_dict)
    
    return None, 0.0
```

## Expected Improvements

After integration, expect:

1. **Better Walk Detection**: 94% accuracy (vs ~70% before)
2. **Clearer Action Recognition**: No walk confusion in jump/punch/turn
3. **Lower False Positives**: Confidence gating at each stage
4. **Logical Control**: Can't jump while walking (makes sense!)

## Debugging Tips

### Common Issues

**Issue**: Low confidence for all predictions
```python
# Solution: Lower confidence thresholds temporarily
binary_confidence_threshold = 0.4
multiclass_confidence_threshold = 0.5
```

**Issue**: Always predicts "not walking"
```python
# Check binary classifier balance
binary_probs = binary_clf.predict_proba(binary_features_scaled)[0]
print(f"Walking: {binary_probs[0]:.2%}, Not-Walking: {binary_probs[1]:.2%}")
```

**Issue**: Multi-class always predicts same gesture
```python
# Check class balance in training data
# Re-train with data augmentation
python src/data_augmentation.py --input data/organized_training/multiclass_classification
```

## Next Steps

1. ✅ Implement two-stage prediction in controller
2. ✅ Test with real sensor data
3. ✅ Adjust confidence thresholds based on testing
4. ✅ Collect more data if multi-class accuracy is low
5. ✅ Add performance monitoring

## References

- **Training Results**: `docs/TRAINING_RESULTS_SUMMARY.md`
- **Data Organization**: `docs/DATA_ORGANIZATION_GUIDE.md`
- **Feature Extraction**: `src/feature_extractor.py`
- **Current Controller**: `src/phase_iv_ml_controller/udp_listener.py`

---

**Last Updated**: 2025-10-19  
**Binary Accuracy**: 94.29% ✅  
**Multi-class Accuracy**: 57.14% (needs improvement)
