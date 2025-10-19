# Quick Start - Testing Connection Fixes

## What Was Fixed

1. **Python Script**: Now checks connection BEFORE recording starts
2. **Android App**: Auto-fill button for IP address + better auto-discovery

## How to Test

### Step 1: Test Python Connection Check

```bash
cd /Users/cvk/Downloads/CODELocalProjects/v3-watch_SilksongController_25TPE/src

# Quick connection test (doesn't record, just checks)
python test_connection.py

# Or test with actual data collector
python continuous_data_collector.py --duration 60 --session test_connection
```

**What you should see:**
```
📱 Checking watch connection...
⏳ Waiting for data... 12.5s remaining | 3 packets received
✅ Connection verified! Received 3 valid packets from watch
```

### Step 2: Rebuild Android App (For IP Input Fix)

**Option A: Using Android Studio**
1. Open project: `Android/` folder
2. Build → Rebuild Project
3. Run → Run 'app' → Select your Pixel Watch
4. Wait for installation

**Option B: Using Gradle (Command Line)**
```bash
cd /Users/cvk/Downloads/CODELocalProjects/v3-watch_SilksongController_25TPE/Android
./gradlew assembleDebug
# APK will be in: app/build/outputs/apk/debug/app-debug.apk
# Install manually or via Android Studio
```

### Step 3: Test Auto-Fill Button

1. Open watch app
2. Wait 5-10 seconds for auto-discovery
3. Status should show: "✅ Connected!"
4. IP field should auto-fill with your computer's IP
5. If IP field is empty or wrong:
   - Tap "📡 Use Auto-Detected IP" button
   - IP should fill automatically
   - Tap "Save" to confirm

### Step 4: Full End-to-End Test

```bash
# Terminal 1: Start Python data collector
cd src
python continuous_data_collector.py --duration 60 --session full_test

# Watch:
# 1. Open app
# 2. Wait for "✅ Connected!" status
# 3. Toggle streaming ON

# Terminal 1 (should now show):
# ✅ Connection verified! Received 3 valid packets from watch
# 🎤 Microphone will start recording in 3 seconds...
# 🔴 RECORDING STARTED
```

## Expected Behavior

### Python Script
✅ **Before recording:**
- Shows "Checking watch connection..."
- Waits up to 15 seconds for data
- Shows live packet count
- Only starts recording if connection verified

❌ **Old behavior:**
- Started recording immediately
- No connection check
- Confusing "no data" warnings during recording

### Android App
✅ **Auto-discovery working:**
- Shows "🔍 Searching for server..."
- Changes to "✅ Connected!" when found
- IP auto-fills in input field
- IP auto-saved to preferences

✅ **Auto-discovery fails / No period key:**
- Shows "❌ Discovery failed - use manual IP"
- User taps "📡 Use Auto-Detected IP" button
- If IP was detected earlier, it fills automatically
- Otherwise, shows "Waiting for discovery" message

❌ **Old behavior:**
- No auto-fill option
- Manual entry required period key
- No way to use auto-discovered IP

## Troubleshooting

### "Connection timeout - no packets received"

**Check:**
1. Watch app is open and streaming is ON
2. Watch shows "✅ Connected!" (green)
3. Both devices on same WiFi network
4. Run test script: `python test_connection.py`

### "Auto-fill button says 'Waiting for discovery'"

**Solutions:**
1. Wait 10-15 seconds for auto-discovery to complete
2. Check computer is running NSD server (udp_listener.py or data collector)
3. Restart watch app
4. Enter IP manually using numeric keyboard only:
   - Type: `192168010235` (no periods)
   - Then edit to add periods if keyboard appears
   - Or use auto-fill once discovery works

### "Still can't type period on watch"

**Workaround:**
1. Wait for auto-discovery to find IP
2. Tap "📡 Use Auto-Detected IP" button
3. IP fills automatically
4. Tap "Save"
5. Done! ✨

**Alternative:**
1. Find your computer's IP: Run `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
2. On another device (phone), send IP via message/email to yourself
3. Copy IP from phone notification to watch
4. Paste in watch app

## Files Changed

### Python
- ✅ `src/continuous_data_collector.py` - Added connection check
- ✅ `src/test_connection.py` - New diagnostic tool

### Android (Need to rebuild!)
- ✅ `Android/app/src/main/java/.../MainActivity.kt` - Auto-fill + better NSD
- ✅ `Android/app/src/main/res/layout/activity_main.xml` - Auto-fill button

### Documentation
- ✅ `docs/CONNECTION_FIXES_101725.md` - Full explanation

## Next Steps

1. **Test Python script** - Verify connection check works
2. **Rebuild Android app** - Get auto-fill button on watch
3. **Test end-to-end** - Full recording with watch
4. **Collect data** - Start Phase V data collection! 🎮

## Quick Reference

**Computer IP (your current):** 192.168.10.235
**Port:** 12345

**Test Command:**
```bash
cd src
python test_connection.py
```

**Data Collection Command:**
```bash
cd src
python continuous_data_collector.py --duration 600 --session game_01
```

---

Everything is ready to go! 🚀
