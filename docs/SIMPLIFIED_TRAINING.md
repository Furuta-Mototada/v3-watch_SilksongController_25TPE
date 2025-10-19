# Simplified Training Data Organization

## Overview

The training data is organized for a **parallel two-classifier architecture** that enables simultaneous detection of locomotion and actions.

## Architecture

### Two Parallel Classifiers:

1. **Binary Classifier**: Walk vs Idle (locomotion states)
   - Sample duration: ~5 seconds
   - Purpose: Determine movement state
   - Classes: `walk`, `idle`

2. **Multi-class Classifier**: Jump, Punch, Turn_Left, Turn_Right (actions)
   - Sample duration: ~1-2 seconds
   - Purpose: Detect quick actions
   - Classes: `jump`, `punch`, `turn_left`, `turn_right`

These run **IN PARALLEL** to enable simultaneous detection like:
- walk + jump
- walk + punch
- idle + turn_left
- walk + turn_right

## Data Structure

```
data/organized_training/
├── binary_classification/
│   ├── walk/      (locomotion - 5s samples)
│   └── idle/      (locomotion - 5s samples)
├── multiclass_classification/
│   ├── jump/      (action - 1-2s samples)
│   ├── punch/     (action - 1-2s samples)
│   ├── turn_left/ (action - 1-2s samples)
│   └── turn_right/(action - 1-2s samples)
└── noise/
    └── baseline/   (optional noise detection)
```

## Why Two Separate Classifiers?

The data has **different characteristics**:
- **Locomotion (walk/idle)**: 5-second samples, slower state changes
- **Actions (jump/punch/turn)**: 1-2 second samples, quick gestures

Separating them allows:
1. Different window sizes for optimal detection
2. Parallel execution for simultaneous actions
3. Better accuracy by matching classifier to data characteristics

## Usage

### 1. Organize Your Data

```bash
cd /path/to/project
python src/organize_training_data.py --input data/button_collected --output data/organized_training
```

**Output:**
```
📊 Data Distribution (balanced):
  Binary Classification (Locomotion):
    - walk: 30 samples (5s each)
    - idle: 30 samples (5s each)
  Multi-class Classification (Actions):
    - jump: 30 samples (1-2s each)
    - punch: 30 samples (1-2s each)
    - turn_left: 30 samples (1-2s each)
    - turn_right: 30 samples (1-2s each)
```

### 2. Train Both Models

```bash
python notebooks/SVM_Local_Training.py
```

Or use Jupyter:
```bash
jupyter notebook notebooks/SVM_Local_Training.ipynb
```

**Training Output:**
- Binary Model: `models/gesture_classifier_binary.pkl`
- Multi-class Model: `models/gesture_classifier_multiclass.pkl`
- Scalers and feature lists for both

### 3. Test Results

Example training results:
```
Binary Classifier (Walk vs Idle):
   Training accuracy: 93.75%
   Test accuracy: 91.67%

Multi-class Classifier (Jump, Punch, Turn_Left, Turn_Right):
   Training accuracy: 88.54%
   Test accuracy: 62.50%
```

## Parallel Execution Pattern

The controller uses both classifiers simultaneously:

```python
# Thread 1: Locomotion detection (5s windows)
locomotion = binary_classifier.predict(features_5s)  # 'walk' or 'idle'

# Thread 2: Action detection (1-2s windows)
action = multiclass_classifier.predict(features_1_2s)  # 'jump', 'punch', 'turn_left', 'turn_right', or None

# Combine results
if locomotion == 'walk':
    hold_arrow_key()
else:  # idle
    release_arrow_keys()

if action == 'jump':
    press_z_key()
elif action == 'punch':
    press_x_key()
elif action in ['turn_left', 'turn_right']:
    change_direction(action)
```

## Key Differences from Previous Approach

### ❌ OLD (Incorrect):
- Binary: "walking" vs "not_walking" (combined all non-walking into one class)
- Multi-class: jump, punch, turn, idle (included idle which is locomotion)
- Sequential: Binary first, then multi-class only if "not_walking"
- Problem: Can't walk and jump simultaneously

### ✅ NEW (Correct):
- Binary: walk vs idle (locomotion states only)
- Multi-class: jump, punch, turn_left, turn_right (actions only)
- Parallel: Both run simultaneously with different window sizes
- Benefit: Can walk + jump, walk + punch, etc.

## Migration Guide

If you have old organized training data:

1. Delete the old `data/organized_training/` folder
2. Re-run `python src/organize_training_data.py`
3. Re-train with `python notebooks/SVM_Local_Training.py`

The new models will be saved with the correct architecture.
