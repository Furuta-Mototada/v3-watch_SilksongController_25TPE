# Phase II: Guided Data Collection for IMU Gesture Recognition

## Overview

Phase II focuses on collecting high-fidelity, labeled IMU sensor data from the Wear OS smartwatch to train machine learning models for gesture recognition. This guide explains the data collection process, methodology, and best practices.

## What is Phase II?

While Phase I established reliable sensor streaming between the watch and host computer, Phase II shifts focus to **data acquisition for machine learning**. Instead of real-time gesture detection based on heuristic thresholds, we collect raw sensor data labeled with ground-truth gestures to train a more robust, personalized gesture recognition system.

## Objectives

1. **Collect high-quality training data** for multiple gesture types
2. **Define clear physical stances** to ensure consistent gesture execution
3. **Label data accurately** with gesture type, stance, and timestamps
4. **Export data in ML-ready format** (CSV files)
5. **Create reproducible data collection protocol** for future sessions

## Design Principles (Lessons from EMG Project)

The data collection design incorporates lessons learned from previous projects:

1. **Use composite sensors**: Leverage Android's sensor fusion (`rotation_vector`) alongside raw sensors
2. **Define stances first**: Establish clear physical postures before gesture execution
3. **Provide unambiguous instructions**: Clear, visual descriptions of each gesture
4. **Record time-series data**: Capture full temporal dynamics, not just peaks
5. **Label comprehensively**: Include stance, gesture, sample number, and timestamps
6. **User-centric design**: Prioritize ergonomics and fatigue management

## Architecture

```
┌─────────────────────┐
│   Wear OS Watch     │  Sensors: rotation_vector,
│   (Streaming ON)    │           linear_acceleration,
└──────────┬──────────┘           gyroscope
           │ UDP (JSON)
           ↓
┌─────────────────────┐
│  data_collector.py  │  • Stance guidance
│  (Host Computer)    │  • Gesture prompting
└──────────┬──────────┘  • Time-series recording
           │             • CSV export
           ↓
┌─────────────────────┐
│   Training Data     │  training_data/session_YYYYMMDD_HHMMSS/
│   (CSV Files)       │    ├── punch_forward_sample01.csv
└─────────────────────┘    ├── jump_quick_sample01.csv
                           └── session_metadata.json
```

## Stances and Gestures

### Stance Definitions

The data collection protocol defines three primary stances:

#### 1. Combat Stance
- **Purpose**: For attack/punch gestures
- **Posture**: 
  - Forearm extended forward, elbow at ~90°
  - Watch face oriented SIDEWAYS
  - Arm at shoulder height or slightly below
  - As if wielding a weapon
- **Use case**: Punch forward, Punch upward

#### 2. Neutral Stance
- **Purpose**: For jump gestures and rest/baseline
- **Posture**:
  - Arm down at side or slightly bent
  - Watch face oriented UP
  - Relaxed, natural position
- **Use case**: Quick jump, Sustained jump, Rest

#### 3. Travel Stance
- **Purpose**: For locomotion gestures
- **Posture**:
  - Arm swinging naturally as if walking
  - Watch face in comfortable orientation
  - Position allows natural arm movement
- **Use case**: Walk in place, Turn left, Turn right

### Gesture Catalog

| Gesture | Stance | Description | ML Purpose |
|---------|--------|-------------|------------|
| **Punch Forward** | Combat | Sharp forward thrust | Horizontal attack detection |
| **Punch Upward** | Combat | Vertical uppercut motion | Vertical attack detection |
| **Quick Jump** | Neutral | Small, crisp hop | Responsive jump input |
| **Sustained Jump** | Neutral | Full jump with arm raise | Charged/long jump |
| **Walk In Place** | Travel | Natural walking rhythm | Locomotion detection |
| **Turn Left** | Travel | 180° body turn left | Direction change |
| **Turn Right** | Travel | 180° body turn right | Direction change |
| **Rest** | Neutral | Complete stillness | Negative class (no gesture) |

## Data Collection Workflow

### Prerequisites

1. **Hardware Setup**:
   - Wear OS watch with sensor streaming app installed
   - Host computer (Mac/Linux/Windows) with Python
   - Both devices on same WiFi network

2. **Software Setup**:
   ```bash
   cd /path/to/v3-watch_SilksongController_25TPE
   pip install -r requirements.txt
   ```

3. **Watch Configuration**:
   - Open Silksong Controller app on watch
   - Verify connection status shows "Connected!" (green)
   - Toggle "Stream" switch to ON
   - Keep watch awake during collection

### Running Data Collection

```bash
cd src
python data_collector.py
```

### Collection Process

The script guides you through:

1. **Setup Phase**
   - Network connection verification
   - Output directory creation
   - Sensor data connection check

2. **Stance-by-Stance Collection**
   - Display stance instructions
   - User adopts physical stance
   - For each gesture in this stance:
     - Display gesture description
     - User confirms readiness
     - 3-second countdown
     - Record sensor data for 3 seconds
     - Save to CSV
     - Repeat 5 times per gesture

3. **Session Completion**
   - Save session metadata
   - Display summary statistics
   - Cleanup resources

### Duration

- **Total time**: 20-30 minutes
- **Per gesture**: ~2 minutes (5 samples × ~20 seconds each)
- **Per stance**: 5-10 minutes
- **Breaks**: Built-in between gestures and stances

## Output Format

### Directory Structure

```
training_data/
└── session_20251013_141530/
    ├── punch_forward_sample01.csv
    ├── punch_forward_sample02.csv
    ├── ...
    ├── rest_sample05.csv
    └── session_metadata.json
```

### CSV File Format

Each CSV contains time-series sensor data:

```csv
timestamp,sensor,gesture,stance,sample,rot_x,rot_y,rot_z,rot_w,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z
0.001,rotation_vector,punch_forward,combat,1,0.12,-0.45,0.78,0.89,...
0.012,linear_acceleration,punch_forward,combat,1,,,,12.5,3.2,-1.1,...
0.015,gyroscope,punch_forward,combat,1,,,,,,0.5,2.1,0.3
...
```

**Fields**:
- `timestamp`: Seconds since recording start (0.000 to 3.000)
- `sensor`: Sensor type (rotation_vector, linear_acceleration, gyroscope)
- `gesture`: Gesture label (e.g., punch_forward)
- `stance`: Physical stance (combat, neutral, travel)
- `sample`: Sample number (1-5)
- `rot_x/y/z/w`: Rotation quaternion (rotation_vector only)
- `accel_x/y/z`: Linear acceleration m/s² (linear_acceleration only)
- `gyro_x/y/z`: Angular velocity rad/s (gyroscope only)

### Metadata File

`session_metadata.json` contains:

```json
{
  "session_id": "20251013_141530",
  "date": "2025-10-13T14:15:30.123456",
  "recording_duration_sec": 3.0,
  "samples_per_gesture": 5,
  "sensors_collected": [
    "rotation_vector",
    "linear_acceleration", 
    "gyroscope"
  ],
  "gestures_completed": [
    "punch_forward",
    "punch_upward",
    ...
  ],
  "config": { ... }
}
```

## Best Practices

### For High-Quality Data

1. **Consistency**: Execute each gesture the same way across samples
2. **Deliberate motion**: Don't rush - make crisp, clear movements
3. **Return to stance**: Always return to defined stance between samples
4. **Stay fresh**: Take breaks if you feel fatigued
5. **Secure watch**: Ensure watch is firmly on wrist, not loose

### Troubleshooting

**No data received**:
- Check watch app streaming toggle is ON
- Verify both devices on same network
- Check `udp_listener.py` is NOT running (port conflict)

**Low sample count**:
- Ensure watch stays awake (tap screen periodically)
- Check WiFi signal strength
- Verify watch battery level

**Inconsistent gestures**:
- Review stance description before each gesture
- Take longer breaks between samples
- Practice gesture motion before recording

## Next Steps: Model Training (Phase III)

Once data collection is complete, the CSV files can be used to:

1. **Feature Engineering**: Extract meaningful features from time-series
2. **Model Training**: Train classifiers (Random Forest, Neural Networks, etc.)
3. **Validation**: Test model accuracy on held-out test set
4. **Deployment**: Integrate trained model into real-time controller

Example workflow:
```python
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# Load training data
data = pd.read_csv('training_data/session_*/punch_forward_sample*.csv')

# Extract features (e.g., statistical moments, FFT coefficients)
features = extract_features(data)

# Train model
model = RandomForestClassifier()
model.fit(features, labels)

# Deploy to real-time controller
```

## Technical Notes

### Sensor Details

- **rotation_vector**: Fused orientation sensor combining gyro, accel, magnetometer
  - Output: Quaternion (x, y, z, w)
  - Provides absolute orientation in world frame
  
- **linear_acceleration**: Acceleration with gravity removed
  - Output: 3-axis acceleration (x, y, z) in m/s²
  - Isolates user motion from gravitational component
  
- **gyroscope**: Raw angular velocity
  - Output: 3-axis rotation rate (x, y, z) in rad/s
  - Captures rotational dynamics

### Sampling Rate

- **Expected rate**: 30-100 Hz depending on sensor and device
- **Recording duration**: 3 seconds per gesture
- **Expected samples**: 90-300 data points per sensor per recording

### File Size Estimates

- **Per sample CSV**: ~5-20 KB
- **Full session**: ~500 KB - 2 MB
- **Storage requirements**: Minimal (< 10 MB per session)

## References

- Android Sensor Documentation: https://developer.android.com/guide/topics/sensors/sensors_motion
- Wear OS Development: https://developer.android.com/training/wearables
- Project repository: https://github.com/CarlKho-Minerva/v3-watch_SilksongController_25TPE

---

**Last Updated**: October 13, 2025  
**Version**: Phase II v1.0  
**Author**: Silksong Controller Team
