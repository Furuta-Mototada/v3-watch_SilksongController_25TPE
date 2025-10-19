# Simplified Training Data Organization

## Overview

The training data structure has been simplified based on user requirements. The goal is to have a clear, straightforward multi-class classifier without confusing binary stages.

## Changes from Previous Version

### OLD (Confusing):
```
data/organized_training/
├── binary_classification/
│   ├── walking/
│   └── not_walking/  (combined: idle + jump + punch + turn_left + turn_right)
├── multiclass_classification/
│   ├── idle/
│   ├── jump/
│   ├── punch/
│   └── turn/  (combined turn_left and turn_right)
└── noise_detection/
    ├── idle/
    ├── active/  (combined all actions)
    └── baseline/
```

**Problems:**
- Binary classifier "not_walking" inflated one class
- "turn" class combined left/right (important game distinction)
- "active" vs "idle" in noise detection was redundant
- Forced undersampling despite balanced data

### NEW (Simplified):
```
data/organized_training/
├── multiclass/
│   ├── idle/
│   ├── jump/
│   ├── punch/
│   ├── turn_left/
│   ├── turn_right/
│   └── walk/
└── noise/
    └── baseline/
```

**Benefits:**
- Single multi-class classifier with 6 clear gestures
- Separate turn_left and turn_right (important for gameplay)
- No undersampling - uses ALL data (already balanced: 34-40 samples per class)
- Noise detection simplified to baseline only

## Usage

### 1. Organize Your Data

```bash
cd /path/to/project
python src/organize_training_data.py --input data/button_collected --output data/organized_training
```

**Output:**
```
📊 Data Distribution (using ALL data):
  idle: 36 samples
  jump: 40 samples
  punch: 34 samples
  turn_left: 37 samples
  turn_right: 36 samples
  walk: 34 samples
  noise: 61 samples
```

### 2. Train the Model

```bash
python notebooks/SVM_Local_Training.py
```

Or use Jupyter:
```bash
jupyter notebook notebooks/SVM_Local_Training.ipynb
```

**Training Output:**
- Model: `models/gesture_classifier.pkl`
- Scaler: `models/feature_scaler.pkl`
- Features: `models/feature_names.pkl`
- Confusion Matrix: `models/multiclass_confusion_matrix.png`

### 3. Test Results

Example training results:
```
📊 Class distribution:
   idle: 36 samples
   jump: 40 samples
   punch: 34 samples
   turn_left: 37 samples
   turn_right: 36 samples
   walk: 34 samples

✅ Multi-class SVM training complete!
   Training accuracy: 83.82%
   Test accuracy: 77.27%
```

## Parallel Execution Pattern

The controller uses a single multi-class classifier that can detect all 6 gestures:

**Locomotion States** (mutually exclusive):
- `idle`: Standing still
- `walk`: Walking/moving

**Actions** (can execute while walking or idle):
- `jump`: Jump action (z key)
- `punch`: Attack action (x key)

**Direction Changes**:
- `turn_left`: Turn character left
- `turn_right`: Turn character right

**Controller Logic:**
```python
# Single classifier predicts one of 6 gestures
gesture = classifier.predict(features)

# Execute based on prediction
if gesture == 'walk':
    hold_arrow_key()
elif gesture == 'idle':
    release_arrow_keys()
elif gesture == 'jump':
    press_z_key()
elif gesture == 'punch':
    press_x_key()
elif gesture in ['turn_left', 'turn_right']:
    change_direction(gesture)
```

## Key Decisions

1. **No Binary Classifier**: Removed the walking vs not-walking stage
2. **6 Gestures**: All gestures treated equally in one classifier
3. **No Undersampling**: Data is already balanced (34-40 samples each)
4. **Separate Turns**: turn_left and turn_right are distinct classes
5. **Simple Noise Detection**: Only baseline for reference (optional)

## Migration Guide

If you have old organized training data:

1. Delete the old `data/organized_training/` folder
2. Re-run `python src/organize_training_data.py`
3. Re-train with `python notebooks/SVM_Local_Training.py`

The new models will be saved to the standard names:
- `gesture_classifier.pkl` (replaces binary + multiclass)
- `feature_scaler.pkl`
- `feature_names.pkl`
