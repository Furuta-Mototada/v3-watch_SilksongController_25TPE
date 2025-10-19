# Hybrid Data Collection Protocol

## Executive Summary

**Date:** October 14, 2025
**Status:** ✅ IMPLEMENTED
**Impact:** CRITICAL - Fundamental improvement to data quality and model robustness

This document details the **Hybrid Data Collection Protocol**, a sophisticated approach that treats **event-based gestures** (PUNCH, JUMP, TURN) differently from **state-based gestures** (WALK). This architectural decision addresses a critical limitation in the original design and will significantly improve model performance.

---

## The Problem: One Size Does NOT Fit All

### Original Approach (Uniform Treatment)
The initial `data_collector.py` design treated all gestures identically:
- Record 40 discrete 2.5-second snippets for each gesture
- Each snippet is saved as an individual file
- All gestures follow the same collection protocol

**This works well for some gestures, but is fundamentally flawed for others.**

### The Critical Insight

**Not all gestures are created equal.** There are two distinct categories:

1. **Event-Based Gestures (Atomic Actions)**
   - PUNCH, JUMP, TURN
   - Have a clear **beginning** and **end**
   - Are discrete, "atomic" actions
   - Each execution is independent from the previous one
   - **✅ Snippet-based recording is OPTIMAL**

2. **State-Based Gestures (Continuous Actions)**
   - WALK
   - Represent a **state** or **mode** that persists over time
   - Have cyclical, rhythmic patterns
   - Include important **transitions** (starting, maintaining, stopping)
   - **❌ Snippet-based recording LOSES critical information**

---

## The Solution: Hybrid Collection Protocol

### Design Philosophy

> **"The data we train on must mirror the data the model will see in the wild."**

Our real-time inference engine uses a **sliding window**. If we only train on "perfect" mid-gesture snippets, the model will struggle when:
- The user is just starting a gesture (window is only partially full)
- The user is stopping a gesture (window contains the tail end)
- The gesture transitions between states

By using **continuous recording for state-based gestures**, we capture these transitions and generate training data that reflects all phases of the gesture.

---

## Implementation Details

### 1. Gesture Classification

Each gesture in the `GESTURES` dictionary now has a `collection_mode` attribute:

```python
"punch": {
    "collection_mode": "snippet",  # Event-based
    # ... other attributes
}

"walk": {
    "collection_mode": "continuous",  # State-based
    # ... other attributes
}
```

### 2. Snippet Mode (Event Gestures)

**Applies to:** PUNCH, JUMP, TURN, NOISE

**Method:** `record_gesture(gesture_key, sample_num)`

**Protocol:**
- User performs gesture 40 times
- Each execution is recorded for 2.5 seconds
- Saved as: `{gesture}_sample{01-40}.csv`
- Each file is one training example

**Example output:**
```
punch_sample01.csv
punch_sample02.csv
...
punch_sample40.csv
```

### 3. Continuous Mode (State Gestures)

**Applies to:** WALK

**Method:** `record_continuous_gesture(gesture_key, duration_min)`

**Protocol:**
- User performs gesture continuously for 2.5 minutes
- All sensor data for the entire duration is recorded
- Saved as: `walk_continuous.csv`
- This single file will generate hundreds of training examples in the ML pipeline

**Example output:**
```
walk_continuous.csv  (2.5 minutes of continuous walking data)
```

### 4. Key Implementation Functions

#### New Function: `record_continuous_gesture()`
```python
def record_continuous_gesture(self, gesture_key, duration_min):
    """
    Record a continuous gesture for an extended duration.

    This captures the full temporal dynamics including transitions
    (starting, maintaining, stopping). The ML pipeline will use
    a sliding window to generate hundreds of training samples.
    """
    duration_sec = duration_min * 60

    # Visual progress bar, connection monitoring
    # Records all sensor data for the full duration
    # Saves to {gesture}_continuous.csv
```

#### Modified Function: `_save_continuous_recording()`
```python
def _save_continuous_recording(self, gesture_key):
    """
    Save continuous recording to a single CSV file.
    Includes metadata indicating continuous collection mode.
    """
    filename = f"{gesture_key}_continuous.csv"
    # ... save logic
```

#### Updated Main Loop
The collection flow now branches based on `collection_mode`:

```python
for gesture_key in gestures_by_stance[stance_key]:
    gesture = GESTURES[gesture_key]
    collection_mode = gesture.get("collection_mode", "snippet")

    if collection_mode == "continuous":
        # CONTINUOUS: One long recording
        collector.record_continuous_gesture(gesture_key, CONTINUOUS_RECORDING_DURATION_MIN)
    else:
        # SNIPPET: Multiple short recordings
        for sample_num in range(1, SAMPLES_PER_GESTURE + 1):
            collector.record_gesture(gesture_key, sample_num)
```

---

## Impact on ML Pipeline

### Before: Snippet-Only Approach

**WALK data structure:**
- 40 files: `walk_sample01.csv` ... `walk_sample40.csv`
- Each file contains 2.5 seconds of walking
- Each file is one training example (after feature extraction)
- **Total training examples for WALK: 40**

**Problem:** All examples are "mid-walk" with no transitions.

### After: Hybrid Approach

**WALK data structure:**
- 1 file: `walk_continuous.csv`
- File contains 2.5 minutes (150 seconds) of continuous walking
- In the Jupyter Notebook, we apply a sliding window:
  - Window size: 2.5 seconds
  - Stride: 0.1 seconds (or smaller)
  - Number of windows: `(150 - 2.5) / 0.1 = 1,475 windows`
- **Total training examples for WALK: ~1,475** (from a single recording session!)

**Benefit:**
- 37x more training examples
- Examples include starting, maintaining, and stopping phases
- Model sees the gesture in all its forms
- Training data matches inference sliding window behavior

---

## Updated Data Collection Parameters

```python
# Snippet mode parameters
RECORDING_DURATION_SEC = 2.5  # Duration for event gestures
SAMPLES_PER_GESTURE = 40      # Repetitions for event gestures

# Continuous mode parameters
CONTINUOUS_RECORDING_DURATION_MIN = 2.5  # Duration for state gestures (minutes)
```

---

## Expected Dataset Structure

After running the hybrid protocol, the output directory will contain:

```
training_data/session_YYYYMMDD_HHMMSS/
├── punch_sample01.csv
├── punch_sample02.csv
│   ... (40 files)
├── punch_sample40.csv
│
├── jump_sample01.csv
│   ... (40 files)
├── jump_sample40.csv
│
├── turn_sample01.csv
│   ... (40 files)
├── turn_sample40.csv
│
├── walk_continuous.csv          ← SINGLE CONTINUOUS FILE
│
├── noise_sample01.csv
│   ... (80 files)
├── noise_sample80.csv
│
└── session_metadata.json
```

---

## Jupyter Notebook Changes Required

The ML pipeline notebook will need **two different data loading paths**:

### 1. For Event Gestures (PUNCH, JUMP, TURN, NOISE)
```python
# Load each CSV file as a single training example
gesture_files = glob.glob(f"{session_dir}/{gesture}_sample*.csv")
for file in gesture_files:
    df = pd.read_csv(file)
    features = extract_features(df)  # One feature vector
    X.append(features)
    y.append(gesture_label)
```

### 2. For State Gestures (WALK)
```python
# Load the continuous file and apply sliding window
continuous_file = f"{session_dir}/walk_continuous.csv"
df = pd.read_csv(continuous_file)

# Sliding window parameters
window_size_sec = 2.5
stride_sec = 0.1
sample_rate = 50  # Hz (adjust based on actual data)

window_samples = int(window_size_sec * sample_rate)
stride_samples = int(stride_sec * sample_rate)

# Generate training examples
for start_idx in range(0, len(df) - window_samples, stride_samples):
    end_idx = start_idx + window_samples
    window_df = df.iloc[start_idx:end_idx]
    features = extract_features(window_df)  # One feature vector per window
    X.append(features)
    y.append("WALK")
```

---

## Validation & Quality Assurance

### Visual Inspection
The continuous recording includes a **live progress bar** showing:
- Elapsed time / Total time
- Progress percentage
- Connection status
- Data collection rate (pts/s)

### Expected Data Rates
At ~50 Hz sampling rate per sensor × 3 sensors:
- **Snippet mode:** ~375 data points per 2.5s recording
- **Continuous mode:** ~22,500 data points per 2.5min recording

### Connection Monitoring
Both modes include real-time connection status:
- ✅ CONNECTED (green) - receiving data
- ❌ CONNECTION LOST (red) - no data for >2 seconds

---

## Performance Comparison

### Estimated Collection Time

| Gesture | Mode       | Old Time | New Time | Change     |
|---------|------------|----------|----------|------------|
| PUNCH   | Snippet    | 15 min   | 15 min   | No change  |
| JUMP    | Snippet    | 15 min   | 15 min   | No change  |
| TURN    | Snippet    | 15 min   | 15 min   | No change  |
| WALK    | Continuous | 15 min   | 3 min    | **-80%**   |
| NOISE   | Snippet    | 30 min   | 30 min   | No change  |
| **Total** |          | **90 min** | **78 min** | **-13%** |

**Result:** Faster collection time AND higher quality data!

---

## Theoretical Foundation

This hybrid approach is grounded in **time-series machine learning best practices**:

### 1. Training-Inference Alignment
> The distribution of training data must match the distribution of inference data.

Our inference system uses a sliding window. Our training data (for WALK) now comes from a sliding window. ✅

### 2. Temporal Context Preservation
> State-based patterns require temporal context to be meaningful.

A single "mid-walk" snippet doesn't capture the rhythm of walking. A continuous recording preserves the cyclical pattern and transitions. ✅

### 3. Data Augmentation Through Natural Variation
> The continuous recording captures natural variations in pace, intensity, and transitions.

This makes the model more robust to real-world usage patterns. ✅

---

## Future Considerations

### Potential Extension: Other Continuous Gestures

If we add more state-based gestures in the future (e.g., "RUNNING", "CLIMBING"), they should use continuous mode:

```python
"run": {
    "collection_mode": "continuous",
    # ... other attributes
}
```

### Potential Optimization: Variable Window Stride

In the ML pipeline, we could experiment with different stride values:
- **Smaller stride (0.05s):** More training examples, more overlap, longer training time
- **Larger stride (0.25s):** Fewer training examples, less redundancy, faster training

---

## Conclusion

**The Hybrid Data Collection Protocol is not just an optimization—it's a correction of a fundamental design flaw.**

By recognizing that **event-based gestures** and **state-based gestures** require different collection strategies, we have:

1. ✅ **Improved data quality** for the WALK gesture
2. ✅ **Increased training examples** from 40 to ~1,475 for WALK
3. ✅ **Ensured training-inference alignment** (both use sliding windows)
4. ✅ **Reduced collection time** by 13%
5. ✅ **Set a scalable pattern** for future state-based gestures

This is the **correct and final** data collection architecture for this project.

---

## Related Documentation

- **Implementation:** `src/data_collector.py`
- **ML Pipeline (Next Phase):** `CS156_Silksong_Watch.ipynb`
- **User Guide:** `docs/Phase_II/DATA_COLLECTION_GUIDE.md`
- **Quick Start:** `docs/Phase_II/QUICK_START.md`

---

**Status:** ✅ READY FOR EXECUTION
**Next Step:** Run `python src/data_collector.py` to begin hybrid data collection
