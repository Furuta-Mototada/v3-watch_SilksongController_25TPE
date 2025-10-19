# Sample Data Collection Output

This document shows what the output looks like from a successful data collection session.

## Console Output Example

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║            SILKSONG CONTROLLER - PHASE II DATA COLLECTION        ║
║              IMU Gesture Training Data Acquisition               ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

Welcome to the guided data collection procedure!

This tool will help you collect high-quality IMU sensor data for training
a machine learning gesture recognition model.

WHAT TO EXPECT:
  • You will be guided through different physical stances
  • For each stance, you'll perform specific gestures
  • Each gesture will be repeated 5 times
  • Clear instructions will be provided before each recording
  • The entire process takes approximately 20-30 minutes

...

Press [Enter] to begin setup...

🔍 Auto-detecting IP address...
Auto-detected IP address: 192.168.1.100
✓ Updated config.json
  Old IP: 192.168.1.113
  New IP: 192.168.1.100
✓ Output directory created: training_data/session_20251013_143022
✓ Listening on 192.168.1.100:12345

──────────────────────────────────────────────────────────────────
CONNECTION CHECK
──────────────────────────────────────────────────────────────────
Checking if watch is sending data...
Please make sure streaming is ON in your watch app.
✓ Connection verified! Receiving sensor data.

╔══════════════════════════════════════════════════════════════════╗
║  Please adopt: COMBAT STANCE                                     ║
╚══════════════════════════════════════════════════════════════════╝

Hold your arm as if wielding a weapon:
  • Forearm extended forward, elbow at ~90 degrees
  • Watch face oriented SIDEWAYS (not facing up or down)
  • Arm at shoulder height or slightly below
  • Comfortable position that you can hold for 1-2 minutes

This is the stance for ATTACK gestures.

Press [Enter] when you have adopted this stance...

══════════════════════════════════════════════════════════════════
  GESTURE: PUNCH FORWARD
══════════════════════════════════════════════════════════════════

──────────────────────────────────────────────────────────────────
Recording: Punch Forward - Sample 1/5
──────────────────────────────────────────────────────────────────

Execute a sharp, forward PUNCH motion:
  • From combat stance, thrust your fist forward
  • Motion should be crisp and deliberate
  • Return to combat stance after the punch
  • Think of striking a target in front of you

Press [Enter] when ready to execute this gesture...

  3...
  2...
  1...

  🔴 RECORDING - EXECUTE GESTURE NOW!
  ⏱️  Recording... 2.5s remaining
  ✓ Recording complete!
  📊 Captured 142 data points
  💾 Saved: punch_forward_sample01.csv

  Take a moment to reset to stance...

──────────────────────────────────────────────────────────────────
Recording: Punch Forward - Sample 2/5
──────────────────────────────────────────────────────────────────
...

  ✓ Gesture complete! Take a short break if needed.
  Press [Enter] to continue to next gesture (or 'q' to quit)...

══════════════════════════════════════════════════════════════════
  GESTURE: PUNCH UPWARD
══════════════════════════════════════════════════════════════════
...

══════════════════════════════════════════════════════════════════
  STANCE COMPLETE!
══════════════════════════════════════════════════════════════════
  Take a longer break. Stretch, have some water.
  Press [Enter] when ready for the next stance...

[... continues through all stances and gestures ...]

╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║                  DATA COLLECTION COMPLETE!                       ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

📊 Session Summary:
   • Session ID: 20251013_143022
   • Gestures collected: 8
   • Samples per gesture: 5
   • Output directory: training_data/session_20251013_143022

💾 Session metadata saved: training_data/session_20251013_143022/session_metadata.json

✨ Your training data is ready for the next phase: Model Training!
   All files have been saved to: training_data/session_20251013_143022

✓ Cleanup complete. Thank you!
```

## File System Output

After a complete session:

```
training_data/
└── session_20251013_143022/
    ├── punch_forward_sample01.csv      (15 KB)
    ├── punch_forward_sample02.csv      (16 KB)
    ├── punch_forward_sample03.csv      (14 KB)
    ├── punch_forward_sample04.csv      (15 KB)
    ├── punch_forward_sample05.csv      (16 KB)
    ├── punch_upward_sample01.csv       (14 KB)
    ├── punch_upward_sample02.csv       (15 KB)
    ├── punch_upward_sample03.csv       (16 KB)
    ├── punch_upward_sample04.csv       (15 KB)
    ├── punch_upward_sample05.csv       (14 KB)
    ├── jump_quick_sample01.csv         (12 KB)
    ├── jump_quick_sample02.csv         (13 KB)
    ├── jump_quick_sample03.csv         (12 KB)
    ├── jump_quick_sample04.csv         (13 KB)
    ├── jump_quick_sample05.csv         (12 KB)
    ├── jump_sustained_sample01.csv     (13 KB)
    ├── jump_sustained_sample02.csv     (14 KB)
    ├── jump_sustained_sample03.csv     (13 KB)
    ├── jump_sustained_sample04.csv     (14 KB)
    ├── jump_sustained_sample05.csv     (13 KB)
    ├── rest_sample01.csv               (8 KB)
    ├── rest_sample02.csv               (8 KB)
    ├── rest_sample03.csv               (9 KB)
    ├── rest_sample04.csv               (8 KB)
    ├── rest_sample05.csv               (8 KB)
    ├── walk_in_place_sample01.csv      (18 KB)
    ├── walk_in_place_sample02.csv      (19 KB)
    ├── walk_in_place_sample03.csv      (18 KB)
    ├── walk_in_place_sample04.csv      (19 KB)
    ├── walk_in_place_sample05.csv      (18 KB)
    ├── turn_left_sample01.csv          (11 KB)
    ├── turn_left_sample02.csv          (12 KB)
    ├── turn_left_sample03.csv          (11 KB)
    ├── turn_left_sample04.csv          (12 KB)
    ├── turn_left_sample05.csv          (11 KB)
    ├── turn_right_sample01.csv         (12 KB)
    ├── turn_right_sample02.csv         (11 KB)
    ├── turn_right_sample03.csv         (12 KB)
    ├── turn_right_sample04.csv         (11 KB)
    ├── turn_right_sample05.csv         (12 KB)
    └── session_metadata.json           (2 KB)

Total: 41 files, ~550 KB
```

## Sample CSV Content

**File: `punch_forward_sample01.csv`** (first 10 rows)

```csv
timestamp,sensor,gesture,stance,sample,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,rot_w,rot_x,rot_y,rot_z
0.001,rotation_vector,punch_forward,combat,1,,,,,,,0.892,0.123,-0.456,0.789
0.012,linear_acceleration,punch_forward,combat,1,12.45,3.21,-1.15,,,,,,,
0.015,gyroscope,punch_forward,combat,1,,,,,0.52,2.14,0.31,,,,
0.023,rotation_vector,punch_forward,combat,1,,,,,,,0.891,0.125,-0.454,0.790
0.029,linear_acceleration,punch_forward,combat,1,15.67,4.32,-0.89,,,,,,,
0.034,gyroscope,punch_forward,combat,1,,,,,0.63,2.45,0.28,,,,
0.045,rotation_vector,punch_forward,combat,1,,,,,,,0.889,0.128,-0.451,0.792
0.051,linear_acceleration,punch_forward,combat,1,18.92,5.67,-0.54,,,,,,,
0.056,gyroscope,punch_forward,combat,1,,,,,0.78,2.89,0.22,,,,
...
```

**Key observations**:
- Each row represents one sensor reading
- Timestamp increases from 0.000 to ~3.000 seconds
- Different sensors have different fields populated
- All rows share: timestamp, sensor, gesture, stance, sample

## Sample Metadata File

**File: `session_metadata.json`**

```json
{
  "session_id": "20251013_143022",
  "date": "2025-10-13T14:30:22.145678",
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
    "jump_quick",
    "jump_sustained",
    "rest",
    "walk_in_place",
    "turn_left",
    "turn_right"
  ],
  "config": {
    "network": {
      "listen_ip": "192.168.1.100",
      "listen_port": 12345
    },
    "thresholds": {
      "fuel_added_per_step_sec": 0.4,
      "max_fuel_sec": 1.0,
      "punch_threshold_xy_accel": 35.06,
      "jump_threshold_z_accel": 33.65,
      "turn_threshold_degrees": 123.67
    },
    "keyboard_mappings": {
      "left": "Key.left",
      "right": "Key.right",
      "jump": "z",
      "attack": "x"
    }
  }
}
```

## Data Statistics Example

For a typical 3-second recording at ~50 Hz sampling rate:

| Sensor | Samples/Recording | Total Samples (5 reps) |
|--------|------------------|----------------------|
| rotation_vector | ~50 | ~250 |
| linear_acceleration | ~50 | ~250 |
| gyroscope | ~50 | ~250 |
| **Total per gesture** | **~150** | **~750** |

For 8 gestures × 5 samples × ~150 readings = **~6,000 total sensor readings**

## Loading Data in Python

Example code to load and explore the collected data:

```python
import pandas as pd
import glob

# Load all samples for a specific gesture
punch_files = glob.glob('training_data/session_*/punch_forward_sample*.csv')
punch_data = pd.concat([pd.read_csv(f) for f in punch_files])

print(f"Total punch samples: {punch_data['sample'].nunique()}")
print(f"Total data points: {len(punch_data)}")
print(f"Sensors recorded: {punch_data['sensor'].unique()}")

# Filter to just acceleration data
accel_data = punch_data[punch_data['sensor'] == 'linear_acceleration']
print(f"Acceleration readings: {len(accel_data)}")

# Basic statistics
print(accel_data[['accel_x', 'accel_y', 'accel_z']].describe())
```

## Visualization Example

```python
import matplotlib.pyplot as plt

# Plot acceleration for one punch sample
sample1 = punch_data[
    (punch_data['sample'] == 1) & 
    (punch_data['sensor'] == 'linear_acceleration')
]

plt.figure(figsize=(12, 6))
plt.plot(sample1['timestamp'], sample1['accel_x'], label='X-axis')
plt.plot(sample1['timestamp'], sample1['accel_y'], label='Y-axis')
plt.plot(sample1['timestamp'], sample1['accel_z'], label='Z-axis')
plt.xlabel('Time (seconds)')
plt.ylabel('Acceleration (m/s²)')
plt.title('Punch Forward - Linear Acceleration')
plt.legend()
plt.grid(True)
plt.show()
```

This would show the characteristic spike in acceleration during the punch motion.

---

**Note**: Actual file sizes and sample counts may vary based on device sensor rates and motion complexity.
