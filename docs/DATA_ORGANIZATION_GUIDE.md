# Data Organization & Training Guide

## Overview

This guide explains how to organize your collected gesture data for training machine learning models with a **two-stage classification architecture**.

## Why Two-Stage Classification?

The Silksong controller uses a two-stage classification approach:

### Stage 1: Binary Classifier (Walking vs Not-Walking)
- **Purpose**: Detect continuous walking motion
- **Classes**: `walking`, `not_walking`
- **Rationale**: Walking is a fundamentally different gesture type (continuous) compared to discrete actions

### Stage 2: Multi-class Classifier (Jump, Punch, Turn, Idle)
- **Purpose**: Recognize discrete action gestures
- **Classes**: `jump`, `punch`, `turn`, `idle`
- **Rationale**: These actions are mutually exclusive and only happen when not walking

### Benefits
1. **Better Accuracy**: Each classifier specializes in its gesture type
2. **Avoids Data Dominance**: Walking data doesn't overwhelm action gesture training
3. **Logical Game Control**: Actions like jump/punch don't make sense while walking
4. **Noise Reduction**: Idle detection filters out non-gestures

---

## Step 1: Collect Data

Use one of the data collection methods:

### Button-Based Collection (Recommended)
```bash
cd src/phase_vi_button_collection
python data_collection_dashboard.py
```

This creates files in `data/button_collected/` with format:
```
gesture_timestamp_to_timestamp.csv
```

### Voice-Labeled Collection (Advanced)
```bash
cd src/phase_v_voice_collection
python continuous_data_collector.py --duration 600 --session game_01
```

Requires post-processing with WhisperX for automatic labeling.

---

## Step 2: Organize Data for Training

Run the organization script:

```bash
cd src
python organize_training_data.py --input ../data/button_collected --output ../data/organized_training --target-samples 35
```

### What This Does:

1. **Analyzes** your data distribution
2. **Balances** classes by undersampling majority classes
3. **Organizes** into three directories:
   - `binary_classification/` - Walking vs Not-Walking
   - `multiclass_classification/` - Jump, Punch, Turn, Idle
   - `noise_detection/` - Idle vs Active (optional)
4. **Creates** `metadata.json` with distribution info

### Example Output:

```
📊 Initial Data Distribution:
  jump: 40 samples
  punch: 34 samples
  turn: 73 samples
  walk: 34 samples
  idle: 36 samples
  
  ⚖️  turn: Undersampled 73 → 35
  
📁 Organizing files...

✅ Data organization complete!

📊 Final Distribution:
  Binary Classification:
    - Walking: 34
    - Not Walking: 139
  Multi-class Classification:
    - jump: 35
    - punch: 34
    - turn: 35
    - idle: 35
```

### Directory Structure:

```
data/organized_training/
├── binary_classification/
│   ├── walking/
│   │   └── walk_*.csv (30-40 samples)
│   └── not_walking/
│       └── (jump + punch + turn + idle samples)
├── multiclass_classification/
│   ├── jump/
│   │   └── jump_*.csv (30-40 samples)
│   ├── punch/
│   │   └── punch_*.csv (30-40 samples)
│   ├── turn/
│   │   └── turn_*.csv (30-40 samples)
│   └── idle/
│       └── idle_*.csv (30-40 samples)
├── noise_detection/
│   ├── idle/
│   │   └── idle_*.csv
│   └── active/
│       └── (all non-idle samples)
└── metadata.json
```

---

## Step 3: Train Models

You have two options:

### Option A: Local Training with SVM (5-15 minutes)

**Best for**: Quick iterations, no GPU needed

```bash
cd notebooks
jupyter notebook SVM_Local_Training.ipynb
```

Or run as Python script:
```bash
python notebooks/SVM_Local_Training.py
```

**Features**:
- ✅ Trains both binary and multi-class models
- ✅ No GPU required (CPU is fine)
- ✅ Fast training (5-15 minutes)
- ✅ Good accuracy (85-95%)
- ✅ Saves models to `models/` directory

**Output Models**:
- `models/gesture_classifier_binary.pkl`
- `models/feature_scaler_binary.pkl`
- `models/feature_names_binary.pkl`
- `models/gesture_classifier_multiclass.pkl`
- `models/feature_scaler_multiclass.pkl`
- `models/feature_names_multiclass.pkl`

### Option B: Google Colab Training with CNN-LSTM (20-40 minutes)

**Best for**: Maximum accuracy, have Colab Pro

1. **Upload organized data to Google Drive**:
   ```
   My Drive/silksong_data/organized_training/
   ```

2. **Open notebook in Colab**:
   - Upload `notebooks/Silksong_Complete_Training_Colab.ipynb` to Colab
   - Enable GPU: Runtime → Change runtime type → GPU

3. **Set training mode**:
   ```python
   TRAINING_MODE = 'MULTICLASS'  # or 'BINARY' or 'NOISE'
   ```

4. **Run all cells**

**Features**:
- ✅ Higher accuracy (92-98%)
- ✅ Automatic feature learning
- ✅ Temporal awareness (LSTM)
- ⚠️ Requires GPU (T4 or better)
- ⚠️ Longer training time

---

## Step 4: Using Models in Controller

### Two-Stage Prediction Logic

```python
# Load both models
binary_classifier = joblib.load('models/gesture_classifier_binary.pkl')
multiclass_classifier = joblib.load('models/gesture_classifier_multiclass.pkl')
binary_scaler = joblib.load('models/feature_scaler_binary.pkl')
multiclass_scaler = joblib.load('models/feature_scaler_multiclass.pkl')

# Extract features from sensor window
features = extract_features(sensor_buffer)

# Stage 1: Check if walking
binary_features = binary_scaler.transform([features])
is_walking = binary_classifier.predict(binary_features)[0]

if is_walking == 0:  # walking
    action = "WALK"
else:  # not_walking
    # Stage 2: Classify action
    multi_features = multiclass_scaler.transform([features])
    action_idx = multiclass_classifier.predict(multi_features)[0]
    action = ['JUMP', 'PUNCH', 'TURN', 'IDLE'][action_idx]

# Execute action
keyboard.press(action_key[action])
```

### Update Your Controller

Modify `src/udp_listener.py` to:
1. Load both binary and multi-class models
2. Implement two-stage prediction logic
3. Use appropriate confidence thresholds for each stage

---

## Data Quality Best Practices

### Balanced Classes
- ✅ Aim for 30-40 samples per gesture
- ✅ Use `--target-samples` to balance automatically
- ⚠️ Warn if classes differ by >30%

### Good Data Collection
- ✅ Perform gestures naturally and consistently
- ✅ Include variations (speed, intensity)
- ✅ Record in realistic conditions
- ⚠️ Avoid artificial/exaggerated movements

### Handling Imbalance

If you have class imbalance:

1. **Undersample majority class** (automatic with `organize_training_data.py`)
2. **Collect more minority class data**
3. **Use class weights** in training:
   ```python
   from sklearn.utils.class_weight import compute_class_weight
   class_weights = compute_class_weight('balanced', classes=np.unique(y), y=y)
   svm = SVC(class_weight='balanced')
   ```
4. **Data augmentation** (add noise, time warping)

---

## Troubleshooting

### "Not enough samples for X gesture"

**Solution**: Collect more data for that gesture or reduce `--target-samples`

```bash
python organize_training_data.py --target-samples 25
```

### "Class imbalance warning"

**Solution**: This is OK if ratio is <1.5x. If higher:
- Collect more minority class samples
- Use class weights in training
- Apply data augmentation

### "Models not found"

**Solution**: Check that training completed and models are in `models/`:
```bash
ls -la models/gesture_classifier_*.pkl
```

### "Low accuracy (<70%)"

**Solutions**:
1. Collect more balanced data
2. Check gesture consistency (watch collection videos)
3. Try different model (SVM → CNN-LSTM or vice versa)
4. Verify CSV format is correct
5. Check feature extraction matches training

---

## CSV File Format

All CSV files must have these columns:

```csv
accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,rot_w,rot_x,rot_y,rot_z,sensor,timestamp
```

**Sensors**:
- `linear_acceleration`: Linear acceleration (no gravity)
- `gyroscope`: Angular velocity
- `rotation_vector`: Orientation quaternion

**Verify format**:
```bash
python organize_training_data.py --verify-only
```

---

## Next Steps

1. ✅ Organize your data with `organize_training_data.py`
2. ✅ Train models locally (SVM) or on Colab (CNN-LSTM)
3. ✅ Test models with `python src/udp_listener.py`
4. ✅ Collect more data if accuracy is low
5. ✅ Iterate and improve!

---

## References

- **Data Collection**: See `DASHBOARD_QUICK_START.md`
- **Training Notebooks**: `notebooks/SVM_Local_Training.ipynb`, `notebooks/Silksong_Complete_Training_Colab.ipynb`
- **Controller**: `src/udp_listener.py`
- **Feature Engineering**: `src/feature_extractor.py`

**Happy Training! 🎮**
