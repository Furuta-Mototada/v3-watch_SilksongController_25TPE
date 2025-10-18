# Button Data Collection Protocol - Quick Start Guide

**Purpose**: Quick reference for implementing and using the button-based data collection system  
**Full Documentation**: See [BUTTON_DATA_COLLECTION_PROTOCOL.md](BUTTON_DATA_COLLECTION_PROTOCOL.md)

---

## 🎯 What Problem Does This Solve?

### The User's Vision (From Problem Statement)

> "I'm going to be doubling down on the button data collection protocol. The idea here is on my left hand, I have my pixel watch, which is streaming data. And essentially what my button pressing protocol will do is just sort of open the gates for those data to be streamed and then labeled."

### Key Requirements Addressed

✅ **Press-and-Hold Recording**: "When I punch I quickly hold... and so I hold on my... I click a button with my right hand as I punch and then left I execute the punch and then when I let go that's when it essentially creates a file"

✅ **Real-Time Count Display**: "I want to see the amount of data I have so on the button itself right next to the button is a count of how many times I've recorded data"

✅ **Data Balance**: "This is to keep the data sort of equal so in other words I want walking idle to have similar data amounts"

✅ **Dual Classifiers**: "Maybe we train like two simple classifiers... a classifier for a walk or idle and then a separate classifier for punch jump turn left turn right so that way at least the duration won't like pollute the data"

✅ **2x3 Grid**: "Let's do a two by three now getting rid of dash and noise" → Walk, Idle, Punch, Jump, Turn Left, Turn Right

✅ **Noise Handling**: Default NOISE state captures all data when no button pressed. 30s baseline at start, then continuous noise collection between button presses. Post-collection: randomly chop into 5s (locomotion) and 1s (action) segments, exactly 30 samples per classifier to avoid class dominance

✅ **Three-Stage Pipeline**: "Pixel watch data streaming to macbook by... streaming to phone" → Watch → Phone → MacBook

---

## 🚀 Quick Implementation Checklist

### Phase 1: MVP (4 hours)

**Python Backend** (`src/button_data_collector.py`):
- [ ] UDP listener for sensor data from watch
- [ ] UDP listener for label events from phone
- [ ] Buffer management for continuous sensor stream
- [ ] File creation on label_start/label_end events
- [ ] Filename format: `{action}_{start_timestamp}_to_{end_timestamp}.csv`

**Android App** (`Android_2_Grid/`):
- [ ] Basic 2x3 button grid UI (Jetpack Compose)
- [ ] Button press/release handlers
- [ ] UDP client for label events
- [ ] Count display (SharedPreferences persistence)
- [ ] NSD discovery or manual IP entry

**Testing**:
- [ ] Collect 20 samples per gesture (120 files total)
- [ ] Verify timestamp accuracy
- [ ] Train quick SVM test model
- [ ] Validate >60% accuracy

### Phase 2: Polish (8 hours)

- [ ] Visual state feedback (colors)
- [ ] Haptic feedback on press/release
- [ ] Count color coding (red/yellow/green)
- [ ] Session metadata JSON
- [ ] Error handling and edge cases

---

## 📱 Button Layout Reference

```
┌──────────────┬──────────────┐
│    WALK      │    IDLE      │  Locomotion (hold 5-10s)
│   Count: 0   │   Count: 0   │
├──────────────┼──────────────┤
│    PUNCH     │    JUMP      │  Actions (tap 1-2s)
│   Count: 0   │   Count: 0   │
├──────────────┼──────────────┤
│  TURN_LEFT   │  TURN_RIGHT  │  Turns (tap <1s)
│   Count: 0   │   Count: 0   │
└──────────────┴──────────────┘
```

**Target**: 30-50 samples per gesture

**Color Coding**:
- Count 0-9: 🔴 Red (need more)
- Count 10-29: 🟡 Yellow (building)
- Count 30+: 🟢 Green (sufficient)

---

## 🔄 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA COLLECTION SESSION                  │
└─────────────────────────────────────────────────────────────┘

[Pixel Watch]                [Phone]               [MacBook]
   (Left Wrist)              (Right Hand)          (Python)
        │                         │                     │
        │  Sensor Stream (50Hz)   │                     │
        ├────────────────────────>│                     │
        │                         │  Sensor Stream      │
        │                         ├────────────────────>│
        │                         │                     │
        │                     👆 USER PRESSES "PUNCH"   │
        │                         │                     │
        │                         │  label_start event  │
        │                         ├────────────────────>│ ← Start buffering
        │                         │                     │
        │  Sensor data continues  │                     │
        ├────────────────────────>│────────────────────>│ ← Recording...
        │                         │                     │
    💪 USER EXECUTES PUNCH MOTION                       │
        │                         │                     │
        │                     👋 USER RELEASES "PUNCH"   │
        │                         │                     │
        │                         │  label_end event    │
        │                         ├────────────────────>│ ← Stop buffering
        │                         │                     │ ← Save CSV file
        │                         │  count_update       │
        │                         │<────────────────────┤
        │                         │                     │
        │                     [Count: 1] displayed      │
        │                         │                     │
```

---

## 🧮 Dual Classifier Architecture

### Why Two Classifiers?

**Problem**: Duration mismatch pollutes training data
- Walk/Idle: Long duration (5-10 seconds)
- Actions: Short duration (1-2 seconds)

**Solution**: Separate classifiers avoid duration-based spurious correlation

### Classifier 1: Locomotion Binary

```python
# Train on long-duration data
classes = ['walk', 'idle']
window_size = 5.0  # seconds
model = SVM_Locomotion()
```

**Use Case**: "Are we currently walking or standing still?"

### Classifier 2: Action Multi-Class

```python
# Train on short-duration data
classes = ['punch', 'jump', 'turn_left', 'turn_right']
window_size = 1.0  # seconds
model = SVM_Actions()
```

**Use Case**: "Did an action just occur? Which one?"

### Deployment Pipeline

```
Continuous Sensor Stream
         │
    ┌────┴────┐
    │         │
Clf 1         Clf 2
Walk/Idle     Actions
    │         │
    └────┬────┘
         │
   Game Control
```

Both run in parallel for <500ms total latency.

---

## 📊 Sample Collection Session (15 minutes)

### Timeline

| Time   | Activity                        | Count Goal | Duration   |
|--------|---------------------------------|------------|------------|
| 0:00   | **AUTO: 30s Baseline Noise**    | Auto       | 0.5 min    |
| 0:30   | **WALK** samples                | 35×        | ~3 min     |
| 3:30   | **IDLE** samples                | 35×        | ~3 min     |
| 6:30   | **PUNCH** samples               | 40×        | ~1.5 min   |
| 8:00   | **JUMP** samples                | 40×        | ~1.5 min   |
| 9:30   | **TURN_LEFT** samples           | 40×        | ~1 min     |
| 10:30  | **TURN_RIGHT** samples          | 40×        | ~1 min     |
| 11:30  | Verification & Buffer           | N/A        | ~0.5 min   |

**Total**: ~12 minutes (30s auto-noise + 11min collection + 30s buffer)

**Result**: 230 gesture samples + 60 noise segments (30 locomotion + 30 action) ready for training

**Note**: Noise is collected continuously in gaps between button presses (default NOISE state)

---

## 🗂️ Data Output Structure

### File Organization

```
src/data/button_collected/
├── session_20251018_143000_metadata.json
├── walk_1697654789123_to_1697654795000.csv
├── walk_1697654795500_to_1697654801000.csv
├── ...
├── idle_1697654802000_to_1697654807000.csv
├── idle_1697654808000_to_1697654813000.csv
├── ...
├── punch_1697654815000_to_1697654815891.csv
├── punch_1697654816500_to_1697654817123.csv
├── ...
├── noise_locomotion_seg_001.csv  (5s chunks for walk/idle classifier)
├── noise_locomotion_seg_002.csv
├── ...
├── noise_locomotion_seg_030.csv
├── noise_action_seg_001.csv      (1s chunks for punch/jump/turn classifier)
├── noise_action_seg_002.csv
├── ...
└── noise_action_seg_030.csv
```

### CSV Format (Same as Voice-Labeled)

```csv
timestamp,sensor,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,rot_x,rot_y,rot_z,rot_w
1697654789123,linear_acceleration,0.234,-0.891,9.801,0,0,0,0,0,0,0
1697654789143,gyroscope,0,0,0,0.123,-0.456,0.789,0,0,0,0
1697654789163,rotation_vector,0,0,0,0,0,0,0.707,0.707,0,0
```

**Compatible with existing feature extraction pipeline!**

---

## 🎓 Academic Context

### Assignment Requirements Met

✅ **Complete ML Pipeline**: Data collection → Feature engineering → Training → Deployment  
✅ **Design Thinking**: Documented exploration of alternatives (voice vs. button)  
✅ **Trade-off Analysis**: Organic vs. controlled data collection  
✅ **Reproducibility**: Clear protocol anyone can follow  
✅ **Iteration**: Building on Phase V learnings

### First Draft Strategy

**Recommended Approach**:
1. Use existing Phase V voice data to demonstrate pipeline
2. Implement MVP button collector (prove concept)
3. Collect small button dataset (20 samples)
4. Compare voice vs. button results in discussion
5. Document lessons learned and future improvements

**Why This Works**:
- Shows complete pipeline (main requirement)
- Demonstrates iteration and learning
- Acknowledges data quality challenges
- Proposes concrete improvements
- Leaves room for second draft enhancements

---

## 💡 Key Design Decisions

### Why Phone App Instead of Watch App?

❌ **Watch Screen**: Too small for 2x3 button grid  
✅ **Phone Screen**: Large, thumb-accessible buttons  
❌ **Watch Input**: Difficult to press while moving  
✅ **Phone Input**: Natural one-handed operation

### Why UDP Instead of Bluetooth?

✅ **Compatibility**: Watch app already uses UDP  
✅ **Simple Protocol**: JSON over UDP is straightforward  
✅ **Low Latency**: Direct WiFi connection  
❌ **Bluetooth**: Would require rewriting watch app

### Why Separate Android_2_Grid Folder?

✅ **Separation of Concerns**: Watch sensors ≠ Phone UI  
✅ **Independent Development**: Can work on each separately  
✅ **Clear Architecture**: One folder = one component  
❌ **Combined App**: Would be confusing and harder to maintain

### Why Not Auto-Label With Game API?

❌ **Game Closed Source**: Can't access Silksong internals  
❌ **Platform Restrictions**: macOS sandboxing limits monitoring  
✅ **User Control**: Human-in-the-loop ensures quality  
✅ **Flexibility**: Works with any game or activity

---

## 🔗 Related Documentation

📄 **Full Protocol**: [BUTTON_DATA_COLLECTION_PROTOCOL.md](BUTTON_DATA_COLLECTION_PROTOCOL.md) (20 pages)  
📄 **Design Exploration**: [ALTERNATIVE_DATA_COLLECTION_BRAINSTORM.md](ALTERNATIVE_DATA_COLLECTION_BRAINSTORM.md)  
📄 **Android App**: [../Android_2_Grid/README.md](../Android_2_Grid/README.md)  
📄 **Phase V Voice**: [Phase_V/README.md](Phase_V/README.md)  
📄 **Phase IV Controller**: [Phase_IV/README.md](Phase_IV/README.md)

---

## ✅ Success Criteria

### MVP Success
- [ ] Collect 20 samples per gesture (120 files total)
- [ ] Zero timestamp errors
- [ ] Files load successfully in training pipeline
- [ ] Train SVM with button-collected data
- [ ] Achieve >60% accuracy on test set

### Full Implementation Success
- [ ] Collect 50 samples per gesture (300 files total)
- [ ] Data balanced across all gestures
- [ ] <100ms latency from button press to label event
- [ ] Train dual classifiers (locomotion + action)
- [ ] Achieve >70% accuracy on test set
- [ ] Better performance than voice-labeled data

---

**Next Steps**: See full protocol document for implementation details, code examples, and testing procedures.
