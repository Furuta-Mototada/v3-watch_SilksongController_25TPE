# Phase VI Controller - Complete Explanation

## Your Question: Why are turn_left/right in the punch folder?

### **SHORT ANSWER: They're NOT!** ✅

The confusion comes from looking at the **wrong folder**. Let me show you exactly what's in each folder:

### Folder Structure Breakdown

```
data/organized_training/
├── binary_classification/          ← For Stage 1 (Walking detector)
│   ├── walking/                    ← 30 walk samples
│   └── not_walking/                ← 150 samples (ALL non-walking gestures mixed)
│       ├── 30 idle files
│       ├── 30 jump files
│       ├── 30 punch files          ← Punch WITH other gestures (this is correct!)
│       ├── 30 turn_left files
│       └── 30 turn_right files
│
└── multiclass_classification/      ← For Stage 2 (Action classifier)
    ├── jump/                       ← 30 jump files ONLY
    ├── punch/                      ← 30 punch files ONLY (NO mixing!)
    ├── turn_left/                  ← 30 turn_left files ONLY
    ├── turn_right/                 ← 30 turn_right files ONLY
    └── idle/                       ← 30 idle files ONLY
```

### Why `binary_classification/not_walking/` Contains Everything

The **binary classifier** needs to learn:
- "This is walking" (30 samples)
- "This is NOT walking" (150 samples of everything else)

It doesn't care WHAT the non-walking action is - just that it's not walking!

So `binary_classification/not_walking/` **correctly** contains:
- Punches
- Jumps
- Turns (both directions)
- Idle

All mixed together as "not walking" examples.

### Why `multiclass_classification/punch/` is Separate

The **multi-class classifier** needs to learn:
- "This specific movement is a punch" (30 punch samples)
- "This specific movement is a jump" (30 jump samples)
- "This specific movement is turn_left" (30 turn_left samples)
- etc.

So each gesture has its **own dedicated folder** with NO mixing.

### Verification

```bash
# Check punch folder in multiclass
$ ls data/organized_training/multiclass_classification/punch/ | head -5
punch_1760841420785_to_1760841421399.csv
punch_1760841422960_to_1760841424207.csv
punch_1760841447588_to_1760841449332.csv
punch_1760841460892_to_1760841462523.csv
punch_1760841463535_to_1760841464265.csv

# Count files
$ ls data/organized_training/multiclass_classification/punch/ | wc -l
30

# Verify no mixing
$ ls data/organized_training/multiclass_classification/punch/ | grep -E "turn_|jump_|walk_|idle_"
(no output = no mixing!) ✅
```

## Two-Stage Classification Architecture

### Stage 1: Binary Classifier (Locomotion)
**Purpose**: Determine if user is walking or stationary

**Training Data**:
- `data/organized_training/binary_classification/`
  - `walking/` - 30 samples
  - `not_walking/` - 150 samples (all non-walking gestures)

**Model**: `models/binary_classifier.pkl` (SVM)

**Output**: `walking` or `not_walking`

**When it runs**: Always first

### Stage 2: Multi-Class Classifier (Actions)
**Purpose**: Identify specific action when not walking

**Training Data**:
- `data/organized_training/multiclass_classification/`
  - `jump/` - 30 samples
  - `punch/` - 30 samples
  - `turn_left/` - 30 samples
  - `turn_right/` - 30 samples
  - `idle/` - 30 samples

**Model**: `models/multiclass_classifier.pkl` (SVM)

**Output**: `jump`, `punch`, `turn_left`, `turn_right`, or `idle`

**When it runs**: Only when Stage 1 predicts `not_walking`

### Why Two Stages?

Walking is fundamentally different from discrete actions:
- **Walking**: Continuous, repetitive motion, long duration (5+ seconds)
- **Actions**: Quick, discrete movements (<2 seconds)

If we trained one classifier with all 6 classes (walk, jump, punch, turn_left, turn_right, idle), the model would get confused because walking patterns are so different from action patterns.

By separating into two stages:
1. First determine the locomotion state (moving vs stationary)
2. Then identify the specific action (only if stationary)

This prevents walking movements from being misclassified as punches or jumps, and vice versa.

## Controller Flow

```
Sensor Data (50Hz)
     ↓
[0.3s Window Buffer] (15 samples)
     ↓
[Feature Extraction] (~60 features)
     ↓
[Stage 1: Binary SVM]
     ↓
  ┌──────┴──────┐
  │             │
"walking"   "not_walking"
  │             │
  │        [Stage 2: Multi-class SVM]
  │             │
  │        ┌────┴────┬────┬──────────┬───────────┐
  │        │         │    │          │           │
  │      "jump"  "punch" "turn_L" "turn_R"   "idle"
  │        │         │    │          │           │
  └────────┴─────────┴────┴──────────┴───────────┘
                    ↓
           [Confidence Gating]
           (require 5 matching predictions)
                    ↓
           [Execute Keyboard Action]
```

## Training the Models

### Step 1: Organize Data (Already Done! ✅)

```bash
python src/organize_training_data.py \
    --input data/button_collected \
    --output data/organized_training \
    --target-samples 30
```

**Result**:
- Binary classification ready: 30 walking, 150 not-walking
- Multi-class ready: 30 samples each for 5 actions
- All properly separated into folders

### Step 2: Train SVM Models

Open `notebooks/SVM_Local_Training.ipynb` and run all cells.

The notebook will:
1. Load data from `data/organized_training/`
2. Extract features (time + frequency domain)
3. Train Stage 1 (Binary SVM)
4. Train Stage 2 (Multi-class SVM)
5. Save models to `models/` directory

**Expected Files**:
```
models/
├── binary_classifier.pkl         ← Stage 1 SVM
├── multiclass_classifier.pkl     ← Stage 2 SVM
├── binary_scaler.pkl            ← StandardScaler for Stage 1
├── multiclass_scaler.pkl        ← StandardScaler for Stage 2
└── feature_names.pkl            ← Feature ordering (important!)
```

### Step 3: Run Controller

```bash
python src/phase_vi_button_collection/phase_vi_svm_controller.py
```

The controller will:
1. Load trained models from `models/`
2. Listen for sensor data on UDP port 12345
3. Run two-stage classification
4. Execute keyboard actions

## Feature Engineering

The SVM uses ~60 engineered features per window:

**Per Axis** (accel_x/y/z, gyro_x/y/z):
- Time domain: mean, std, min, max, range, median, skew, kurtosis
- Frequency domain: FFT max, dominant frequency

**Cross-Sensor**:
- Acceleration magnitude: mean, std
- Gyroscope magnitude: mean, std

Total: 6 axes × 10 features + 4 magnitude features = **64 features**

## Performance Expectations

**Binary Classifier (Stage 1)**:
- Target: >90% accuracy
- Easy problem: walking vs everything else
- Very distinct patterns

**Multi-Class Classifier (Stage 2)**:
- Target: >80% accuracy
- Harder problem: 5 similar actions
- Turn_left vs turn_right may be confusing

**Overall System**:
- Latency: <500ms (0.3s window + 5× confidence gating)
- False positives: Minimal (confidence gating)
- Responsiveness: Good for gameplay

## Summary

1. ✅ **No mixing in multiclass folders** - each action is separate
2. ✅ **Mixing in binary/not_walking is CORRECT** - it's supposed to group all non-walking
3. ✅ **Data is properly organized** for two-stage classification
4. ✅ **Controller is ready** - just needs trained models
5. 🔄 **Next step**: Train models in `notebooks/SVM_Local_Training.ipynb`

The organization script did exactly what it should - separate the classes properly for each stage of classification!
