# Android Apps Coordination Guide

## Overview

This project uses **TWO Android apps** that work together to collect labeled gesture data:

1. **Watch App** (`Android/`) - Runs on Pixel Watch, streams sensor data
2. **Phone App** (`Android_2_Grid/`) - Runs on Android phone, sends button press labels

Both apps communicate with the Python backend via UDP on the same network.

---

## Architecture

```
┌─────────────────┐         UDP (Port 12345)          ┌──────────────────┐
│  Pixel Watch    │  ─────────────────────────────>   │                  │
│  (Android/)     │   Sensor Data @ 50Hz              │   Python         │
│                 │   (accel, gyro, rotation)         │   Backend        │
└─────────────────┘                                   │                  │
                                                       │  (dashboard or   │
┌─────────────────┐         UDP (Port 12345)          │   button_data_   │
│  Android Phone  │  ─────────────────────────────>   │   collector)     │
│  (Android_2_    │   Button Events                   │                  │
│   Grid/)        │   (start/end labels)              └──────────────────┘
└─────────────────┘
```

### Data Flow

1. **Watch streams continuously**: Sends sensor packets at ~50Hz (accel, gyro, rotation)
2. **User presses button on phone**: Phone sends "start" event with action name
3. **Python buffers sensor data**: Keeps last 30 seconds in memory
4. **User releases button**: Phone sends "end" event
5. **Python extracts and saves**: Gets sensor data between start/end timestamps

---

## Watch App (Android/)

### Purpose
Streams IMU sensor data from Pixel Watch to Python backend.

### Sensors Streamed
- **Linear Acceleration** (`Sensor.TYPE_LINEAR_ACCELERATION`)
- **Gyroscope** (`Sensor.TYPE_GYROSCOPE`)
- **Rotation Vector** (`Sensor.TYPE_ROTATION_VECTOR`)
- **Step Detector** (`Sensor.TYPE_STEP_DETECTOR`)

### UDP Packet Format
```json
{
  "sensor": "linear_acceleration",
  "timestamp_ns": 123456789000000,
  "values": {
    "x": -0.10,
    "y": -0.14,
    "z": 0.29
  }
}
```

### How to Use
1. Install app on Pixel Watch via Android Studio
2. Open app on watch
3. Enter computer's IP address (or use auto-discovery)
4. Toggle "Stream" switch to ON
5. Watch should show "Connected!" in green
6. Leave app running in background

### File Location
`Android/app/src/main/java/com/cvk/silksongcontroller/MainActivity.kt`

---

## Phone App (Android_2_Grid/)

### Purpose
Provides button grid interface for labeling gestures during data collection.

### Button Actions
- **WALK** - Walking motion
- **IDLE** - Standing still
- **PUNCH** - Attack/punch gesture
- **JUMP** - Jumping motion
- **TURN_LEFT** - Turning left
- **TURN_RIGHT** - Turning right

### UDP Packet Format

**Button Press (Start)**:
```json
{
  "type": "label_event",
  "action": "jump",
  "event": "start",
  "timestamp_ms": 1634567890123,
  "count": 5
}
```

**Button Release (End)**:
```json
{
  "type": "label_event",
  "action": "jump",
  "event": "end",
  "timestamp_ms": 1634567892456,
  "count": 5
}
```

**Connection Test**:
```json
{
  "type": "label_event",
  "event": "ping",
  "timestamp_ms": 1634567890000
}
```

### How to Use
1. Install app on Android phone via Android Studio
2. Open app on phone
3. Press "Connect" button to test connection
4. Wait for "Connected" status
5. Press and HOLD buttons while performing gestures
6. Release button when done
7. Button counter shows how many times each gesture was recorded

### File Location
`Android_2_Grid/app/src/main/java/com/example/grid_watch_udp_datacollector/MainActivity.kt`

---

## Python Backend

### Options

#### 1. Dashboard (Recommended for Troubleshooting)
**File**: `src/data_collection_dashboard.py`

**Features**:
- Real-time visualization of incoming data
- Connection status for both apps
- Live sensor values display
- Data rate metrics
- Recording status

**Usage**:
```bash
cd src
python data_collection_dashboard.py
```

#### 2. Button Data Collector (Original)
**File**: `src/button_data_collector.py`

**Features**:
- Text-based interface
- Connection verification
- Data collection and saving

**Usage**:
```bash
cd src
python button_data_collector.py
```

Both scripts:
- Listen on UDP port 12345
- Wait for both Watch and Phone to connect
- Prompt user to press ENTER when ready
- Capture 30s baseline noise (optional: `--skip-noise`)
- Save labeled gesture data to CSV files

---

## Complete Workflow

### Step 1: Start Python Backend
```bash
cd src
python data_collection_dashboard.py
```

### Step 2: Connect Watch
1. Open Watch app on Pixel Watch
2. Enable streaming
3. Python should show: "✅ Watch connected"

### Step 3: Connect Phone
1. Open Phone app on Android phone
2. Press "Connect" button
3. Python should show: "✅ Phone connected"

### Step 4: Begin Collection
1. Python will show "Press ENTER to begin"
2. Press ENTER
3. Wait for 30s baseline noise capture
4. Dashboard shows "READY"

### Step 5: Collect Gestures
1. Press and HOLD a button on phone (e.g., "JUMP")
2. Perform the gesture on watch (jump motion)
3. Release button when done
4. Repeat for each gesture type
5. Aim for 10-30 samples per gesture

### Step 6: Stop and Save
1. Press Ctrl+C in Python terminal
2. Python saves all recordings to `data/button_collected/`
3. Check CSV files have real sensor data (not zeros!)

---

## Troubleshooting

### Problem: "No data coming in"

**Check Watch App**:
- [ ] App is open on watch
- [ ] Streaming toggle is ON (green)
- [ ] Watch shows "Connected!"
- [ ] Watch screen stays on (not sleeping)

**Check Phone App**:
- [ ] App is open on phone
- [ ] "Connect" button was pressed
- [ ] Status shows "Connected"
- [ ] Buttons respond to press/release

**Check Network**:
- [ ] Both devices on same WiFi network
- [ ] Computer firewall allows UDP port 12345
- [ ] IP address is correct (check with `ifconfig` or `ipconfig`)

**Check Python**:
- [ ] Dashboard shows both connections as green
- [ ] Sensor data count is increasing
- [ ] Latest sensor values are NOT all zeros

### Problem: "CSV files have all zeros"

This means Watch app is NOT sending sensor data properly.

**Verify Watch App Sensors**:
1. Open `Android/app/src/main/java/com/cvk/silksongcontroller/MainActivity.kt`
2. Check sensors are registered:
   ```kotlin
   linearAccelerationSensor = sensorManager.getDefaultSensor(Sensor.TYPE_LINEAR_ACCELERATION)
   gyroscopeSensor = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE)
   rotationVectorSensor = sensorManager.getDefaultSensor(Sensor.TYPE_ROTATION_VECTOR)
   ```
3. Check listeners are registered when streaming starts:
   ```kotlin
   sensorManager.registerListener(this, linearAccelerationSensor, SENSOR_DELAY_GAME)
   sensorManager.registerListener(this, gyroscopeSensor, SENSOR_DELAY_GAME)
   sensorManager.registerListener(this, rotationVectorSensor, SENSOR_DELAY_GAME)
   ```
4. Rebuild and reinstall Watch app

**Check Dashboard**:
- Latest sensor values should NOT be all 0.0
- Sensor type should rotate between "linear_acceleration", "gyroscope", "rotation_vector"
- Data freshness should be "FRESH" (green)

### Problem: "Connection keeps dropping"

**Symptoms**:
- Watch/Phone shows connected, then disconnected
- Data rate drops to 0 Hz
- Python shows "connection lost" warnings

**Solutions**:
1. **WiFi Signal**: Move closer to router
2. **Battery Saver**: Disable on both devices
3. **Background Apps**: Close other network-heavy apps
4. **Watch Sleep**: Keep watch screen on during collection
5. **Restart**: Close and reopen both apps, restart Python

### Problem: "Button presses not creating files"

**Check Phone App**:
- [ ] Press AND HOLD button (not just tap)
- [ ] Hold for at least 1-2 seconds
- [ ] Release cleanly (not swipe away)
- [ ] Watch counter increment after release

**Check Python**:
- [ ] Dashboard shows "🔴 RECORDING: ACTION" when button held
- [ ] Recording ends when button released
- [ ] CSV file created in `data/button_collected/`

**Check Timestamps**:
- Phone and Python clocks should be roughly synchronized
- If phone clock is way off, timestamps won't match sensor data
- Solution: Make sure phone has network time enabled

---

## Data Verification

### Quick Test
```bash
# View a recorded CSV file
cd data/button_collected
head -20 jump_*.csv
```

**Good Data** (non-zero values):
```csv
accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,rot_w,rot_x,rot_y,rot_z,sensor,timestamp
-0.156,-0.234,0.891,0.023,-0.045,0.012,0.999,-0.001,0.023,0.015,linear_acceleration,1634567890123000000
0.012,0.045,-0.023,1.234,-0.567,0.890,0.998,0.012,-0.034,0.056,gyroscope,1634567890143000000
```

**Bad Data** (all zeros):
```csv
accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,rot_w,rot_x,rot_y,rot_z,sensor,timestamp
0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,linear_acceleration,1634567890123000000
0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,gyroscope,1634567890143000000
```

If you see all zeros, the Watch app is NOT streaming real sensor data!

### Dashboard Verification
The dashboard provides real-time verification:

1. **Connection Status**: Both should be green/connected
2. **Latest Sensor Data**: Should show non-zero values
3. **Data Freshness**: Should be "FRESH" (< 1 second old)
4. **Data Rate**: Should be ~50 Hz for sensor data
5. **Recording Status**: Should show action name when button held

---

## Building the Apps

### Watch App (Android/)
```bash
cd Android
# Open in Android Studio
# Build > Make Project
# Run > Run 'app' (select watch device)
```

### Phone App (Android_2_Grid/)
```bash
cd Android_2_Grid
# Open in Android Studio
# Build > Make Project
# Run > Run 'app' (select phone device)
```

**Note**: Both apps can be built in the same Android Studio instance using "File > Open" to switch projects.

---

## Summary

- **Watch App** = Sensor data streaming (continuous)
- **Phone App** = Button press labeling (on-demand)
- **Python Backend** = Data buffering + saving (coordinated)

Both apps must be running and connected for data collection to work properly. Use the dashboard to verify data is flowing correctly before starting your collection session.
