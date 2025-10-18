# Quick Start: Data Collection with Dashboard

## TL;DR - Get Data Flowing Now!

```bash
# 1. Start the dashboard
cd src
python data_collection_dashboard.py

# 2. Open Watch app → Enable streaming
# 3. Open Phone app → Press "Connect"
# 4. Press ENTER when both show connected
# 5. Hold buttons on phone while performing gestures
# 6. Press Ctrl+C when done
```

---

## What You'll See

### 1. Dashboard Startup
```
🔍 Waiting for connections...
   📱 Watch app: Waiting...
   📲 Phone app: Waiting...
```

### 2. Watch Connects
```
✅ Watch connected from 192.168.1.100
```

### 3. Phone Connects
```
✅ Phone connected from 192.168.1.101
🎉 Both devices connected!
📊 Sensor packets: 142
📱 Label events: 3

Press ENTER to begin collecting data...
```

### 4. Dashboard Running
```
================================================================================
         DATA COLLECTION DASHBOARD - Real-time Verification
================================================================================

Session: 2025-10-18 19:00:00 (0:02:15)
Output: /path/to/data/button_collected

CONNECTION STATUS
────────────────────────────────────────────────────────────────────────────────
  📱 Watch App:  ✓ CONNECTED  | Packets:   1234  | Rate:  48.5 Hz
  📲 Phone App:  ✓ CONNECTED  | Events:      12  | Rate:  0.05 Hz

COLLECTION STATUS
────────────────────────────────────────────────────────────────────────────────
  ✅ READY - Waiting for button press
  📦 Buffer size: 1456

LATEST SENSOR DATA
────────────────────────────────────────────────────────────────────────────────
  Sensor: linear_acceleration  | Freshness: FRESH (0.1s ago)
  Timestamp: 1729280400123000000

  Acceleration (m/s²):
    X:  -0.156  Y:  -0.234  Z:   0.891

  Gyroscope (rad/s):
    X:   0.023  Y:  -0.045  Z:   0.012

  Rotation Vector:
    X:  -0.001  Y:   0.023  Z:   0.015  W:   0.999

RECORDING STATISTICS
────────────────────────────────────────────────────────────────────────────────
  Total Recordings: 8
  WALK:   3  IDLE:   2  PUNCH:   1
  JUMP:   2  TURN_L:   0  TURN_R:   0
  NOISE:   0

================================================================================
Press Ctrl+C to stop and save data
```

---

## Dashboard Features

### ✅ Connection Verification
- **Green ✓ CONNECTED** = Device is streaming
- **Red ✗ DISCONNECTED** = Device is not responding
- **Packet/Event counts** = Total messages received
- **Rate (Hz)** = Messages per second

### 📊 Real-time Sensor Data
- **Freshness indicator**:
  - 🟢 **FRESH** (< 1s) = Data is current
  - 🟡 **STALE** (1-3s) = Data is delayed
  - 🔴 **NO DATA** (> 3s) = No recent data
- **Latest values** for all three sensors
- **Timestamp** = When data was captured

### 🔴 Recording Status
When you press a button on the phone:
```
🔴 RECORDING: JUMP
⏱  Duration: 2.34s
📦 Buffer size: 1500
```

### 📈 Statistics
- Total recordings saved
- Count per gesture type
- Tracks noise segments

---

## How to Use

### Before You Start
1. **Check WiFi**: Both watch and phone on same network
2. **Check IP**: Python dashboard will bind to `0.0.0.0:12345`
3. **Close other apps**: No other program using port 12345

### Step-by-Step

#### 1. Start Dashboard
```bash
cd src
python data_collection_dashboard.py
```

#### 2. Connect Watch
- Open Watch app on Pixel Watch
- Toggle "Stream" to ON
- Watch should show "Connected!" in green
- Dashboard should show: `✅ Watch connected`

#### 3. Connect Phone
- Open Phone button grid app
- Press "Connect" button
- App should show "Connected" status
- Dashboard should show: `✅ Phone connected`

#### 4. Start Collection
- Dashboard shows "Press ENTER to begin"
- Press ENTER
- Wait 30 seconds for baseline noise capture
- Progress bar shows capture progress

#### 5. Record Gestures
- **Press and HOLD** a button on phone (e.g., "JUMP")
- **Perform gesture** on watch (jump motion)
- **Release button** when done
- Dashboard shows recording in progress
- Repeat 10-30 times per gesture

#### 6. Stop and Save
- Press **Ctrl+C** in terminal
- Dashboard saves all recordings
- Check `data/button_collected/` for CSV files

---

## Verification Checklist

### ✅ Data Is Flowing If:
- [ ] Connection status shows both devices as **CONNECTED** (green)
- [ ] Data rate is around **50 Hz** for watch
- [ ] Latest sensor data shows **non-zero values**
- [ ] Freshness indicator is **FRESH** (green)
- [ ] Sensor type rotates: `linear_acceleration`, `gyroscope`, `rotation_vector`

### ❌ Data Is NOT Flowing If:
- [ ] Connection status shows **DISCONNECTED** (red)
- [ ] Data rate is **0 Hz**
- [ ] Latest sensor data is **all zeros**
- [ ] Freshness indicator is **NO DATA** (red)
- [ ] Timestamp never changes

---

## Troubleshooting

### Problem: Dashboard shows "DISCONNECTED"

**Watch not connecting?**
```bash
# Test watch connection separately
python src/test_connection.py
```

**Phone not connecting?**
- Press "Connect" button in phone app
- Check phone shows "Connected" status
- Verify phone is on same WiFi

### Problem: Sensor data is all zeros

**This means Watch app is NOT sending real data!**

Check Watch app:
1. Open app on watch
2. Toggle streaming OFF then ON
3. Watch should show "Connected!" in green
4. Try moving watch - sensor values should change

If still zeros:
1. Rebuild Watch app in Android Studio
2. Verify sensors are registered (see `ANDROID_COORDINATION_GUIDE.md`)
3. Check watch permissions (allow sensors)

### Problem: Recording not creating files

**Button press/release issue:**
- **Press AND HOLD** button (don't just tap)
- Hold for at least 1-2 seconds
- Release cleanly (no swipe)
- Watch counter increment after release

**Check dashboard:**
- Should show `🔴 RECORDING: ACTION` when button held
- Should return to `✅ READY` when button released
- Check `data/button_collected/` for new CSV files

---

## Output Files

### File Naming
```
action_starttime_endtime.csv

Examples:
jump_1634567890123_1634567892456.csv
walk_1634567900000_1634567905000.csv
```

### File Contents
```csv
accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,rot_w,rot_x,rot_y,rot_z,sensor,timestamp
-0.156,-0.234,0.891,0.023,-0.045,0.012,0.999,-0.001,0.023,0.015,linear_acceleration,1634567890123000000
0.012,0.045,-0.023,1.234,-0.567,0.890,0.998,0.012,-0.034,0.056,gyroscope,1634567890143000000
...
```

### Verify Data Quality
```bash
# Check a recording has non-zero data
head -10 data/button_collected/jump_*.csv

# Count recordings per action
ls data/button_collected/ | grep "^walk" | wc -l
ls data/button_collected/ | grep "^jump" | wc -l
ls data/button_collected/ | grep "^punch" | wc -l
```

---

## Tips

### Get Good Data
1. **Move naturally** - Don't exaggerate gestures
2. **Consistent duration** - Hold button for similar times (1-3s)
3. **Clear motions** - Complete full gesture before releasing
4. **Multiple angles** - Try gesture from different positions
5. **Balanced dataset** - Aim for 10-30 samples per gesture

### Dashboard Refresh Rate
- Updates every 0.5 seconds
- Shows most recent sensor values
- Buffer holds last 30 seconds of data

### Skip Noise Capture (for testing)
```bash
python data_collection_dashboard.py --skip-noise
```
Starts immediately without 30s baseline capture.

---

## Next Steps

After collecting data:

1. **Verify CSV files**:
   ```bash
   ls -lh data/button_collected/
   head data/button_collected/*.csv
   ```

2. **Check file sizes**:
   - Should be 3-10 KB per recording
   - If < 1 KB, might be empty or have too few samples

3. **Train model** (see `notebooks/` for training pipelines)

4. **Test controller** (see `src/udp_listener.py` for real-time control)

---

## Dashboard vs. Original Collector

| Feature | Dashboard | button_data_collector.py |
|---------|-----------|--------------------------|
| Real-time visualization | ✅ Yes | ❌ No |
| Connection status | ✅ Live | ⚠️ Text only |
| Sensor data display | ✅ Live values | ❌ Hidden |
| Data rate metrics | ✅ Yes | ❌ No |
| Recording feedback | ✅ Visual | ⚠️ Text only |
| Troubleshooting | ✅ Easy | ⚠️ Harder |

**Recommendation**: Use **dashboard** for data collection, especially when troubleshooting!

---

## Still Having Issues?

See full troubleshooting guide: `ANDROID_COORDINATION_GUIDE.md`

Or check recent fixes: `BUTTON_APP_FIXES.md` and `FIXES_ANDROID_PYTHON.md`
