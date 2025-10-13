# Phase IV Integration Guide

This document provides guidance on integrating the trained ML model into the real-time controller for gesture-based game control.

## Overview

Phase IV transforms `udp_listener.py` from a threshold-based controller to an ML-powered gesture recognition system.

**Key Changes:**
1. Load trained model and scaler at startup
2. Replace threshold logic with ML predictions
3. Implement sliding window buffer for sensor data
4. Extract features and predict gestures in real-time
5. Execute actions based on predictions with confidence thresholding

## Architecture

```
Smartwatch           Network            ML Controller         Game
  Sensors    →    UDP Stream    →    Feature Extract   →   Keyboard
   50Hz                              ↓                       Actions
                                  ML Predict
                                  (Confidence > 0.7)
```

## Implementation Steps

### Step 1: Import Required Modules

Add to the top of `src/udp_listener.py`:

```python
import joblib
import pandas as pd
from collections import deque
from src.feature_extractor import extract_window_features, prepare_feature_vector
```

### Step 2: Load Trained Models

After loading the configuration:

```python
# Load ML models for gesture recognition
print("🤖 Loading trained ML models...")
try:
    model = joblib.load('models/gesture_classifier.pkl')
    scaler = joblib.load('models/feature_scaler.pkl')
    feature_names = joblib.load('models/feature_names.pkl')
    print("✓ ML models loaded successfully")
    ML_ENABLED = True
except FileNotFoundError:
    print("⚠️  ML models not found. Using threshold-based detection.")
    print("   Train models first: jupyter notebook CS156_Silksong_Watch.ipynb")
    ML_ENABLED = False
```

### Step 3: Create Sensor Buffer

Create a buffer to collect sensor data for prediction windows:

```python
# Sensor buffer for ML predictions
# 150 samples ≈ 3 seconds at 50Hz
sensor_buffer = deque(maxlen=150)
MIN_BUFFER_SIZE = 100  # Minimum samples for prediction

# Prediction state
last_prediction = None
last_prediction_time = 0
PREDICTION_COOLDOWN = 0.5  # Seconds between predictions
CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence for action
```

### Step 4: Process Incoming Sensor Data

Modify the main UDP loop to buffer sensor data:

```python
while True:
    data, addr = sock.recvfrom(1024)
    
    try:
        parsed_json = json.loads(data.decode('utf-8'))
        
        if ML_ENABLED:
            # Add to buffer for ML prediction
            sensor_buffer.append(parsed_json)
            
            # Try to make prediction
            current_time = time.time()
            if (len(sensor_buffer) >= MIN_BUFFER_SIZE and 
                current_time - last_prediction_time > PREDICTION_COOLDOWN):
                
                # Predict gesture
                gesture, confidence = predict_gesture(sensor_buffer, model, scaler, feature_names)
                
                if gesture and confidence > CONFIDENCE_THRESHOLD:
                    print(f"🎯 Detected: {gesture} (confidence: {confidence:.2f})")
                    execute_gesture(gesture)
                    last_prediction = gesture
                    last_prediction_time = current_time
                    
                    # Optional: Clear buffer after successful prediction
                    # sensor_buffer.clear()
        else:
            # Fall back to threshold-based detection
            handle_threshold_based_detection(parsed_json)
            
    except Exception as e:
        print(f"Error processing data: {e}")
```

### Step 5: Implement Prediction Function

```python
def predict_gesture(buffer, model, scaler, feature_names):
    """Predict gesture from sensor buffer using trained ML model.
    
    Parameters:
    -----------
    buffer : deque
        Buffer of sensor data dictionaries
    model : sklearn model
        Trained gesture classifier
    scaler : StandardScaler
        Feature scaler from training
    feature_names : list
        List of feature names in correct order
        
    Returns:
    --------
    tuple
        (predicted_gesture, confidence) or (None, 0) if prediction fails
    """
    try:
        # Convert buffer to DataFrame
        buffer_df = pd.DataFrame(list(buffer))
        
        # Extract features
        features = extract_window_features(buffer_df)
        
        # Prepare feature vector
        X = prepare_feature_vector(features, feature_names)
        
        # Scale features
        X_scaled = scaler.transform(X)
        
        # Predict
        prediction = model.predict(X_scaled)[0]
        confidence = model.predict_proba(X_scaled).max()
        
        return prediction, confidence
        
    except Exception as e:
        print(f"⚠️  Prediction error: {e}")
        return None, 0.0


def execute_gesture(gesture):
    """Execute keyboard action for predicted gesture.
    
    Parameters:
    -----------
    gesture : str
        Predicted gesture label
    """
    # Map gestures to actions
    if gesture in ["punch_forward", "punch_upward"]:
        keyboard.press(KEY_MAP["attack"])
        keyboard.release(KEY_MAP["attack"])
        print("  → Attack!")
        
    elif gesture in ["jump_quick", "jump_sustained"]:
        keyboard.press(KEY_MAP["jump"])
        keyboard.release(KEY_MAP["jump"])
        print("  → Jump!")
        
    elif gesture == "turn_left":
        # Set facing direction
        print("  → Turn Left")
        # Implementation depends on movement system
        
    elif gesture == "turn_right":
        # Set facing direction
        print("  → Turn Right")
        # Implementation depends on movement system
        
    elif gesture == "walk_forward":
        # Trigger walking
        print("  → Walk Forward")
        
    elif gesture == "rest":
        # No action for rest gesture
        pass
```

## Tuning Parameters

### Confidence Threshold

Adjust based on desired responsiveness vs. accuracy:

```python
CONFIDENCE_THRESHOLD = 0.7  # Default

# More responsive (may have false positives)
CONFIDENCE_THRESHOLD = 0.5

# More accurate (may miss some gestures)
CONFIDENCE_THRESHOLD = 0.9
```

### Buffer Size

Adjust based on gesture duration and sensor frequency:

```python
# Current: ~3 seconds at 50Hz
sensor_buffer = deque(maxlen=150)

# Shorter window for faster response (2 seconds)
sensor_buffer = deque(maxlen=100)

# Longer window for complex gestures (4 seconds)
sensor_buffer = deque(maxlen=200)
```

### Prediction Cooldown

Prevent rapid-fire predictions:

```python
PREDICTION_COOLDOWN = 0.5  # 500ms between predictions

# More responsive
PREDICTION_COOLDOWN = 0.2  # 200ms

# Less frequent
PREDICTION_COOLDOWN = 1.0  # 1 second
```

## Testing

### 1. Verify Model Loading

```bash
python src/udp_listener.py
```

Expected output:
```
🤖 Loading trained ML models...
✓ ML models loaded successfully
```

### 2. Test with Live Data

1. Start the controller:
   ```bash
   python src/udp_listener.py
   ```

2. Start the Android app on your smartwatch

3. Perform gestures and verify predictions:
   ```
   🎯 Detected: punch_forward (confidence: 0.85)
     → Attack!
   🎯 Detected: jump_quick (confidence: 0.92)
     → Jump!
   ```

### 3. Monitor Performance

Add logging to track prediction latency:

```python
start_time = time.time()
gesture, confidence = predict_gesture(sensor_buffer, model, scaler, feature_names)
latency = time.time() - start_time

print(f"Prediction latency: {latency*1000:.2f}ms")
```

Target: <100ms latency

## Fallback Mode

The implementation should gracefully fall back to threshold-based detection if ML models are not available:

```python
if ML_ENABLED:
    # Use ML predictions
    predict_and_execute()
else:
    # Use original threshold logic
    handle_threshold_based_detection()
```

This allows the controller to function even without trained models.

## Debugging

### Common Issues

**Issue**: Prediction errors or crashes

**Possible Causes**:
- Feature mismatch between training and deployment
- Missing sensor data in buffer
- Incorrect feature extraction

**Solutions**:
- Verify `feature_names.pkl` matches training
- Check buffer has all sensor types
- Test feature extraction with sample data

**Issue**: Low confidence predictions

**Possible Causes**:
- Gesture execution different from training
- Insufficient training data
- Model overfitting

**Solutions**:
- Collect more training data with varied executions
- Review gesture execution technique
- Retrain model with more samples

**Issue**: High latency (>100ms)

**Possible Causes**:
- Large buffer size
- Complex feature extraction
- Slow model prediction

**Solutions**:
- Reduce buffer size
- Optimize feature extraction
- Consider simpler model (fewer features)

## Performance Optimization

### 1. Feature Caching

Cache computed features to avoid recomputation:

```python
feature_cache = {}

def extract_features_cached(buffer_df):
    buffer_hash = hash(tuple(buffer_df.values.flatten()))
    if buffer_hash not in feature_cache:
        feature_cache[buffer_hash] = extract_window_features(buffer_df)
    return feature_cache[buffer_hash]
```

### 2. Sliding Window

Instead of clearing buffer after prediction, use sliding window:

```python
# Don't clear buffer - it automatically slides
# This allows for continuous gesture detection
# sensor_buffer.clear()  # Don't do this
```

### 3. Parallel Processing

For advanced use, process predictions in separate thread:

```python
import threading
import queue

prediction_queue = queue.Queue()

def prediction_worker():
    while True:
        buffer_data = prediction_queue.get()
        gesture, confidence = predict_gesture(buffer_data, model, scaler, feature_names)
        if gesture and confidence > CONFIDENCE_THRESHOLD:
            execute_gesture(gesture)

# Start worker thread
threading.Thread(target=prediction_worker, daemon=True).start()

# In main loop
if len(sensor_buffer) >= MIN_BUFFER_SIZE:
    prediction_queue.put(list(sensor_buffer))
```

## Next Steps

1. **Test thoroughly** with various gestures
2. **Collect more training data** if accuracy is low
3. **Tune hyperparameters** for optimal performance
4. **Document gesture execution** for consistent results
5. **Create demonstration videos** of the system in action

## Resources

- **Feature Extractor**: `src/feature_extractor.py`
- **Training Notebook**: `CS156_Silksong_Watch.ipynb`
- **ML Pipeline Preview**: `docs/Phase_II/ML_PIPELINE_PREVIEW.md`
- **Original Controller**: `src/udp_listener.py`

---

**Good luck with Phase IV integration! 🚀**
