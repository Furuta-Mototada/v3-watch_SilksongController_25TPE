# Hybrid Data Collection Protocol - Visual Summary

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    GESTURE CLASSIFICATION SYSTEM                        │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
        ┌───────────▼──────────┐      ┌──────────▼──────────┐
        │  EVENT-BASED         │      │  STATE-BASED        │
        │  GESTURES            │      │  GESTURES           │
        │                      │      │                     │
        │  • PUNCH             │      │  • WALK             │
        │  • JUMP              │      │  • (Future: RUN)    │
        │  • TURN              │      │  • (Future: CLIMB)  │
        │  • NOISE             │      │                     │
        └──────────┬───────────┘      └──────────┬──────────┘
                   │                             │
        ┌──────────▼───────────┐      ┌─────────▼──────────┐
        │  SNIPPET MODE        │      │  CONTINUOUS MODE   │
        │                      │      │                    │
        │  Duration: 2.5s      │      │  Duration: 2.5min  │
        │  Repetitions: 40     │      │  Repetitions: 1    │
        │                      │      │                    │
        │  Output:             │      │  Output:           │
        │  ├─ gesture_01.csv   │      │  └─ walk_cont.csv  │
        │  ├─ gesture_02.csv   │      │                    │
        │  ├─ ...              │      │                    │
        │  └─ gesture_40.csv   │      │                    │
        └──────────┬───────────┘      └──────────┬─────────┘
                   │                             │
                   └──────────────┬──────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │   ML PIPELINE PROCESSING   │
                    └─────────────┬──────────────┘
                                  │
                    ┌─────────────┴──────────────┐
                    │                            │
        ┌───────────▼─────────┐      ┌──────────▼──────────────┐
        │  DIRECT LOADING     │      │  SLIDING WINDOW         │
        │                     │      │                         │
        │  Each file =        │      │  Window: 2.5s           │
        │  1 training example │      │  Stride: 0.1s           │
        │                     │      │  Output: ~1,475 samples │
        │  Total: 40 samples  │      │                         │
        └───────────┬─────────┘      └──────────┬──────────────┘
                    │                           │
                    └────────────┬──────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   FEATURE EXTRACTION    │
                    │   (extract_features)    │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   MODEL TRAINING        │
                    │   (Random Forest, etc)  │
                    └─────────────────────────┘
```

## Data Flow Comparison

### BEFORE: Uniform Snippet Approach
```
WALK Collection:
User executes walk → 2.5s recording → Save walk_01.csv
User executes walk → 2.5s recording → Save walk_02.csv
...
User executes walk → 2.5s recording → Save walk_40.csv

Result: 40 training examples
Problem: All samples are "mid-walk", no transitions captured
```

### AFTER: Hybrid Approach
```
WALK Collection:
User walks continuously → 2.5min recording → Save walk_continuous.csv

ML Pipeline Processing:
walk_continuous.csv → Sliding window (2.5s, stride 0.1s) → 1,475 windows

Result: 1,475 training examples from single recording session
Benefit: Captures start, maintain, stop phases + 37x more data
```

## Collection Time Breakdown

```
┌────────────────────────────────────────────────────────────┐
│  GESTURE    │  MODE       │  OLD TIME  │  NEW TIME  │  Δ   │
├────────────────────────────────────────────────────────────┤
│  PUNCH      │  Snippet    │   15 min   │   15 min   │   0  │
│  JUMP       │  Snippet    │   15 min   │   15 min   │   0  │
│  TURN       │  Snippet    │   15 min   │   15 min   │   0  │
│  WALK       │  Continuous │   15 min   │    3 min   │ -12m │
│  NOISE      │  Snippet    │   30 min   │   30 min   │   0  │
├────────────────────────────────────────────────────────────┤
│  TOTAL      │             │   90 min   │   78 min   │ -12m │
└────────────────────────────────────────────────────────────┘
```

## File Output Structure

```
training_data/
└── session_20251014_143052/
    ├── punch_sample01.csv      ┐
    ├── punch_sample02.csv      │
    ├── ...                     │  SNIPPET MODE
    ├── punch_sample40.csv      │  (Event Gestures)
    │                           │
    ├── jump_sample01.csv       │
    ├── ...                     │
    ├── jump_sample40.csv       │
    │                           │
    ├── turn_sample01.csv       │
    ├── ...                     │
    ├── turn_sample40.csv       ┘
    │
    ├── walk_continuous.csv     ←── CONTINUOUS MODE (State Gesture)
    │                               Single 2.5-minute recording
    │
    ├── noise_sample01.csv      ┐
    ├── ...                     │  SNIPPET MODE
    ├── noise_sample80.csv      ┘  (Stray Catcher)
    │
    └── session_metadata.json
```

## Training Data Statistics

```
┌──────────────────────────────────────────────────────────────┐
│              TRAINING EXAMPLES PER GESTURE                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  PUNCH:   ■■■■■■■■  40 samples                              │
│  JUMP:    ■■■■■■■■  40 samples                              │
│  TURN:    ■■■■■■■■  40 samples                              │
│  WALK:    ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■  1,475 samples   │
│  NOISE:   ■■■■■■■■■■■■■■■■  80 samples                      │
│                                                              │
│  TOTAL:   1,675 training examples                           │
│                                                              │
│  ★ Balanced via class weighting in ML pipeline              │
└──────────────────────────────────────────────────────────────┘
```

## Code Structure

```python
# data_collector.py

class DataCollector:

    def record_gesture(gesture_key, sample_num):
        """SNIPPET MODE - For event gestures"""
        # Record 2.5s
        # Save as gesture_sampleXX.csv

    def record_continuous_gesture(gesture_key, duration_min):
        """CONTINUOUS MODE - For state gestures"""
        # Record 2.5min
        # Save as gesture_continuous.csv
        # Display progress bar

    def _save_recording(gesture_key, sample_num):
        """Save snippet mode data"""

    def _save_continuous_recording(gesture_key):
        """Save continuous mode data"""

# Main Loop (Simplified)
for gesture_key in gestures:
    mode = GESTURES[gesture_key]["collection_mode"]

    if mode == "continuous":
        record_continuous_gesture(gesture_key, 2.5)
    else:
        for sample in range(1, 41):
            record_gesture(gesture_key, sample)
```

## Key Advantages

```
┌────────────────────────────────────────────────────────────────┐
│  ADVANTAGE                    │  IMPACT                        │
├────────────────────────────────────────────────────────────────┤
│  Training-Inference Alignment │  Higher accuracy, less         │
│  (Both use sliding window)    │  overfitting                   │
├────────────────────────────────────────────────────────────────┤
│  Temporal Context Preserved   │  Model learns transitions      │
│  (Start, maintain, stop)      │  and rhythmic patterns         │
├────────────────────────────────────────────────────────────────┤
│  37x More WALK Training Data  │  More robust classifier        │
│  (1,475 vs 40 examples)       │  for walking detection         │
├────────────────────────────────────────────────────────────────┤
│  13% Faster Data Collection   │  Better user experience        │
│  (78 min vs 90 min)           │  Less fatigue                  │
├────────────────────────────────────────────────────────────────┤
│  Scalable Pattern for Future  │  Can add RUN, CLIMB, etc       │
│  State-Based Gestures         │  using same protocol           │
└────────────────────────────────────────────────────────────────┘
```

## Decision Matrix: When to Use Each Mode

```
┌────────────────────────────────────────────────────────────────┐
│  IF GESTURE IS...                 │  USE MODE                  │
├────────────────────────────────────────────────────────────────┤
│  • Has clear start/end            │  SNIPPET                   │
│  • Atomic action                  │  (40 × 2.5s)               │
│  • Each execution independent     │                            │
│  • Examples: punch, jump, clap    │                            │
├────────────────────────────────────────────────────────────────┤
│  • Represents a state/mode        │  CONTINUOUS                │
│  • Cyclical or rhythmic pattern   │  (1 × 2.5min)              │
│  • Transitions are important      │                            │
│  • Examples: walk, run, swim      │                            │
└────────────────────────────────────────────────────────────────┘
```

## Implementation Status

```
✅ collection_mode attribute added to all gestures
✅ record_continuous_gesture() method implemented
✅ _save_continuous_recording() method implemented
✅ Main loop updated with conditional branching
✅ Progress bar with time/percentage for continuous mode
✅ Connection monitoring for both modes
✅ Documentation: HYBRID_COLLECTION_PROTOCOL.md
✅ CHANGELOG.md updated
✅ Welcome message reflects new approach
✅ Dataset breakdown updated

🚀 READY FOR EXECUTION
```

## Next Steps

1. **Test the implementation:**
   ```bash
   cd /path/to/v3-watch_SilksongController_25TPE/src
   python data_collector.py
   ```

2. **Verify WALK output:**
   - Should produce single `walk_continuous.csv` file
   - Should contain ~150 seconds of continuous data
   - Should have ~22,500 data points (at 50 Hz × 3 sensors)

3. **Update ML Pipeline (CS156_Silksong_Watch.ipynb):**
   - Add sliding window function for WALK data
   - Keep direct loading for other gestures
   - Test feature extraction on both data types

4. **Validate model performance:**
   - Compare with old approach (if baseline data exists)
   - Measure accuracy, precision, recall for all gestures
   - Pay special attention to WALK classification robustness
