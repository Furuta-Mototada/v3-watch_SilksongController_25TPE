# Phase VI: Data Organization - Q&A

## Your Questions Answered

### Q1: Why does baseline say only 1 sample when it's one CSV file of a 30-second clip?

**Answer**: You're absolutely right! The original `baseline_noise_1760841370.csv` was indeed a single **30-second continuous recording** (4,583 samples at 50Hz). The script now:

1. **Segments** this file into 18 smaller 5-second clips
2. Each segment becomes an independent training sample
3. Files are saved as: `baseline_segment_001.csv`, `baseline_segment_002.csv`, etc.

**Result**:
- Before: 1 baseline sample (not enough for training)
- After: 18 baseline segments (proper training data)

The segmentation logic is in the `segment_baseline_noise()` function which:
- Reads the 30s clip
- Splits it into 5-second windows (250 samples each at 50Hz)
- Creates 18 non-overlapping segments


### Q2: Why did you mix turn left and turn right? I thought we were going to separate them.

**Answer**: They are **NOT mixed** - they're properly separated! The organization script now:

1. **Multi-class classifier** has **5 classes** (not 4):
   - `jump` (30 samples)
   - `punch` (30 samples)
   - `turn_left` (30 samples) ← Separate
   - `turn_right` (30 samples) ← Separate
   - `idle` (30 samples)

2. **Binary classifier** groups them together as "not_walking":
   - `walking` (30 samples)
   - `not_walking` (150 samples) = jump + punch + turn_left + turn_right + idle

3. **Noise detector** doesn't care about turn direction:
   - `idle` (30 samples)
   - `active` (150 samples) = all non-idle gestures
   - `baseline` (48 samples) = baseline segments + noise files

The script correctly parses compound filenames like `turn_left_1760841426505_to_1760841428161.csv` and separates them into distinct classes.

## Two-Stage Classification Architecture

Yes, you're correct about the two-stage approach:

### Stage 1: Binary Classifier (Locomotion Detection)
- **Purpose**: Determine if the user is walking or not
- **Classes**:
  - `walking` (30 samples)
  - `not_walking` (150 samples - includes all actions)
- **Output**: Walking vs Not-Walking
- **When to use**: Always runs first to determine locomotion state

### Stage 2: Multi-Class Classifier (Action Recognition)
- **Purpose**: Identify specific action when NOT walking
- **Classes**:
  - `jump` (30 samples)
  - `punch` (30 samples)
  - `turn_left` (30 samples)
  - `turn_right` (30 samples)
  - `idle` (30 samples)
- **Output**: Specific action type
- **When to use**: Only when Stage 1 detects "not_walking"

### Optional: Noise Detector
- **Purpose**: Filter out baseline noise and artifacts
- **Classes**:
  - `idle` (30 samples) - stationary with minimal movement
  - `active` (150 samples) - any deliberate gesture
  - `baseline` (48 samples) - environmental noise, hand at rest
- **When to use**: Can run before Stage 1 to filter false positives

## Class Balance Analysis

| Class | Samples | Balanced? | Notes |
|-------|---------|-----------|-------|
| walk | 30 | ✅ | Undersampled from 34 |
| jump | 30 | ✅ | Undersampled from 40 |
| punch | 30 | ✅ | Undersampled from 34 |
| turn_left | 30 | ✅ | Undersampled from 37 |
| turn_right | 30 | ✅ | Undersampled from 36 |
| idle | 30 | ✅ | Undersampled from 36 |
| baseline | 18+30 | ⚠️ | 18 segments + 30 noise files = 48 total |

**No data dominance!** All active gesture classes have exactly 30 samples. The baseline/noise class has slightly more (48) which is good for a "catch-all" category.

## Directory Structure

```
data/organized_training/
├── binary_classification/
│   ├── walking/          (30 samples)
│   └── not_walking/      (150 samples)
│
├── multiclass_classification/
│   ├── jump/             (30 samples)
│   ├── punch/            (30 samples)
│   ├── turn_left/        (30 samples)
│   ├── turn_right/       (30 samples)
│   └── idle/             (30 samples)
│
└── noise_detection/
    ├── idle/             (30 samples)
    ├── active/           (150 samples)
    └── baseline/         (48 samples)
```

## Next Steps

1. ✅ Data organized with proper class separation
2. ✅ Baseline noise segmented into 18 samples
3. ✅ Turn left/right separated into distinct classes
4. ✅ Class balance achieved (30 samples each for active gestures)
5. 🔄 Ready to train models:
   - Binary SVM (local training)
   - Multi-class CNN/LSTM (Google Colab)
   - Optional noise filter

## Model Training Strategy

### For Binary Classifier (SVM - Local)
- Fast training on laptop
- Use `binary_classification/` folder
- Traditional ML features (statistical + frequency)
- Target: >90% accuracy for walk/not-walk

### For Multi-Class Classifier (CNN/LSTM - Colab)
- Deep learning on GPU
- Use `multiclass_classification/` folder
- Raw sensor time-series input
- Target: >85% accuracy for 5-class problem

### Integration
```
Raw Sensor Data
     ↓
[Noise Filter] ← Optional
     ↓
[Binary Classifier: Walk vs Not-Walk]
     ↓
  If "Not Walking"
     ↓
[Multi-Class: Jump/Punch/Turn_L/Turn_R/Idle]
     ↓
Execute Action
```

The two-stage approach prevents the multi-class classifier from being confused by walking movements, which are fundamentally different from discrete actions.
