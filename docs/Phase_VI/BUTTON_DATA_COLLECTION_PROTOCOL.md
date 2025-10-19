# Button Data Collection Protocol

**Status**: Design Specification for Android_2_Grid App  
**Created**: October 18, 2025  
**Purpose**: Assignment Reference & Implementation Guide  
**Context**: Streamlined data collection for ML pipeline using press-and-hold interaction model

---

## Overview

This document specifies the button-based data collection protocol for the Silksong Motion Controller project. The protocol addresses data quality issues from voice-labeled collection by providing precise, user-controlled labeling during natural gameplay.

### Key Innovation

Instead of per-gesture intentional recording, this protocol allows **real-time labeling during active gameplay**:
- Left hand: Pixel Watch streaming sensor data continuously
- Right hand: Phone with button grid for instant labeling
- No interruption to gameplay flow - buttons act as "gates" for data segmentation

## Interaction Model

### Press-and-Hold Protocol

**Basic Flow:**
1. **Press button** → Start recording action + capture start timestamp
2. **Perform gesture** → Sensor data flows from watch through "open gate"
3. **Release button** → Stop recording + capture end timestamp
4. **System saves** → One training cycle complete (timestamp pair + sensor data + label)

**Example Scenario:**
```
User sees enemy in Silksong
User presses "PUNCH" button with right thumb
User executes punch motion with left hand (wearing watch)
User releases "PUNCH" button
→ System saves: punch_YYYYMMDD_HHMMSS_start_to_end.csv
```

### Why This Works

- **Organic human-ness**: Still playing the actual game, not lab exercises
- **Precise labeling**: Exact timestamps eliminate ambiguity
- **Single session**: All data collected in continuous flow
- **No voice coordination**: No conflict between speaking and moving
- **Real-time feedback**: Immediate count updates show data balance

## Button Grid Layout

### 2x3 Grid (6 Buttons)

**Decision**: Removing DASH and NOISE buttons from the interface

```
┌──────────────┬──────────────┐
│    WALK      │    IDLE      │  Row 1: Locomotion states
│   Count: 0   │   Count: 0   │  (longer duration expected)
├──────────────┼──────────────┤
│    PUNCH     │    JUMP      │  Row 2: Action gestures
│   Count: 0   │   Count: 0   │  (shorter duration)
├──────────────┼──────────────┤
│  TURN_LEFT   │  TURN_RIGHT  │  Row 3: Directional changes
│   Count: 0   │   Count: 0   │  (short, discrete actions)
└──────────────┴──────────────┘
```

**Button Behavior:**
- **Hold WALK** → Blocks noise gate, filters data to walk label, records entire walking sequence
- **Hold IDLE** → Records standing still period (when starting session, auto-captures noise baseline)
- **Tap PUNCH** → Quick press-release for discrete action
- **Tap JUMP** → Quick press-release for discrete action
- **Tap TURN_LEFT/RIGHT** → Quick press-release for 90° body rotation

### Visual Design Specifications

**Button Size:**
- Touch target: 120x120 dp (thumb-optimized)
- Minimum: 80x80 dp for accessibility

**Color States:**
- **Unpressed**: Material Gray (#757575)
- **Pressed/Recording**: Material Green (#4CAF50)
- **Post-Recording Flash**: Material Blue (#2196F3) for 300ms
- **Error State**: Material Red (#F44336) if timestamp fails

**Typography:**
- Action label: 18sp, bold, Material Sans
- Count: 14sp, regular, gray when 0, green when >0

## Data Count Display

### Real-Time Tracking

**Display Format:**
```
WALK
Count: 23
```

**Purpose**: Visual feedback to maintain balanced dataset

**Target Distribution:**
- **WALK & IDLE**: 30-50 samples each (longer durations acceptable)
- **PUNCH, JUMP, TURN_LEFT, TURN_RIGHT**: 30-50 samples each (shorter, discrete)

**Color Coding:**
- 0-9 samples: Red (⚠️ need more data)
- 10-29 samples: Yellow (🟡 building dataset)
- 30+ samples: Green (✅ sufficient for training)

### Data Balance Goals

**Why Balance Matters:**
- Prevents model bias toward overrepresented classes
- Ensures equal learning opportunity for all gestures
- Critical for first draft academic demonstration

**User Feedback:**
"I want to see the amount of data I have so on the button itself right next to the button is a count of how many times I've recorded data and this is to keep the data sort of equal"

## Dual Classifier Architecture

### Rationale

**Problem:** Walk/idle have naturally longer durations than action buttons
- WALK: User holds button 5-10 seconds
- PUNCH: User taps button <1 second

**Solution:** Train two separate classifiers to avoid duration-based data pollution

### Classifier 1: Locomotion (Walk vs. Idle)

**Classes:** 
- `walk` - Active walking motion
- `idle` - Standing still, minimal movement

**Characteristics:**
- Longer duration windows (5-10 seconds)
- Continuous state recognition
- Binary classification (simpler problem)

**Training Data Format:**
```
walk_20251018_143022_start_to_end.csv
idle_20251018_143045_start_to_end.csv
```

### Classifier 2: Actions

**Classes:**
- `punch` - Forward punch motion
- `jump` - Jumping in place
- `turn_left` - 90° left rotation
- `turn_right` - 90° right rotation

**Characteristics:**
- Shorter duration windows (0.5-2 seconds)
- Discrete action detection
- Multi-class classification (4 classes)

**Training Data Format:**
```
punch_20251018_143100_start_to_end.csv
jump_20251018_143115_start_to_end.csv
turn_left_20251018_143130_start_to_end.csv
turn_right_20251018_143145_start_to_end.csv
```

### Pipeline Architecture

```
Sensor Data Stream (50Hz from Pixel Watch)
         ↓
    Data Buffer
    ┌────┴────┐
    ↓         ↓
Classifier 1  Classifier 2
(Walk/Idle)   (Actions)
    ↓         ↓
 Locomotion   Gesture
   State    Detection
    └────┬────┘
         ↓
    Game Control
```

**Decision Logic:**
1. Classifier 1 continuously monitors: "Are we walking or idle?"
2. Classifier 2 triggers on state change: "Did an action just occur?"
3. Both classifiers run in parallel threads for <500ms latency

## Noise Data Handling

### Noise Definition

**Noise** = Any movement not matching the 6 defined gestures:
- Random arm movements
- Scratching head
- Adjusting watch
- Typing on keyboard
- etc.

### Default State: NOISE Mode

**Critical Policy**: The system operates in **NOISE mode by default**:
- If no button is pressed-and-held, ALL incoming UDP sensor data is labeled as "noise" continuously
- Only when a button is pressed does labeling switch to that specific action
- Upon button release, system immediately returns to NOISE mode
- This ensures comprehensive noise data collection during natural pauses in data collection

### Collection Strategy

**Automatic Baseline Capture (Session Start):**
1. System auto-captures first **30 seconds** as baseline noise
2. User performs natural non-gameplay movements during this period
3. Display countdown: "Capturing baseline noise: 27s remaining..."
4. After 30s, baseline complete and ready for button presses

**Continuous Noise Collection:**
- Between button presses: All sensor data labeled as noise
- During gameplay pauses: Natural noise data captured
- No manual "noise button" needed - it's the default state

**Post-Collection Segmentation:**
After data collection ends, noise data is processed:

```python
def segment_and_save_noise(noise_buffer):
    """
    Segment continuous noise into fixed-duration chunks for training.
    Includes timestamp integrity validation and random sampling.
    """
    # 1. Validate timestamp integrity
    valid_noise = [s for s in noise_buffer if s['timestamp'] and s['data']]
    
    # 2. Segment for locomotion classifier (5-second chunks)
    locomotion_segments = segment_noise(valid_noise, duration_sec=5.0)
    
    # 3. Segment for action classifier (1-second chunks)
    action_segments = segment_noise(valid_noise, duration_sec=1.0)
    
    # 4. Randomly select exactly 30 samples per classifier
    selected_locomotion = random.sample(locomotion_segments, 30)
    selected_action = random.sample(action_segments, 30)
    
    # 5. Save segments
    save_segments(selected_locomotion, "noise_locomotion_seg_")
    save_segments(selected_action, "noise_action_seg_")
```

**Alignment Logic:**
- For **Locomotion Classifier**: Chop noise into **5-second chunks** (match walk/idle duration)
- For **Action Classifier**: Chop noise into **1-second chunks** (match punch/jump duration)
- **Exactly 30 noise samples per classifier** to avoid class dominance
- Random sampling from available segments ensures diversity

**Timestamp Integrity Validation:**
Before segmentation, validate each sample:
- Has valid timestamp field
- Has complete sensor data
- Timestamps are monotonically increasing
- No gaps larger than 100ms (2 missed packets)

**Storage Format:**
```
noise_locomotion_seg_001.csv  (5 seconds @ 50Hz = 250 samples)
noise_locomotion_seg_002.csv
...
noise_locomotion_seg_030.csv

noise_action_seg_001.csv      (1 second @ 50Hz = 50 samples)
noise_action_seg_002.csv
...
noise_action_seg_030.csv
```

**Total Noise Samples**: 60 files (30 locomotion + 30 action)

## Data Pipeline Architecture

### Three-Stage Streaming

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ Pixel Watch  │─UDP──│Android Phone │─UDP──│   MacBook    │
│ (Left Wrist) │      │(Right Hand)  │      │  (Python)    │
└──────────────┘      └──────────────┘      └──────────────┘
  Sensor Data           Button Events         Data Storage
  50Hz IMU              Label + Timestamp     CSV + Labels
```

### Stage 1: Watch → Phone

**Technology:** UDP over WiFi
**Frequency:** 50Hz (~20ms per packet)
**Data Format:** 
```json
{
  "sensor": "linear_acceleration",
  "accel_x": 0.234,
  "accel_y": -0.891,
  "accel_z": 9.801,
  "timestamp": 1697654789123
}
```

**Watch App:** Unchanged from existing `Android/` folder
- Already implemented with NSD discovery
- Streams continuously regardless of button presses

### Stage 2: Phone App Logic

**Core Functionality:**
```kotlin
// Pseudo-code for button press handler
var currentRecording: Recording? = null

fun onButtonPressed(action: String) {
    val startTimestamp = System.currentTimeMillis()
    
    currentRecording = Recording(
        action = action,
        startTime = startTimestamp,
        sensorBuffer = mutableListOf()
    )
    
    // Start buffering sensor data
    sensorStreamActive = true
    
    // Send label event to MacBook
    sendUDP(LabelEvent(
        type = "label_start",
        action = action,
        timestamp = startTimestamp
    ))
    
    // Visual feedback
    updateButtonState(action, isRecording = true)
    hapticFeedback(HapticFeedbackConstants.VIRTUAL_KEY)
}

fun onButtonReleased(action: String) {
    val endTimestamp = System.currentTimeMillis()
    
    currentRecording?.let { recording ->
        recording.endTime = endTimestamp
        
        // Send label event to MacBook
        sendUDP(LabelEvent(
            type = "label_end",
            action = action,
            timestamp = endTimestamp
        ))
        
        // Update count display
        incrementCount(action)
        
        // Visual feedback
        updateButtonState(action, isRecording = false)
        hapticFeedback(HapticFeedbackConstants.VIRTUAL_KEY_RELEASE)
    }
    
    currentRecording = null
    sensorStreamActive = false
}
```

### Stage 3: Phone → MacBook

**Label Event Protocol:**
```json
{
  "type": "label_event",
  "action": "punch",
  "event": "start" | "end",
  "timestamp_ms": 1697654789123,
  "count": 15
}
```

**MacBook Python Script:**
```python
# Pseudo-code for data collector
class ButtonDataCollector:
    def __init__(self):
        self.sensor_buffer = deque(maxlen=500)  # 10 seconds at 50Hz
        self.active_recording = None
        self.action_counts = defaultdict(int)
    
    def handle_label_event(self, event):
        if event['event'] == 'start':
            self.active_recording = {
                'action': event['action'],
                'start_time': event['timestamp_ms'],
                'start_index': len(self.sensor_buffer)
            }
        
        elif event['event'] == 'end':
            if self.active_recording:
                end_index = len(self.sensor_buffer)
                
                # Extract sensor data for this recording
                recording_data = list(self.sensor_buffer)[
                    self.active_recording['start_index']:end_index
                ]
                
                # Save to CSV
                filename = f"{self.active_recording['action']}_" \
                          f"{self.active_recording['start_time']}_" \
                          f"to_{event['timestamp_ms']}.csv"
                
                self.save_recording(filename, recording_data)
                self.action_counts[self.active_recording['action']] += 1
                
                self.active_recording = None
```

## Data File Structure

### Per-Recording Files

**Filename Convention:**
```
{action}_{start_timestamp}_to_{end_timestamp}.csv
```

**Example:**
```
punch_1697654789123_to_1697654789891.csv
walk_1697654790000_to_1697654795000.csv
turn_left_1697654796123_to_1697654796789.csv
```

**CSV Format:**
```csv
timestamp,sensor,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,rot_x,rot_y,rot_z,rot_w
1697654789123,linear_acceleration,0.234,-0.891,9.801,0,0,0,0,0,0,0
1697654789143,gyroscope,0,0,0,0.123,-0.456,0.789,0,0,0,0
1697654789163,rotation_vector,0,0,0,0,0,0,0.707,0.707,0,0
```

### Session Metadata

**File:** `session_{YYYYMMDD_HHMMSS}_metadata.json`

```json
{
  "session_id": "20251018_143000",
  "start_time": "2025-10-18T14:30:00Z",
  "end_time": "2025-10-18T14:45:00Z",
  "total_duration_sec": 900,
  "action_counts": {
    "walk": 35,
    "idle": 32,
    "punch": 40,
    "jump": 38,
    "turn_left": 42,
    "turn_right": 41
  },
  "noise_segments": 30,
  "watch_model": "Pixel Watch 2",
  "phone_model": "Pixel 8 Pro",
  "sampling_rate_hz": 50,
  "notes": "Session with good data balance, collected during Silksong gameplay"
}
```

## Implementation Phases

### Phase 1: Minimal Viable Product (MVP) - 4 Hours

**Goal:** Prove the concept with minimal code

**Deliverables:**
1. Android app receives button presses
2. Sends start/end timestamps via UDP
3. Python script saves CSV files with proper naming
4. Manual verification: 20 samples per gesture

**Success Criteria:**
- Can collect balanced dataset (20 samples × 6 gestures = 120 files)
- Train SVM on collected data
- Achieve >60% accuracy on test set

### Phase 2: Full Button Grid UI - 8 Hours

**Goal:** Production-ready data collection app

**Deliverables:**
1. 2x3 button grid with Jetpack Compose
2. Real-time count display with color coding
3. Haptic feedback on press/release
4. Visual state indicators (color changes)
5. Session summary screen

**Success Criteria:**
- Intuitive UX (can use without looking at screen)
- Collect 50 samples per gesture in <20 minutes
- Zero timestamp errors or data loss

### Phase 3: Advanced Features - Future

**Potential Additions:**
- Export session data to Google Drive
- Multi-session management
- Data visualization (live sensor graphs)
- Bluetooth external button support
- Multi-user mode for collaborative datasets

## Advantages Over Voice Labeling

✅ **Precision**: Exact start/end timestamps (no transcription ambiguity)  
✅ **Coordination**: No conflict between speaking and moving  
✅ **Real-time**: No post-processing required  
✅ **Deterministic**: Button state is always unambiguous  
✅ **Balanced**: Visual counts enable intentional data balancing  
✅ **Reproducible**: Anyone can follow the protocol  
✅ **Low Latency**: Immediate label application (<50ms)

## Limitations & Trade-offs

❌ **Two-Handed**: Requires phone in right hand (can't use for gameplay controls)  
❌ **Less Organic**: More intentional than natural gameplay  
❌ **Context Switch**: Mental overhead of button pressing  
❌ **Single Focus**: Can't fully focus on game while collecting data  
❌ **Phone Dependency**: Adds additional device to setup

## Data Integrity Considerations

### Duration Mismatch Problem

**User's Concern:**
> "Obviously I'm gonna hold down the walk button longer than the action buttons so maybe... the duration won't like pollute the data"

**Solution:** Dual classifier architecture
- Separate models trained on data with similar duration characteristics
- Walk/idle naturally have longer durations → train together
- Actions naturally have shorter durations → train together
- Avoids model learning duration as a spurious feature

### Post-Processing Steps

**1. Validate Timestamps**
```python
def validate_recording(start_time, end_time, sensor_data):
    duration = end_time - start_time
    expected_samples = duration / 20  # 50Hz = 20ms per sample
    actual_samples = len(sensor_data)
    
    if abs(actual_samples - expected_samples) > 5:
        print(f"⚠️ Timestamp mismatch: expected {expected_samples}, got {actual_samples}")
        return False
    return True
```

**2. Remove Outliers**
```python
def filter_outliers(recordings, action):
    durations = [r.duration for r in recordings]
    median_duration = np.median(durations)
    
    # Keep recordings within 2x of median duration
    return [r for r in recordings 
            if 0.5 * median_duration < r.duration < 2.0 * median_duration]
```

**3. Segment Noise**
```python
def align_noise_segments(noise_data, target_classifier):
    if target_classifier == "locomotion":
        segment_duration = 5.0  # seconds
    elif target_classifier == "action":
        segment_duration = 1.0  # seconds
    
    return chunk_data(noise_data, segment_duration)
```

## Testing & Validation Protocol

### Pre-Collection Checklist

- [ ] Watch fully charged (>50%)
- [ ] Phone fully charged (>50%)
- [ ] Both devices on same WiFi network
- [ ] Python data collector script running on MacBook
- [ ] UDP connection established (check ping)
- [ ] Empty `data/button_collected/` directory ready
- [ ] Session metadata file created

### During Collection

- [ ] Monitor count displays for balance
- [ ] Check MacBook terminal for incoming label events
- [ ] Verify CSV files are being created in real-time
- [ ] Perform gestures naturally (not exaggerated)
- [ ] Take breaks every 10 minutes to avoid fatigue

### Post-Collection Validation

```bash
# Check file counts
ls data/button_collected/walk_*.csv | wc -l  # Should be ~30-50
ls data/button_collected/punch_*.csv | wc -l  # Should be ~30-50

# Validate CSV format
python src/validate_button_data.py --session 20251018_143000

# Quick training test
python src/quick_train_test.py --data data/button_collected/
```

## Example Collection Session

### Timeline (15-minute session)

**00:00 - 01:00** - Setup & Noise Baseline
- Start Python script
- Launch Android app
- Perform 30 seconds of random movements
- System auto-segments into noise samples

**01:00 - 04:00** - Locomotion States (3 min)
- Record 35× WALK gestures (walk in place, 5 sec each)
- Record 35× IDLE gestures (stand still, 5 sec each)

**04:00 - 10:00** - Action Gestures (6 min)
- Record 40× PUNCH gestures (1-2 sec each)
- Record 40× JUMP gestures (1-2 sec each)
- Record 40× TURN_LEFT gestures (<1 sec each)
- Record 40× TURN_RIGHT gestures (<1 sec each)

**10:00 - 15:00** - Buffer & Verification (5 min)
- Review count displays (all green?)
- Quick spot-check of generated CSV files
- Save session metadata
- Export to training pipeline

**Result:** Balanced dataset ready for training

## Future Enhancements

### Short-term (Phase 2)
- Session pause/resume functionality
- Undo last recording
- Export to CSV summary
- Dark mode support

### Medium-term (Phase 3)
- External Bluetooth button support
- Audio confirmation ("Punch recorded")
- Live sensor visualization
- Automatic backup to cloud storage

### Long-term (Future Research)
- Multi-person data collection mode
- Transfer learning across users
- Active learning (suggest which gesture needs more data)
- Integration with game API for automatic labeling

## References

- **Related Documentation**: `docs/ALTERNATIVE_DATA_COLLECTION_BRAINSTORM.md`
- **Voice Labeling Approach**: `docs/Phase_V/README.md`
- **Original Android App**: `Android/app/src/main/java/com/cvk/silksongcontroller/MainActivity.kt`
- **Target App Location**: `Android_2_Grid/` (reserved for this implementation)
- **ML Pipeline**: `src/udp_listener.py` (Phase IV controller)

---

## Summary

This button data collection protocol provides a **controlled, reproducible, and user-friendly** method for collecting balanced training data. By using press-and-hold interaction with real-time count feedback, it addresses the data quality issues of voice labeling while maintaining the organic feel of gameplay-based collection.

**Next Steps:**
1. Implement MVP (Phase 1) to validate approach
2. Collect initial dataset (20 samples per gesture)
3. Train dual classifiers and compare to voice-labeled results
4. If successful, build full button grid UI (Phase 2)
5. Document findings in assignment write-up

**Key Success Metric:** Can we achieve >70% accuracy with button-collected data in first draft pipeline?
