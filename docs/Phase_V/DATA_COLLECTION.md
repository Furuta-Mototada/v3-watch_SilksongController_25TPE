# Phase V: Continuous Motion Data Collection

## Overview

Phase V requires a **fundamentally different data collection approach** compared to Phase II. Instead of isolated gesture snippets, we record continuous motion with all gestures naturally mixed together.

---

## Why Continuous Motion?

### The Problem with Snippets (Phase II)

**Old Approach**:
```
Record: jump_01.csv (2.5s isolated jump)
Record: jump_02.csv (2.5s isolated jump)
...
Record: jump_40.csv (2.5s isolated jump)
```

**Issues**:
1. ❌ No transitions between gestures
2. ❌ Artificial start/stop in each clip
3. ❌ Model never sees realistic motion flow
4. ❌ Can't learn "walk → jump → walk" pattern

### The Solution: Continuous Recording

**New Approach**:
```
Record: session_01.csv (10 minutes of natural motion)
  Contains: walking, jumping, punching, turning mixed naturally
  With: Labels marking when each gesture occurs
```

**Advantages**:
1. ✅ Realistic transitions captured
2. ✅ Natural gesture flow
3. ✅ Context for LSTM to learn
4. ✅ Models actual gameplay patterns

---

## Recording Sessions

### Session Structure

**Duration**: 5-10 minutes per session  
**Goal**: Minimum 10 sessions = 50-100 minutes total data

**Natural Flow Example**:
```
0:00-0:15  → Walk forward
0:15-0:16  → Jump
0:16-0:30  → Continue walking
0:30-0:31  → Punch
0:31-0:45  → Walk
0:45-0:50  → Turn around
0:50-1:05  → Walk other direction
1:05-1:06  → Jump
... continues naturally for 5-10 minutes
```

### What to Perform

**During each session, mix these gestures naturally**:

1. **Walking** (70-80% of time)
   - Natural walking pace
   - Various speeds (slow, normal, fast)
   - Different arm swings

2. **Jumping** (5-10% of time)
   - Quick upward arm motion
   - Perform every 10-20 seconds
   - Mix with different speeds

3. **Punching** (5-10% of time)
   - Forward punch motion
   - Perform every 15-30 seconds
   - Mix strong and light punches

4. **Turning** (5-10% of time)
   - 180° wrist rotation
   - Perform every 20-40 seconds
   - Left and right turns

5. **Noise** (5-10% of time)
   - Scratching head
   - Adjusting watch
   - Random arm movements

---

## Data Collection Tool

### New Tool: Continuous Recorder

**File**: `src/continuous_data_collector.py`

**Features**:
- Records continuous sensor stream
- Keyboard shortcuts mark gesture boundaries
- Real-time visualization
- Auto-saves with timestamps
- Generates label files automatically

### Usage

**Step 1: Start Recording**
```bash
cd src
python continuous_data_collector.py --duration 600  # 10 minutes
```

**Step 2: Perform Motion + Mark Gestures**

While recording, press keys to mark gestures:
- **'j'** = Jump (marks next 0.3s as jump)
- **'p'** = Punch (marks next 0.3s as punch)
- **'t'** = Turn (marks next 0.5s as turn)
- **'n'** = Noise (marks next 1.0s as noise)
- **Everything else** = Walk (default state)

**Step 3: Review and Save**

Recording automatically saves:
- `data/continuous/session_01.csv` (sensor data)
- `data/continuous/session_01_labels.csv` (gesture labels)

### Recording Interface

```
┌─────────────────────────────────────────────────────────┐
│  CONTINUOUS GESTURE RECORDER                            │
│  Session: session_01                                     │
│  Duration: 03:24 / 10:00                                │
├─────────────────────────────────────────────────────────┤
│  Current State: WALKING                                 │
│  Last Gesture: JUMP (03:23.5)                          │
│                                                         │
│  Sensor Data:                                           │
│    Accel: [2.3, -0.5, 9.8]                            │
│    Gyro:  [0.1, 0.0, -0.2]                            │
│    Rot:   [0.01, -0.02, 0.03, 0.99]                   │
│                                                         │
│  Gesture Counts This Session:                          │
│    Walk:  194 seconds                                   │
│    Jump:  12 events                                     │
│    Punch: 8 events                                      │
│    Turn:  6 events                                      │
│    Noise: 4 events                                      │
├─────────────────────────────────────────────────────────┤
│  CONTROLS:                                              │
│    j = Jump  |  p = Punch  |  t = Turn  |  n = Noise  │
│    q = Quit  |  s = Save Now                          │
└─────────────────────────────────────────────────────────┘
```

---

## Label File Format

### Structure

**File**: `session_01_labels.csv`

```csv
timestamp,gesture,duration
0.0,walk,15.2
15.2,jump,0.3
15.5,walk,14.6
30.1,punch,0.3
30.4,walk,14.6
45.0,turn,0.5
45.5,walk,14.5
60.0,jump,0.3
...
```

**Fields**:
- `timestamp`: Start time of gesture (seconds)
- `gesture`: Gesture name (walk, jump, punch, turn, noise)
- `duration`: How long gesture lasts (seconds)

### How Labels Are Used

**Training Process**:
```python
# Load sensor data
sensor_data = pd.read_csv('session_01.csv')
labels = pd.read_csv('session_01_labels.csv')

# For each timestep in sensor data
for t in range(len(sensor_data)):
    current_time = sensor_data.loc[t, 'timestamp']
    
    # Find which gesture is happening at this time
    for i, label in labels.iterrows():
        if label['timestamp'] <= current_time < label['timestamp'] + label['duration']:
            current_gesture = label['gesture']
            break
    
    # Train model to predict current_gesture at time t
    X = sensor_data[t-50:t]  # Last 1 second
    y = current_gesture
    train_model(X, y)
```

---

## Best Practices

### Recording Quality

**DO**:
- ✅ Perform gestures naturally as you would in gameplay
- ✅ Mix gesture speeds (fast, normal, slow)
- ✅ Include transitions between gestures
- ✅ Record in different environments
- ✅ Vary arm positions and orientations

**DON'T**:
- ❌ Perform gestures robotically
- ❌ Make every gesture exactly the same
- ❌ Record only perfect gestures
- ❌ Stop between each gesture
- ❌ Only record in one position

### Session Distribution

**Recommended**:
- Session 1-3: Normal walking pace, clear gestures
- Session 4-6: Faster pace, gameplay simulation
- Session 7-8: Different orientations, varied speeds
- Session 9-10: Edge cases, difficult transitions

### Gesture Timing

**Walk**: 
- Default state, happens most of time
- Don't mark unless specifically walking
- Natural arm swing

**Jump**:
- Mark right when you start upward motion
- Duration: 0.3 seconds
- Press 'j' at gesture start

**Punch**:
- Mark at start of forward motion
- Duration: 0.3 seconds
- Press 'p' at gesture start

**Turn**:
- Mark at start of rotation
- Duration: 0.5 seconds (slightly longer)
- Press 't' at gesture start

**Noise**:
- Any non-gesture motion
- Duration: 1.0 seconds
- Press 'n' when doing random motion

---

## Data Validation

### Automated Checks

After recording, validate data quality:

```bash
python src/validate_continuous_data.py --session session_01
```

**Checks**:
1. ✅ Sensor data continuity (no gaps)
2. ✅ Label coverage (all time labeled)
3. ✅ Gesture distribution (balanced classes)
4. ✅ Label overlap (no conflicts)
5. ✅ Minimum gesture counts

**Expected Output**:
```
Validating session_01...
  ✅ Sensor data: 30,000 samples (10 min @ 50Hz)
  ✅ No data gaps detected
  ✅ Labels cover 100% of recording
  ✅ No overlapping labels
  
Gesture Distribution:
  Walk:  450s (75%)
  Jump:  15s (2.5%)
  Punch: 12s (2%)
  Turn:  18s (3%)
  Noise: 105s (17.5%)
  
  ✅ Distribution acceptable
  ⚠️  Jump slightly low (need 15+ jumps)
  
Overall: PASSED (minor warnings)
```

### Manual Review

**Visualize recording**:
```bash
python src/visualize_session.py --session session_01
```

**Shows**:
- Sensor readings over time
- Labeled gesture regions
- Detected anomalies
- Gesture transition points

**Example Plot**:
```
Acceleration Z-axis
  ▲
  │        Jump!
  │         /\
  │        /  \
  │  ─────/────\──────────────  Walk
  │                  Punch!
  │                    \/
  └──────────────────────────────▶ Time
  
Labeled Regions:
  [Walk][Jump][Walk][Punch][Walk]...
```

---

## Dataset Requirements

### Minimum Data

**For Training**:
- **Total Sessions**: 10+ sessions
- **Total Duration**: 60+ minutes
- **Gesture Counts**:
  - Walk: 3000+ seconds
  - Jump: 60+ events (18+ seconds)
  - Punch: 50+ events (15+ seconds)
  - Turn: 40+ events (20+ seconds)
  - Noise: 300+ seconds

### Ideal Data

**For Production**:
- **Total Sessions**: 20+ sessions
- **Total Duration**: 120+ minutes
- **Multiple Users**: 3+ different people
- **Varied Conditions**: Different rooms, positions, speeds

---

## Data Augmentation

### Why Augmentation?

Even with continuous recording, we can increase dataset size:

**Techniques**:
1. **Time Warping**: Speed up/slow down slightly
2. **Noise Injection**: Add small random noise
3. **Rotation**: Rotate sensor axes (orientation change)
4. **Magnitude Scaling**: Scale sensor values slightly

**Implementation**:
```python
def augment_window(window):
    # Time warping
    window = time_warp(window, factor=0.9-1.1)
    
    # Add noise
    noise = np.random.normal(0, 0.1, window.shape)
    window = window + noise
    
    # Scale magnitude
    scale = np.random.uniform(0.9, 1.1)
    window = window * scale
    
    return window
```

**Benefits**:
- 2-3x more training data
- Better generalization
- Handles edge cases

---

## Troubleshooting

### Issue: Labels Don't Match Data

**Symptoms**: Model learns poorly, validation accuracy low

**Causes**:
- Marked gestures too early/late
- Duration too short/long
- Missed marking a gesture

**Solution**:
- Use visualization tool to review
- Re-record session if many errors
- Adjust timing in label file manually

### Issue: Imbalanced Gestures

**Symptoms**: Model always predicts "walk"

**Causes**:
- Too much walking (>90%)
- Too few action gestures

**Solution**:
- Perform more jumps/punches/turns per session
- Reduce walking time between gestures
- Use class weights during training

### Issue: Transitions Confuse Model

**Symptoms**: Poor accuracy at gesture boundaries

**Causes**:
- Abrupt transitions
- Overlapping labels
- Unclear gesture starts

**Solution**:
- Perform natural transitions
- Add small overlap in labels
- Train longer (LSTM learns transitions)

---

## Comparison: Phase II vs Phase V

| Aspect | Phase II (Snippets) | Phase V (Continuous) |
|--------|-------------------|---------------------|
| Recording | 40 isolated clips | 1 long recording |
| Duration per gesture | 2.5s | 0.3-1.0s |
| Transitions | None | Natural |
| Labels | Filenames | CSV file |
| Total time | ~90 minutes | ~60 minutes |
| Data realism | Low | High |
| LSTM training | Poor | Excellent |

---

## Next Steps

1. **Implement Recorder**: Create `continuous_data_collector.py`
2. **Record Sessions**: Collect 10+ sessions
3. **Validate Data**: Check quality and distribution
4. **Train Model**: Use continuous data with CNN/LSTM
5. **Evaluate**: Compare with Phase IV SVM

---

## Summary

Continuous motion data collection is the **foundation** of Phase V success. By capturing realistic gesture flow and transitions, we enable the CNN/LSTM model to learn true temporal patterns.

**Key Principles**:
- Natural motion beats isolated clips
- Transitions are as important as gestures
- Quality over quantity (but need minimum quantity)
- Validation prevents wasted training time

---

**Next**: See `CNN_LSTM_ARCHITECTURE.md` for model details  
**Status**: 🚧 Ready to implement recorder tool
