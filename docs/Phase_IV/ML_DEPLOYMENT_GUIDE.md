# Phase IV: ML Model Deployment Guide

## Overview

The Silksong Watch Controller now operates in **ML-Powered Mode**, using a trained Support Vector Machine (SVM) to recognize gestures in real-time. This replaces the previous threshold-based system with an intelligent, adaptive gesture recognition pipeline.

---

## Architecture

### System Flow

```
Smartwatch Sensors → UDP Packets → Sensor Buffer → Feature Extraction →
ML Model Prediction → Confidence Check → Keyboard Action
```

### Key Components

1. **Sensor Buffer** (`deque(maxlen=125)`)
   - Stores ~2.5 seconds of sensor data at 50Hz
   - Continuously updated with new readings
   - Used as sliding window for predictions

2. **Feature Extractor** (`extract_window_features()`)
   - Identical to training pipeline
   - Extracts 60+ time and frequency domain features
   - Processes acceleration, gyroscope, and rotation data

3. **ML Pipeline**
   - Model: SVM with RBF kernel
   - Scaler: StandardScaler (fitted on training data)
   - Confidence threshold: 70% (configurable)

4. **Prediction Engine**
   - Runs every 0.5 seconds
   - Only executes gestures above confidence threshold
   - Handles: jump, punch, turn, walk, noise

---

## Setup Instructions

### 1. Prerequisites

Ensure you have completed Phase III (Model Training):

```bash
# Check for required model files
ls -la models/
# Should contain:
# - gesture_classifier.pkl
# - feature_scaler.pkl
# - feature_names.pkl
```

If models are missing, run the training notebook:
```bash
jupyter notebook CS156_Silksong_Watch.ipynb
# Execute all cells to train and save models
```

### 2. Install Dependencies

The ML mode requires additional Python packages:

```bash
pip install joblib scikit-learn scipy pandas numpy
```

### 3. Start the ML-Powered Controller

```bash
cd src
python udp_listener.py
```

You should see:

```
--- Silksong Controller v2.0 (ML-POWERED) ---
Listening on 192.168.x.x:5005
✓ Machine Learning Model Active
  Confidence Threshold: 70%
  Prediction Interval: 0.5s
Official Hollow Knight/Silksong key mappings:
  ...
---------------------------------------
```

---

## Usage

### Gesture Recognition

The system recognizes 5 gesture classes:

| Gesture | Action | Confidence Display |
|---------|--------|-------------------|
| **jump** | Press Z key | `[ML] JUMP (0.85)` |
| **punch** | Press X key | `[ML] ATTACK (0.92)` |
| **turn** | Flip direction | `[ML] TURN (0.78)` |
| **walk** | Handled by step detector | (legacy system) |
| **noise** | Ignored | (no action) |

### Confidence Values

- **High (>80%)**: Very confident prediction, gesture executed
- **Medium (70-80%)**: Threshold level, gesture executed
- **Low (<70%)**: Prediction ignored, no action taken

### Real-Time Dashboard

```
Facing: RIGHT   | Walk: WALKING | Fuel: [####----] 1.2s |
World Z-A: 8.5 | World XY-A: 12.3 | Yaw: 45.2
```

- **Facing**: Current character direction (LEFT/RIGHT)
- **Walk**: Movement state (IDLE/WALKING)
- **Fuel**: Walk fuel remaining (visual bar + seconds)
- **World Z-A**: Peak vertical acceleration (jump detection)
- **World XY-A**: Peak horizontal acceleration (attack detection)
- **Yaw**: Angular rotation rate (turn detection)

---

## Configuration

### Tuning Confidence Threshold

Edit `src/udp_listener.py`:

```python
ML_CONFIDENCE_THRESHOLD = 0.7  # Default: 70%
```

**Recommendations:**
- **85%+**: Very conservative, fewer false positives
- **70-80%**: Balanced (recommended for gameplay)
- **60-70%**: Aggressive, more responsive but noisier

### Adjusting Prediction Frequency

```python
PREDICTION_INTERVAL = 0.5  # Run prediction every 0.5 seconds
```

**Trade-offs:**
- **Lower (0.3s)**: More responsive, higher CPU usage
- **Higher (0.7s)**: Less responsive, lower CPU usage
- **Recommended**: 0.4-0.6s for real-time gameplay

### Buffer Size

```python
sensor_buffer = deque(maxlen=125)  # ~2.5 seconds at 50Hz
```

Must match training window size. Default is optimal for 2.5-second gesture recordings.

---

## Troubleshooting

### Models Not Loading

**Symptom:**
```
⚠️  ML model files not found
   Running in threshold-based mode (legacy)
```

**Solution:**
1. Run the training notebook: `CS156_Silksong_Watch.ipynb`
2. Ensure models are saved to `models/` directory
3. Check file paths in error message

### Low Prediction Accuracy

**Symptom:** Gestures not being recognized correctly

**Solutions:**
1. **Collect more training data**
   ```bash
   python src/data_collector.py
   ```
   - Collect 40+ samples per gesture
   - Use consistent, exaggerated movements

2. **Retrain with current environment**
   - Models trained in one physical setup may not generalize
   - Retrain in the same room/position you'll use for gameplay

3. **Lower confidence threshold temporarily**
   ```python
   ML_CONFIDENCE_THRESHOLD = 0.6  # For testing
   ```

### Lag or Delayed Responses

**Symptoms:** Actions execute too slowly

**Solutions:**
1. Reduce prediction interval:
   ```python
   PREDICTION_INTERVAL = 0.3  # Faster predictions
   ```

2. Check system resources:
   ```bash
   top  # Monitor CPU usage
   ```

3. Close other applications to free CPU cycles

### Too Many False Positives

**Symptom:** Random gestures being detected

**Solutions:**
1. Increase confidence threshold:
   ```python
   ML_CONFIDENCE_THRESHOLD = 0.8  # More conservative
   ```

2. Collect more "noise" samples during training
   - Record normal hand movements that aren't gestures
   - Label as "noise" class

3. Check for sensor interference or loose watch band

---

## Performance Metrics

### Expected Performance

Based on Phase III evaluation:

- **Accuracy**: 85-95% on test set
- **Latency**: 50-100ms per prediction
- **CPU Usage**: 10-15% on modern hardware
- **Memory**: ~50MB for loaded models

### Monitoring Performance

The controller prints ML predictions with confidence:

```
[ML] JUMP (0.85)
[ML] ATTACK (0.92)
[ML] TURN (0.78)
```

Monitor these messages to gauge system responsiveness.

---

## Fallback Mode

If ML models fail to load, the system automatically falls back to **threshold-based mode**:

- Uses hardcoded acceleration/gyroscope thresholds
- Legacy system from Phases I-II
- Less accurate but still functional
- Useful for debugging or comparison

To force threshold mode, rename/move model files:
```bash
mv models models_backup
```

---

## Integration with Game

### Hollow Knight / Silksong Controls

The ML model predicts gestures that map to game actions:

| ML Prediction | Game Action | Key |
|---------------|-------------|-----|
| jump | Jump | Z |
| punch | Attack | X |
| turn | Change direction | (internal state) |
| walk | Walk (via fuel) | Arrow keys |

### Walking System

Walking uses a **hybrid approach**:
- **Step detector** adds "fuel" to walk buffer
- **ML model** can detect "walk" gestures
- Character walks automatically while fuel remains
- Direction based on `facing_direction` state

---

## Advanced Features

### Dual Detection System

The controller runs **both** ML and threshold systems:

1. **ML System**: Primary gesture recognition
2. **Threshold System**: Backup for critical actions (jumps)

This ensures reliability even if ML predictions are delayed.

### Adaptive Thresholds

Future enhancement: Use ML confidence to dynamically adjust thresholds in real-time.

---

## Next Steps

### Phase V: Optimization

1. **Model Quantization**: Reduce model size for faster inference
2. **Feature Selection**: Identify and remove redundant features
3. **Hardware Acceleration**: Use GPU for predictions
4. **Multi-Model Ensemble**: Combine SVM + Random Forest

### Phase VI: Deployment

1. **Standalone Executable**: Package as .exe or .app
2. **Auto-Update System**: Pull new models from cloud
3. **Cloud Training**: Upload data, train remotely
4. **Mobile App**: Control interface on phone

---

## Support

### Common Issues

**Q: Gestures work in training but not in controller**
A: Ensure the `extract_window_features()` function is identical in both the notebook and `udp_listener.py`. Any mismatch will break predictions.

**Q: Can I use Random Forest instead of SVM?**
A: Yes! Change model loading:
```python
model = joblib.load('models/random_forest_classifier.pkl')
```

**Q: How do I retrain with new data?**
A:
1. Collect new samples: `python src/data_collector.py`
2. Run notebook: `CS156_Silksong_Watch.ipynb`
3. Models auto-save to `models/` directory
4. Restart controller

---

## Credits

- **ML Pipeline**: Designed using SVM with RBF kernel
- **Feature Engineering**: Time and frequency domain analysis
- **Training Framework**: scikit-learn, scipy, pandas
- **Real-time Inference**: 50Hz sensor processing

**End of ML Deployment Guide**
