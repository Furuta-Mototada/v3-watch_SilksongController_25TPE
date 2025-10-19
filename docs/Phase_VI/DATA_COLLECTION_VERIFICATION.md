# DATA COLLECTION TROUBLESHOOTING & VERIFICATION

## Quick Diagnosis

**Problem**: Clicking buttons but no data files are created, or CSV files have all zeros.

**Root Causes**:
1. ❌ Watch app NOT streaming sensor data
2. ❌ Phone app NOT connected to Python backend
3. ❌ Python backend NOT running or listening on wrong port
4. ❌ Network issues (devices on different WiFi, firewall blocking)

---

## Step-by-Step Verification

### 1. Verify Python Backend is Running

```bash
cd src

# Option A: Use the NEW dashboard (recommended - shows live data!)
python data_collection_dashboard.py

# Option B: Use the original collector (text-based)
python button_data_collector.py
```

**Expected output**:
```
🔍 Waiting for connections...
   📱 Watch app: Waiting...
   📲 Phone app: Waiting...
```

If you see an error about port already in use:
```bash
# Find what's using port 12345
lsof -i :12345
# or
netstat -an | grep 12345

# Kill the process and try again
```

---

### 2. Verify Watch App is Streaming

**On Pixel Watch**:
1. Open "Silksong Controller" app
2. Toggle "Stream" switch to **ON** (should turn green)
3. Watch should show "Connected!" in green
4. Keep watch screen on (don't let it sleep)

**In Python**:
```
✅ Watch connected from 192.168.1.100
```

**If Watch doesn't connect**:

```bash
# Test watch connection separately
python src/test_connection.py
```

This will:
- Show exactly what's being received
- Display sample packets
- Report data rate
- Show troubleshooting steps if nothing arrives

**Common Watch issues**:
- ❌ App closed or crashed - Reopen it
- ❌ Streaming toggle OFF - Turn it ON
- ❌ Wrong IP address - Use NSD auto-discovery or update IP
- ❌ Watch sleeping - Keep screen on during collection
- ❌ Different WiFi network - Put both devices on same network
- ❌ Battery saver enabled - Disable it

---

### 3. Verify Phone App is Connected

**On Android Phone**:
1. Open "Button Data Collector" app (grid layout)
2. Press **"Connect"** button
3. App should show "Connected" status
4. Button grid should be visible

**In Python**:
```
✅ Phone connected from 192.168.1.101
```

**If Phone doesn't connect**:
- Check app has correct IP address (should auto-detect or manual entry)
- Verify phone is on same WiFi as computer
- Try pressing "Connect" button again
- Restart the phone app

---

### 4. Start Data Collection

**In Python**:
```
🎉 Both devices connected!
📊 Sensor packets: 142
📱 Label events: 3

Press ENTER to begin collecting data...
```

**Press ENTER** to start!

---

### 5. Verify Real-time Data (Dashboard Only)

**If using the dashboard**, you'll see:

```
CONNECTION STATUS
────────────────────────────────────────────────────────────────────────────────
  📱 Watch App:  ✓ CONNECTED  | Packets:   1234  | Rate:  48.5 Hz
  📲 Phone App:  ✓ CONNECTED  | Events:      12  | Rate:  0.05 Hz

LATEST SENSOR DATA
────────────────────────────────────────────────────────────────────────────────
  Sensor: linear_acceleration  | Freshness: FRESH (0.1s ago)

  Acceleration (m/s²):
    X:  -0.156  Y:  -0.234  Z:   0.891

  Gyroscope (rad/s):
    X:   0.023  Y:  -0.045  Z:   0.012

  Rotation Vector:
    X:  -0.001  Y:   0.023  Z:   0.015  W:   0.999
```

**Good signs**:
- ✅ Connection status shows **CONNECTED** (green)
- ✅ Data rate around **50 Hz** for watch
- ✅ Sensor values are **NOT all zeros**
- ✅ Freshness is **FRESH** (green, < 1s old)
- ✅ Sensor type rotates: `linear_acceleration`, `gyroscope`, `rotation_vector`

**Bad signs**:
- ❌ Connection status shows **DISCONNECTED** (red)
- ❌ Data rate is **0 Hz**
- ❌ Sensor values are **all zeros**
- ❌ Freshness is **NO DATA** (red)
- ❌ Sensor type stuck on one type

---

### 6. Collect Gesture Data

**On Phone**:
1. **Press and HOLD** a button (e.g., "JUMP")
2. **Perform gesture** on watch (jump motion)
3. **Release button** when done
4. Counter should increment

**In Dashboard**:
```
COLLECTION STATUS
────────────────────────────────────────────────────────────────────────────────
  🔴 RECORDING: JUMP
  ⏱  Duration: 2.34s
  📦 Buffer size: 1500
```

When you release:
```
COLLECTION STATUS
────────────────────────────────────────────────────────────────────────────────
  ✅ READY - Waiting for button press
  📦 Buffer size: 1456

RECORDING STATISTICS
────────────────────────────────────────────────────────────────────────────────
  Total Recordings: 1
  WALK:   0  IDLE:   0  PUNCH:   0
  JUMP:   1  TURN_L:   0  TURN_R:   0
```

**Repeat 10-30 times per gesture type!**

---

### 7. Verify Data Files

**Stop collector**:
Press **Ctrl+C** in Python terminal.

**Check files were created**:
```bash
ls -lh data/button_collected/

# Should show files like:
# jump_1634567890123_1634567892456.csv
# walk_1634567900000_1634567905000.csv
# ...
```

**Inspect data quality**:
```bash
# NEW: Use the CSV inspector tool!
python src/inspect_csv_data.py data/button_collected/jump_*.csv
```

**Good output**:
```
✅ Total samples: 112

📊 Sensor types:
   gyroscope                :   37 samples
   linear_acceleration      :   38 samples
   rotation_vector          :   37 samples

📈 Data Quality:
   Acceleration: ✅ 114 non-zero values
      Range: [-2.345, 3.456]
      Mean:  0.123
      Stdev: 1.234
   Gyroscope:    ✅ 111 non-zero values
      Range: [-1.234, 2.345]
      Mean:  -0.056
      Stdev: 0.789
   Rotation:     ✅ 148 non-zero values
      Range: [-0.987, 0.998]
      Mean:  0.234
      Stdev: 0.456

⏱  Timestamps:
   Duration: 2.24s
   Rate:     50.0 Hz

🎯 Overall Verdict:
   ✅ File contains real sensor data!
```

**Bad output** (all zeros):
```
📈 Data Quality:
   Acceleration: ❌ ALL ZEROS - No real data!
   Gyroscope:    ❌ ALL ZEROS - No real data!
   Rotation:     ❌ ALL ZEROS - No real data!

🎯 Overall Verdict:
   ❌ File has NO real sensor data - all zeros!
```

---

## Understanding the Data Format

### Important: Each Packet = One Sensor

The Watch app sends **separate packets** for each sensor type:

```json
// Packet 1: Acceleration
{
  "sensor": "linear_acceleration",
  "timestamp_ns": 123456789000000,
  "values": {"x": -0.156, "y": -0.234, "z": 0.891}
}

// Packet 2: Gyroscope
{
  "sensor": "gyroscope",
  "timestamp_ns": 123456789020000,
  "values": {"x": 0.023, "y": -0.045, "z": 0.012}
}

// Packet 3: Rotation
{
  "sensor": "rotation_vector",
  "timestamp_ns": 123456789040000,
  "values": {"x": -0.001, "y": 0.023, "z": 0.015, "w": 0.999}
}
```

### CSV Structure

Each row in the CSV corresponds to **one packet**:

```csv
accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,rot_w,rot_x,rot_y,rot_z,sensor,timestamp
-0.156,-0.234,0.891,0.0,0.0,0.0,1.0,0.0,0.0,0.0,linear_acceleration,123456789000000
0.0,0.0,0.0,0.023,-0.045,0.012,1.0,0.0,0.0,0.0,gyroscope,123456789020000
0.0,0.0,0.0,0.0,0.0,0.0,0.999,-0.001,0.023,0.015,rotation_vector,123456789040000
```

**This is CORRECT!** Each row has non-zero values only for its sensor type.

The `sensor` column tells you which type of measurement each row contains.

---

## Common Problems & Solutions

### Problem: "All CSV files have zeros"

**Diagnosis**: Watch app is NOT sending real sensor data.

**Solutions**:

1. **Test connection first**:
   ```bash
   python src/test_connection.py
   ```
   
   If this shows zeros too, the Watch app is the problem.

2. **Check Watch app code** (`Android/app/src/main/java/com/cvk/silksongcontroller/MainActivity.kt`):
   ```kotlin
   // Verify sensors are registered
   linearAccelerationSensor = sensorManager.getDefaultSensor(Sensor.TYPE_LINEAR_ACCELERATION)
   gyroscopeSensor = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE)
   rotationVectorSensor = sensorManager.getDefaultSensor(Sensor.TYPE_ROTATION_VECTOR)
   
   // Verify listeners are registered when streaming starts
   sensorManager.registerListener(this, linearAccelerationSensor, SENSOR_DELAY_GAME)
   sensorManager.registerListener(this, gyroscopeSensor, SENSOR_DELAY_GAME)
   sensorManager.registerListener(this, rotationVectorSensor, SENSOR_DELAY_GAME)
   ```

3. **Rebuild Watch app**:
   - Open `Android/` in Android Studio
   - Build > Clean Project
   - Build > Rebuild Project
   - Run > Run 'app' (select watch)

4. **Check Watch permissions**:
   - Settings > Apps > Silksong Controller > Permissions
   - Ensure sensor access is allowed

5. **Try a different watch** (if available) to rule out hardware issues

### Problem: "Button presses not creating files"

**Diagnosis**: Phone app events not being received or processed.

**Solutions**:

1. **Verify phone connection**:
   - Dashboard should show "✓ CONNECTED" for phone
   - "Connect" button in phone app should show "Connected"

2. **Press AND HOLD button** (don't just tap):
   - Press button down
   - Hold for 1-2 seconds while performing gesture
   - Release cleanly (no swipe away)
   - Counter should increment after release

3. **Check dashboard shows recording**:
   - Should see "🔴 RECORDING: ACTION" when button held
   - Should return to "✅ READY" when released

4. **Check timestamps**:
   - Phone and computer clocks should be roughly synchronized
   - If phone clock is way off, timestamps won't match sensor data

### Problem: "Connection keeps dropping"

**Diagnosis**: Network instability or devices going to sleep.

**Solutions**:

1. **WiFi signal**: Move devices closer to router
2. **Battery saver**: Disable on both watch and phone
3. **Background apps**: Close other network-heavy apps
4. **Watch sleep**: Keep watch screen on during collection
5. **Restart**: Close and reopen both apps, restart Python

---

## Tools Summary

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `test_connection.py` | Test watch connection only | When watch won't connect |
| `data_collection_dashboard.py` | **RECOMMENDED** - Live data collection with visualization | For data collection with real-time verification |
| `button_data_collector.py` | Original text-based collector | When terminal/dashboard has issues |
| `inspect_csv_data.py` | Verify CSV file quality | After collection to check data quality |

---

## Complete Workflow (Recommended)

```bash
# 1. Start dashboard
cd src
python data_collection_dashboard.py

# 2. Connect devices
# - Open Watch app → Enable streaming
# - Open Phone app → Press "Connect"
# - Wait for both to show "✅ CONNECTED" in dashboard

# 3. Press ENTER to start

# 4. Collect data
# - Press and hold buttons while performing gestures
# - Dashboard shows live feedback
# - Aim for 10-30 samples per gesture

# 5. Stop with Ctrl+C

# 6. Verify data quality
python src/inspect_csv_data.py data/button_collected/*.csv
```

---

## Documentation Index

- **Quick Start**: `DASHBOARD_QUICK_START.md` - How to use the dashboard
- **App Coordination**: `ANDROID_COORDINATION_GUIDE.md` - How Watch and Phone apps work together
- **Button App Fixes**: `BUTTON_APP_FIXES.md` - Recent Android fixes
- **Python Fixes**: `FIXES_ANDROID_PYTHON.md` - Recent Python fixes
- **This Document**: Troubleshooting and verification

---

## Getting Help

If you're still stuck:

1. **Capture diagnostics**:
   ```bash
   # Test watch connection
   python src/test_connection.py > watch_test.log 2>&1
   
   # Run dashboard and capture output
   python src/data_collection_dashboard.py 2>&1 | tee dashboard.log
   
   # Inspect CSV files
   python src/inspect_csv_data.py data/button_collected/*.csv > inspect.log
   ```

2. **Check these files**:
   - `watch_test.log` - Watch connection details
   - `dashboard.log` - Full dashboard output
   - `inspect.log` - Data quality report

3. **Look for error messages** in the logs

4. **Review recent fixes**:
   - `BUTTON_APP_FIXES.md` - Fixed button stuck, connection detection, CSV format
   - `FIXES_ANDROID_PYTHON.md` - Fixed sensor parsing, connection flow

---

## Success Criteria

You know it's working when:

✅ Dashboard shows both devices **CONNECTED** (green)
✅ Data rate around **50 Hz** for watch
✅ Sensor values are **NOT zeros** (dashboard shows real numbers)
✅ Freshness is **FRESH** (green, < 1s)
✅ Recording status changes when button pressed/released
✅ CSV files created in `data/button_collected/`
✅ Inspector shows **real sensor data** (not all zeros)
✅ File size > 1 KB (has actual data)

If ALL of these are true, your data collection is working perfectly! 🎉
