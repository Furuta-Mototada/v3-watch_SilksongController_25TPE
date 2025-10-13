# Quick Test Guide - Fixed UI Issues

## What Was Fixed

### 1. **Missing UI Elements (Streaming Switch)**
**Problem**: The switch was hidden off-screen on the small watch display.

**Solution**:
- Replaced `ConstraintLayout` with `BoxInsetLayout` (Wear OS optimized)
- Added `NestedScrollView` for scrolling on small screens
- Reduced font sizes and padding for watch display
- Reordered UI: Connection status → **Stream switch** → IP config → Sensors

### 2. **Wear OS Warning**
**Problem**: "missing uses-feature watch" warning

**Solution**:
- Added Wear OS dependencies to `build.gradle.kts`
- Added `standalone` metadata to `AndroidManifest.xml`
- Already had `android.hardware.type.watch` feature declared

---

## New UI Layout (Top to Bottom)

```
┌─────────────────────────┐
│  🟢 Connected!          │  ← Status (Orange/Green/Red)
├─────────────────────────┤
│  [Stream] ○             │  ← MAIN SWITCH (now visible!)
├─────────────────────────┤
│  IP: 192.168.1.100      │  ← Current IP
├─────────────────────────┤
│  Manual IP:             │
│  [192.168.1.100] [Save] │  ← Manual override
├─────────────────────────┤
│  Sensor Status:         │
│  Step: Ready            │  ← Abbreviated
│  Accel: Ready           │
│  Rotation: Ready        │
│  Gyro: Ready            │
└─────────────────────────┘
   (scroll if needed)
```

---

## How to Test RIGHT NOW

### Step 1: Start Python Server

```bash
# Terminal 1
cd /Users/cvk/Downloads/CODELocalProjects/v3-watch_SilksongController_25TPE/src
python udp_listener.py
```

**Look for:**
```
🎮 Silksong Motion Controller v3 🎮
📡 Listening on 0.0.0.0:12345
🔍 Advertising service...
```

### Step 2: Launch Watch App

On your Pixel Watch:
1. **Swipe up** or **press crown** to open apps
2. Find **"Silksong Controller"**
3. **Tap to launch**

OR via ADB:
```bash
~/Library/Android/sdk/platform-tools/adb -s adb-2B081JEEJW01VK-p2asqI._adb-tls-connect._tcp shell am start -n com.cvk.silksongcontroller/.MainActivity
```

### Step 3: Watch the Connection

**ON WATCH:**
- Status should change: 🟠 "Searching..." → 🟢 "Connected!"
- IP field auto-fills
- **YOU SHOULD NOW SEE THE STREAM SWITCH!**

### Step 4: Start Streaming

**ON WATCH:**
1. **Toggle the "Stream" switch to ON**
2. You may see a permission prompt → **Allow**
3. Toast message: "Streaming ON"

**ON MAC (Python terminal):**
You should see JSON data:
```json
{"sensor": "gyroscope", "timestamp_ns": 1234567890, "values": {"x": 0.01, "y": 0.02, "z": -0.01}}
{"sensor": "linear_acceleration", "timestamp_ns": 1234567891, "values": {"x": 0.23, "y": -0.45, "z": 9.81}}
{"sensor": "rotation_vector", "timestamp_ns": 1234567892, "values": {"x": 0.1, "y": 0.2, "z": 0.3, "w": 0.9}}
{"sensor": "step_detector", "timestamp_ns": 1234567893}
```

### Step 5: Verify Streaming

**Move your wrist around** - you should see the values changing in real-time!

---

## Troubleshooting

### "I still don't see the switch!"

**Try:**
1. **Scroll down** on the watch (swipe up from bottom)
2. Force close and reopen the app
3. Check if the app updated:
   ```bash
   ~/Library/Android/sdk/platform-tools/adb -s adb-2B081JEEJW01VK-p2asqI._adb-tls-connect._tcp shell pm dump com.cvk.silksongcontroller | grep versionCode
   ```

### "No data in Python terminal"

**Check:**
1. Is the switch actually ON? (Should see "Streaming ON" toast)
2. Are you on the same WiFi network?
3. Watch logcat for errors:
   ```bash
   ~/Library/Android/sdk/platform-tools/adb -s adb-2B081JEEJW01VK-p2asqI._adb-tls-connect._tcp logcat | grep Silksong
   ```

### "Connection Lost" immediately

**Check:**
1. Python script is running
2. Firewall isn't blocking UDP port 12345
3. Try manual IP entry as fallback

---

## What You Can Do Now

### Test All Sensors

1. **Gyroscope**: Rotate your wrist → see `gyroscope` values change
2. **Accelerometer**: Move wrist up/down → see `linear_acceleration` values
3. **Rotation Vector**: Tilt watch → see `rotation_vector` orientation
4. **Step Detector**: Walk around → see `step_detector` events

### Monitor Packet Rate

In Python terminal, watch how fast data arrives:
- **Gyro/Accel**: ~50-100 packets/second (SENSOR_DELAY_GAME)
- **Step Detector**: Only when you take a step
- **All combined**: ~200-300 packets/second when moving

### Test Reconnection

1. Stop Python script (Ctrl+C)
2. Watch should show "Connection Lost" (🔴)
3. Restart Python script
4. Watch should auto-reconnect within 5-10 seconds
5. **No need to toggle the switch!**

---

## Expected Behavior Summary

| Action | Watch Display | Python Terminal |
|--------|---------------|-----------------|
| App launch | "Searching..." (🟠) | No change |
| NSD discovery | "Connected!" (🟢) | "Service discovered" |
| Toggle ON | "Streaming ON" toast | Start receiving JSON |
| Move wrist | Switch stays ON | Values update |
| Toggle OFF | "Streaming OFF" toast | Stop receiving data |
| Stop Python | "Connection Lost" (🔴) | Process exits |
| Restart Python | Auto-reconnects to 🟢 | "Advertising service..." |

---

## Success Criteria ✅

You've successfully completed the test when:

- [x] **App installs** without Wear OS warnings
- [x] **Switch is visible** on the watch screen
- [x] **Auto-connection works** (status → Connected!)
- [x] **Toggle switch ON** shows "Streaming ON"
- [x] **Python receives data** (JSON packets appear)
- [x] **All 4 sensors** send data when moving
- [x] **Toggle switch OFF** stops the data stream

---

## Next Steps

Once streaming works perfectly:

1. **Collect gesture data** (Phase 2)
2. **Build calibration routine** (normalize sensor values)
3. **Train ML model** (gesture recognition)
4. **Map to Silksong controls** (punch, jump, walk)

---

## Files Changed in This Fix

```
Android/app/src/main/res/layout/activity_main.xml
  - Replaced ConstraintLayout with BoxInsetLayout
  - Added NestedScrollView for scrolling
  - Reduced font sizes for watch display
  - Reordered UI elements for better UX

Android/app/build.gradle.kts
  - Added androidx.wear:wear:1.3.0
  - Added wearable dependencies

Android/app/src/main/AndroidManifest.xml
  - Added standalone metadata
  - Already had watch feature declaration
```

---

**Ready to stream! 🚀**

Try it now and report back what you see on your watch and in your Python terminal!
