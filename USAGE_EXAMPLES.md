# Quick Usage Examples

## Scenario 1: "I just want to collect data NOW"

```bash
cd src
python data_collection_dashboard.py
```

**What you'll see**:
1. Wait for Watch connection ✅
2. Wait for Phone connection ✅
3. Press ENTER when prompted
4. Dashboard shows live sensor data
5. Press buttons on phone to record gestures
6. Ctrl+C when done

---

## Scenario 2: "Is my Watch app sending data?"

```bash
cd src
python test_connection.py
```

**Expected output** (if working):
```
✅ CONNECTION SUCCESSFUL!

Connection Details:
  Packets received: 25
  Watch address: 192.168.1.100:54321
  Sensor types: gyroscope, linear_acceleration, rotation_vector
  
Sample Packet:
  {
    "sensor": "linear_acceleration",
    "timestamp_ns": 1234567890000000,
    "values": {
      "x": -0.156,
      "y": -0.234,
      "z": 0.891
    }
  }

✨ Your watch is connected and streaming properly!
```

**If NOT working**:
- Shows troubleshooting steps
- Indicates timeout or missing packets
- Suggests fixes

---

## Scenario 3: "Are my CSV files any good?"

```bash
cd src
python inspect_csv_data.py ../data/button_collected/jump_*.csv
```

**Good output** (real data):
```
================================================================================
Inspecting: jump_1634567890123_1634567892456.csv
================================================================================

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

💡 Troubleshooting:
   1. Check Watch app is streaming (toggle should be ON)
   2. Verify Watch app shows 'Connected!' in green
   3. Try running: python src/test_connection.py
   4. Rebuild Watch app in Android Studio
   5. Check sensor permissions on watch
```

---

## Scenario 4: "Dashboard shows all zeros - how do I fix it?"

**Step 1**: Test Watch connection separately
```bash
python src/test_connection.py
```

**Step 2**: If test shows zeros too, the problem is in the Watch app:

1. **Rebuild Watch app**:
   ```bash
   # Open Android/app in Android Studio
   # Build > Clean Project
   # Build > Rebuild Project
   # Run > Run 'app' (select watch)
   ```

2. **Check sensor registration** in `Android/app/src/main/java/com/cvk/silksongcontroller/MainActivity.kt`:
   ```kotlin
   // Verify these lines exist in onCreate():
   linearAccelerationSensor = sensorManager.getDefaultSensor(Sensor.TYPE_LINEAR_ACCELERATION)
   gyroscopeSensor = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE)
   rotationVectorSensor = sensorManager.getDefaultSensor(Sensor.TYPE_ROTATION_VECTOR)
   
   // Verify these are called when streaming starts:
   sensorManager.registerListener(this, linearAccelerationSensor, SENSOR_DELAY_GAME)
   sensorManager.registerListener(this, gyroscopeSensor, SENSOR_DELAY_GAME)
   sensorManager.registerListener(this, rotationVectorSensor, SENSOR_DELAY_GAME)
   ```

3. **Check Watch permissions**:
   - Settings > Apps > Silksong Controller > Permissions
   - Ensure sensor access allowed

**Step 3**: Test again with dashboard
```bash
python data_collection_dashboard.py
```

Look for non-zero values in "LATEST SENSOR DATA" section.

---

## Scenario 5: "Phone buttons don't create files"

**Checklist**:

1. **Verify phone is connected**:
   - Dashboard shows: ✓ CONNECTED (green) for Phone App
   - Phone app shows "Connected" status

2. **Press AND HOLD button** (don't just tap):
   - Press button down
   - Hold for 1-2 seconds
   - Perform gesture on watch
   - Release cleanly (no swipe)

3. **Check dashboard shows recording**:
   - Should show: 🔴 RECORDING: [ACTION]
   - Duration counter increases
   - When released: ✅ READY
   - Statistics counter increments

4. **Check files were created**:
   ```bash
   ls -lh data/button_collected/
   ```
   
   Should show files like:
   ```
   jump_1634567890123_1634567892456.csv
   walk_1634567900000_1634567905000.csv
   ```

5. **If still no files**:
   - Check Python console for error messages
   - Verify `data/button_collected/` directory exists
   - Check disk space

---

## Scenario 6: "Everything works but quality is bad"

**Check sample counts**:
```bash
python src/inspect_csv_data.py data/button_collected/*.csv | grep "Total samples"
```

**Good**: 50-150 samples (1-3 seconds at 50Hz)
**Too few**: < 30 samples (gesture too short)
**Too many**: > 250 samples (gesture too long)

**Tips for better data**:
1. Hold button for 1-3 seconds (not too short, not too long)
2. Complete full gesture motion
3. Record at least 10-30 samples per gesture type
4. Try gesture from different positions/angles
5. Keep motions natural (don't exaggerate)

---

## Scenario 7: "I want to skip the 30s noise capture"

```bash
python data_collection_dashboard.py --skip-noise
```

This:
- Starts collection immediately
- No baseline noise recording
- Good for quick testing
- Not recommended for training data

---

## File Locations

```
v3-watch_SilksongController_25TPE/
├── src/
│   ├── data_collection_dashboard.py   ← Main tool (use this!)
│   ├── button_data_collector.py       ← Original (text-based)
│   ├── inspect_csv_data.py            ← Verify quality
│   └── test_connection.py             ← Test watch only
│
├── data/
│   └── button_collected/              ← Output CSV files
│
├── DASHBOARD_QUICK_START.md           ← Quick start (5 min)
├── DATA_COLLECTION_VERIFICATION.md    ← Troubleshooting (step-by-step)
├── ANDROID_COORDINATION_GUIDE.md      ← How apps work together
└── IMPLEMENTATION_SUMMARY.md          ← What was built
```

---

## Command Cheat Sheet

```bash
# Start dashboard (recommended)
cd src && python data_collection_dashboard.py

# Test watch connection
cd src && python test_connection.py

# Verify CSV quality
cd src && python inspect_csv_data.py ../data/button_collected/*.csv

# Skip noise capture (for testing)
cd src && python data_collection_dashboard.py --skip-noise

# List collected files
ls -lh data/button_collected/

# Count files per gesture
ls data/button_collected/ | grep "^jump" | wc -l
ls data/button_collected/ | grep "^walk" | wc -l
ls data/button_collected/ | grep "^punch" | wc -l
```

---

## Quick Diagnostics

**Question**: Is Watch sending data?
**Answer**: Run `python src/test_connection.py`

**Question**: Is Phone connected?
**Answer**: Check dashboard "CONNECTION STATUS" section

**Question**: Are CSV files good?
**Answer**: Run `python src/inspect_csv_data.py data/button_collected/*.csv`

**Question**: Why are values all zeros?
**Answer**: Watch app problem - rebuild it or check sensors

**Question**: Why no files created?
**Answer**: Phone not connected OR not holding button long enough

**Question**: How many samples do I need?
**Answer**: 10-30 per gesture type for basic training

---

## Success Checklist

Before stopping data collection, verify:

- [x] Dashboard shows both devices **CONNECTED** (green)
- [x] Data rate around **50 Hz** for watch
- [x] Sensor values are **NOT zeros**
- [x] Freshness is **FRESH** (green)
- [x] Recording status changes when buttons pressed/released
- [x] CSV files exist in `data/button_collected/`
- [x] CSV files have size > 1 KB
- [x] Inspector shows **"✅ File contains real sensor data!"**
- [x] At least 10 samples per gesture type

If ALL checkboxes are ticked, your data collection is successful! 🎉
