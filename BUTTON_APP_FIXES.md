# Button Data Collection App - Critical Fixes Applied

## Date: October 19, 2025

## Issues Fixed

### 1. **Button Stuck in Pressed State** ✅
**Problem**: Button remained highlighted after release, UI frozen
**Root Cause**: `tryAwaitRelease()` was blocking without checking return value
**Fix**: Added proper release handling:
```kotlin
val released = tryAwaitRelease()
if (released) {
    viewModel.onButtonReleased(action)
    onVibrate(100)
}
```

### 2. **Connection Detection Not Working** ✅
**Problem**: "Connect" button didn't register phone connection
**Root Cause**: Python script only detected `label_event` messages, but "Connect" sent `test_ping`
**Fix**:
- Android: Changed test message to `label_event` with `event: "ping"`
- Python: Added ping handler that updates `last_phone_data` timestamp

### 3. **CSV Format Mismatch** ✅
**Problem**: Old training data has different column order
**Expected Format**:
```csv
accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,rot_w,rot_x,rot_y,rot_z,sensor,timestamp
```
**Fix**: Updated both `save_recording()` and `_save_noise_segment()` to match old format

### 4. **Empty Gyro/Rotation Data** ✅
**Problem**: Watch sends `linear_acceleration` but Python expected flat JSON fields
**Watch JSON Format**:
```json
{
  "sensor": "linear_acceleration",
  "timestamp_ns": 123456789,
  "values": {"x": -0.10, "y": -0.14, "z": 0.29}
}
```
**Fix**: Updated Python parser to handle both nested `values` object and flat fields:
```python
values = msg.get('values', {})
if msg.get('sensor') == 'linear_acceleration':
    accel_x = values.get('x', msg.get('accel_x', 0.0))
    # ... etc for all sensors
```

## Testing Checklist

### Android App (Rebuild Required)
- [ ] Button press/release works smoothly (no sticking)
- [ ] "Connect" button shows "Connected" status
- [ ] Button counts increment correctly
- [ ] Vibration feedback works on press/release

### Python Backend (Restart Required)
- [ ] Watch connection detected on startup
- [ ] Phone connection detected when pressing "Connect"
- [ ] Sensor data shows all three types:
  - `linear_acceleration` → accel_x/y/z
  - `gyroscope` → gyro_x/y/z
  - `rotation_vector` → rot_x/y/z/w
- [ ] CSV files match old format (column order)
- [ ] No empty gyro/rotation columns

### Data Collection Workflow
1. Start Python: `python src/button_data_collector.py`
2. Start watch app (enable streaming)
3. Launch phone button app
4. Press "Connect" → Should show both devices connected
5. Press ENTER to start collection
6. Wait 30s for baseline noise
7. Press/hold buttons to collect gestures
8. Check CSV files have all sensor data populated

## Files Modified

### Android (Rebuild in Android Studio)
- `Android_2_Grid/app/src/main/java/com/example/grid_watch_udp_datacollector/MainActivity.kt`
  - Fixed button gesture detector
- `Android_2_Grid/app/src/main/java/com/example/grid_watch_udp_datacollector/DataCollectorViewModel.kt`
  - Changed test connection message format

### Python (Restart Service)
- `src/button_data_collector.py`
  - Fixed sensor data parsing (nested values)
  - Added ping handler for connection test
  - Fixed CSV column order (2 places)

## Next Steps

1. **Rebuild Android App**: Open `Android_2_Grid` in Android Studio and rebuild
2. **Restart Python**: Kill and restart `button_data_collector.py`
3. **Verify Watch App**: Ensure it's streaming all 3 sensors (accel, gyro, rotation)
4. **Test Full Workflow**: Follow testing checklist above
5. **Collect Data**: Record 10+ samples per gesture class

## Watch App Verification

If still seeing empty gyro/rotation data, verify watch app is registering all sensors:
```kotlin
// Check MainActivity.kt onCreate():
linearAccelerationSensor = sensorManager.getDefaultSensor(Sensor.TYPE_LINEAR_ACCELERATION)
gyroscopeSensor = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE)
rotationVectorSensor = sensorManager.getDefaultSensor(Sensor.TYPE_ROTATION_VECTOR)

// Check registerListener() calls when streaming starts
sensorManager.registerListener(this, linearAccelerationSensor, SENSOR_DELAY_GAME)
sensorManager.registerListener(this, gyroscopeSensor, SENSOR_DELAY_GAME)
sensorManager.registerListener(this, rotationVectorSensor, SENSOR_DELAY_GAME)
```
