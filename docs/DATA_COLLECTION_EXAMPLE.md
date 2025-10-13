# Data Collection Example Output

This document shows example output from a typical data collection session.

## Session Start

```
======================================================================
           IMU GESTURE DATA COLLECTION - PHASE II
======================================================================

Welcome to the guided data collection procedure.
This tool will help you create a high-quality IMU gesture dataset.

🔍 Loading configuration...
✓ Will listen on 192.168.1.113:12345

🔌 Setting up UDP socket...
✓ Socket ready

📁 Creating data directory structure...
✓ Data will be saved to: data_collection/20251013_164530

======================================================================
                    USER STANCES OVERVIEW
======================================================================

This data collection uses THREE distinct stances:

1. COMBAT STANCE
   Purpose: For attack gestures (punch, slash, stab)
   Position: Hold watch arm as if holding a weapon
            - Watch face should be perpendicular to ground
            - Screen facing sideways (left for right-handed users)
            - Elbow bent at ~90 degrees
            - Ready to strike forward

2. NEUTRAL STANCE
   Purpose: For vertical movements (jump, hop, crouch)
   Position: Natural standing position
            - Watch face parallel to ground
            - Screen facing UP toward sky
            - Arm relaxed at side or bent naturally
            - Weight balanced on both feet

3. TRAVEL STANCE
   Purpose: For locomotion (walk, turn, stop)
   Position: Natural walking position
            - Watch face parallel to ground
            - Screen facing UP or slightly inward
            - Arm swinging naturally while walking
            - Body facing direction of travel

Press [Enter] when you are ready to continue...
```

## Configuration

```
======================================================================
                    SESSION CONFIGURATION
======================================================================

Number of samples per gesture (default: 5): 3
Duration per sample in seconds (default: 3.0): 2.5

Configuration: 3 samples × 2.5s per gesture
Press [Enter] to continue...
```

## Collecting Combat Stance Gestures

```
======================================================================
                STANCE: COMBAT
======================================================================

⚔️  COMBAT STANCE: Hold watch arm as if wielding a weapon
Press [Enter] to continue...

======================================================================
          COLLECTING: PUNCH (COMBAT Stance)
======================================================================

Gesture: Perform a sharp, forward punch motion

Sample 1 of 3
Press [Enter] when ready for sample 1...
  Get ready...
  3...
  2...
  1...
  GO!
  📊 Recording for 2.5 seconds...
  ⏱  Time remaining: 0.0s | Packets: 387
✓ Collected 387 packets
  📈 Sensor distribution:
     - gravity: 129
     - linear_acceleration: 129
     - rotation_vector: 129
✓ Saved to data_collection/20251013_164530/combat/punch/punch_sample_001.json

  Rest for a moment...

Sample 2 of 3
Press [Enter] when ready for sample 2...
  Get ready...
  3...
  2...
  1...
  GO!
  📊 Recording for 2.5 seconds...
  ⏱  Time remaining: 0.0s | Packets: 394
✓ Collected 394 packets
  📈 Sensor distribution:
     - gravity: 131
     - linear_acceleration: 132
     - rotation_vector: 131
✓ Saved to data_collection/20251013_164530/combat/punch/punch_sample_002.json

  Rest for a moment...

Sample 3 of 3
Press [Enter] when ready for sample 3...
  Get ready...
  3...
  2...
  1...
  GO!
  📊 Recording for 2.5 seconds...
  ⏱  Time remaining: 0.0s | Packets: 381
✓ Collected 381 packets
  📈 Sensor distribution:
     - gravity: 127
     - linear_acceleration: 127
     - rotation_vector: 127
✓ Saved to data_collection/20251013_164530/combat/punch/punch_sample_003.json

✓ Completed all samples for punch!

======================================================================
          COLLECTING: SLASH (COMBAT Stance)
======================================================================

Gesture: Execute a horizontal slashing motion across your body
...
```

## Session Completion

```
======================================================================
               DATA COLLECTION COMPLETE!
======================================================================

All data saved to: data_collection/20251013_164530

Next steps:
  1. Review the collected data for quality
  2. Use this data to train gesture recognition models
  3. Analyze sensor patterns and signatures

✓ Thank you for your participation!

🔌 Socket closed
```

## Example Data File Structure

After completion, you'll have:

```
data_collection/20251013_164530/
├── combat/
│   ├── punch/
│   │   ├── punch_sample_001.json
│   │   ├── punch_sample_002.json
│   │   └── punch_sample_003.json
│   ├── slash/
│   │   ├── slash_sample_001.json
│   │   ├── slash_sample_002.json
│   │   └── slash_sample_003.json
│   └── stab/
│       ├── stab_sample_001.json
│       ├── stab_sample_002.json
│       └── stab_sample_003.json
├── neutral/
│   ├── jump/
│   ├── hop/
│   └── crouch/
├── travel/
│   ├── walk/
│   ├── turn_left/
│   ├── turn_right/
│   └── stop/
└── metadata/
    └── session_info.json
```

## Example JSON Data File

**File**: `combat/punch/punch_sample_001.json`

```json
{
  "metadata": {
    "stance": "combat",
    "gesture": "punch",
    "sample_number": 1,
    "duration_seconds": 2.5,
    "timestamp": "2025-10-13T16:45:32.123456",
    "packet_count": 387
  },
  "sensor_data": [
    {
      "sensor": "rotation_vector",
      "timestamp_ns": 1234567890123456,
      "values": {
        "x": 0.123,
        "y": -0.456,
        "z": 0.789,
        "w": 0.912
      },
      "collection_timestamp": 1697213132.123
    },
    {
      "sensor": "linear_acceleration",
      "timestamp_ns": 1234567890234567,
      "values": {
        "x": 12.34,
        "y": -5.67,
        "z": 2.89
      },
      "collection_timestamp": 1697213132.134
    },
    {
      "sensor": "gravity",
      "timestamp_ns": 1234567890345678,
      "values": {
        "x": 0.12,
        "y": 9.78,
        "z": 0.34
      },
      "collection_timestamp": 1697213132.145
    }
    // ... 384 more packets
  ]
}
```

## Example Session Metadata

**File**: `metadata/session_info.json`

```json
{
  "session_timestamp": "20251013_164530",
  "session_start": "2025-10-13T16:45:30.123456",
  "session_end": "2025-10-13T17:15:45.789012",
  "listen_ip": "192.168.1.113",
  "listen_port": 12345,
  "samples_per_gesture": 3,
  "duration_per_sample": 2.5,
  "sensors_expected": [
    "rotation_vector",
    "linear_acceleration",
    "gravity"
  ],
  "status": "completed"
}
```

## Data Analysis Example

Here's how you might load and analyze the collected data:

```python
import json
import pandas as pd
from pathlib import Path

# Load a sample
sample_file = Path("data_collection/20251013_164530/combat/punch/punch_sample_001.json")
with open(sample_file, 'r') as f:
    data = json.load(f)

# Extract metadata
print(f"Gesture: {data['metadata']['gesture']}")
print(f"Stance: {data['metadata']['stance']}")
print(f"Packets: {data['metadata']['packet_count']}")

# Convert sensor data to DataFrame
df = pd.json_normalize(data['sensor_data'])
print(f"\nDataFrame shape: {df.shape}")
print(f"Sensor types: {df['sensor'].unique()}")

# Analyze linear acceleration
accel_data = df[df['sensor'] == 'linear_acceleration']
print(f"\nLinear Acceleration Stats:")
print(f"  Max X: {accel_data['values.x'].max():.2f} m/s²")
print(f"  Max Y: {accel_data['values.y'].max():.2f} m/s²")
print(f"  Max Z: {accel_data['values.z'].max():.2f} m/s²")

# Calculate magnitude of XY acceleration (punch signature)
accel_data['xy_magnitude'] = (accel_data['values.x']**2 + accel_data['values.y']**2)**0.5
print(f"  Peak XY magnitude: {accel_data['xy_magnitude'].max():.2f} m/s²")
```

## Color-Coded Terminal Output

The data collector uses ANSI color codes for better user experience:

- 🔵 **Blue**: Headers and section titles
- 🟢 **Green**: Success messages and confirmations
- 🟡 **Yellow**: Warnings and stance indicators
- 🟣 **Cyan**: Instructions and information
- ⚪ **Bold**: Important prompts and countdowns

This makes it easy to follow the procedure and understand what's happening at each step.

---

**Note**: This is example output. Actual values and packet counts will vary based on:
- Watch sensor sampling rates
- Network conditions
- User's gesture execution
- Duration settings
