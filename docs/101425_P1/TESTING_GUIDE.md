# Testing Guide: Pixel Watch Automatic Connection

## Prerequisites Checklist

Before you begin, ensure you have:

- ✅ **Pixel Watch 1** (Wear OS device)
- ✅ **Mac computer** (your development machine)
- ✅ **Same WiFi network** - Both devices must be connected to the same local network
- ✅ **USB cable** (for initial app installation)
- ✅ **Android Studio** installed on Mac
- ✅ **Python 3.x** installed on Mac
- ✅ **ADB (Android Debug Bridge)** configured

---

## Phase 1: Mac Setup (Python Host)

### Step 1.1: Install Python Dependencies

Open Terminal and navigate to your project directory:

```bash
cd /Users/cvk/Downloads/CODELocalProjects/v3-watch_SilksongController_25TPE
```

Install the required `zeroconf` library:

```bash
pip install -r requirements.txt
```

Or install it directly:

```bash
pip install zeroconf>=0.131.0
```

**Verify installation:**
```bash
python -c "import zeroconf; print('zeroconf version:', zeroconf.__version__)"
```

Expected output: `zeroconf version: 0.131.0` (or higher)

### Step 1.2: Verify Network Configuration

Check your Mac's IP address:

```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

**Example output:**
```
inet 192.168.1.100 netmask 0xffffff00 broadcast 192.168.1.255
```

Note down this IP address (e.g., `192.168.1.100`). You'll use it for manual fallback testing.

### Step 1.3: Test Zeroconf Service Registration

Before running the full app, test if service registration works:

```bash
python -c "
import socket
from zeroconf import ServiceInfo, Zeroconf
print('Starting zeroconf test...')
zc = Zeroconf()
info = ServiceInfo(
    '_silksong._udp.local.',
    'Test._silksong._udp.local.',
    addresses=[socket.inet_aton('$(ipconfig getifaddr en0)')],
    port=12345,
    properties={'version': '1.0'}
)
zc.register_service(info)
print('✅ Service registered successfully!')
print('Service name: Test._silksong._udp.local.')
print('Press Ctrl+C to stop...')
import time
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print('\nUnregistering service...')
    zc.unregister_service(info)
    zc.close()
    print('✅ Test complete!')
"
```

**Expected output:**
```
Starting zeroconf test...
✅ Service registered successfully!
Service name: Test._silksong._udp.local.
Press Ctrl+C to stop...
```

Press `Ctrl+C` to stop the test.

### Step 1.4: Check Firewall Settings

Ensure your Mac's firewall allows UDP traffic:

1. Open **System Preferences** → **Security & Privacy** → **Firewall**
2. If firewall is ON, click **Firewall Options**
3. Ensure "Block all incoming connections" is **NOT** checked
4. Add Python to allowed apps if prompted

---

## Phase 2: Pixel Watch Setup (Android Client)

### Step 2.1: Enable Developer Mode on Pixel Watch

1. On your Pixel Watch, go to **Settings** → **System** → **About**
2. Tap **Build number** 7 times until you see "You are now a developer!"
3. Go back to **Settings** → **Developer options**
4. Enable **ADB debugging**
5. Enable **Debug over Wi-Fi** (important for wireless testing)

### Step 2.2: Connect Watch to Mac via USB

1. Connect your Pixel Watch to Mac using USB cable
2. On your Mac, open Terminal and verify ADB connection:

```bash
adb devices
```

**Expected output:**
```
List of devices attached
1234567890ABCDEF	device
```

If you see "unauthorized", check your watch for an authorization prompt and approve it.

### Step 2.3: Verify Watch WiFi Connection

Check that your watch is on the same WiFi as your Mac:

```bash
adb shell dumpsys wifi | grep "mWifiInfo"
```

Look for the SSID (network name) and verify it matches your Mac's network.

### Step 2.4: Build and Install the App

Open Android Studio:

1. **Open Project**: Navigate to the `Android/` folder
2. Wait for Gradle sync to complete
3. **Select Device**: In the device dropdown, select your connected Pixel Watch
4. **Build & Run**: Click the green play button (▶️)

**Alternative: Command Line Installation**

```bash
cd Android
./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

**Verify installation:**
```bash
adb shell pm list packages | grep silksong
```

Expected output: `package:com.cvk.silksongcontroller`

---

## Phase 3: The First Connection Test

### Step 3.1: Start the Python Host

In your Mac Terminal, start the UDP listener:

```bash
cd /Users/cvk/Downloads/CODELocalProjects/v3-watch_SilksongController_25TPE/src
python udp_listener.py
```

**What to look for:**
```
🎮 Silksong Motion Controller v3 🎮
📡 Listening on 0.0.0.0:12345
🔍 Advertising service: SilksongController._silksong._udp.local.
   IP: 192.168.1.100
   Port: 12345

Waiting for data...
```

**✅ SUCCESS INDICATOR**: You should see the "Advertising service" message with your Mac's IP.

### Step 3.2: Launch the Watch App

On your Pixel Watch:

1. Open the app drawer (press the crown)
2. Find "Silksong Controller" app
3. Tap to launch

**Alternative: Launch via ADB**
```bash
adb shell am start -n com.cvk.silksongcontroller/.MainActivity
```

### Step 3.3: Watch the Connection Sequence

**ON YOUR WATCH**, observe the UI transitions:

1. **Initial State** (0-2 seconds):
   - Status: 🟠 "Searching..."
   - Color: Orange
   - Switch: Disabled

2. **Discovery Phase** (2-5 seconds):
   - NSD is scanning for `_silksong._udp.local.` service
   - Progress indicator may be visible

3. **Connected State** (should happen within 5 seconds):
   - Status: 🟢 "Connected!"
   - Color: Green
   - IP Address field auto-fills with Mac's IP (e.g., `192.168.1.100`)
   - Switch: **Enabled**

**ON YOUR MAC**, check the Python terminal for:
```
[Connection] Service discovered by client
```

### Step 3.4: Test Data Streaming

On your Pixel Watch:

1. Toggle the **"Stream"** switch to **ON**
2. Move your wrist around

**ON YOUR MAC**, you should see data packets:

```
📦 Received from 192.168.1.50:
{
  "timestamp": 1697234567890,
  "accel": {"x": 0.23, "y": -0.45, "z": 9.81},
  "gyro": {"x": 0.01, "y": 0.02, "z": -0.01}
}

📦 Received from 192.168.1.50:
{
  "timestamp": 1697234567990,
  "accel": {"x": 0.25, "y": -0.43, "z": 9.79},
  "gyro": {"x": 0.03, "y": 0.04, "z": -0.02}
}
```

**✅ SUCCESS**: You're seeing real-time sensor data from your watch!

---

## Phase 4: Comprehensive Testing

### Test 4.1: Automatic Reconnection

**Purpose**: Verify the system can recover from disconnection.

**Steps:**
1. With streaming active, **stop** the Python script (Ctrl+C)
2. **Watch status** should change to 🔴 "Connection Lost"
3. **Restart** the Python script
4. **Watch status** should automatically return to 🟢 "Connected!" within 5-10 seconds

**Expected behavior**: Automatic rediscovery without manual intervention.

### Test 4.2: Manual IP Fallback

**Purpose**: Test the fallback mechanism when automatic discovery fails.

**Steps:**
1. Stop the Python script
2. On the watch, tap the **IP Address field**
3. Enter your Mac's IP manually: `192.168.1.100` (use your actual IP)
4. Tap "Save"
5. Start the Python script
6. Toggle streaming ON

**Expected behavior**: Manual connection should work even without NSD.

### Test 4.3: Network Resilience

**Purpose**: Test behavior across different network scenarios.

**Scenario A: WiFi Interference**
1. Move away from the router (weak signal)
2. Observe connection stability
3. Check for dropped packets in Python terminal

**Scenario B: Network Switch**
1. Disconnect watch from WiFi
2. Reconnect to the same network
3. Watch should rediscover automatically

### Test 4.4: Multi-Device Testing (if available)

**Purpose**: Verify single-server, single-client model.

**Steps:**
1. If you have another Android device, install the app
2. Start Python script
3. Launch app on both devices
4. Observe that only one can stream at a time

---

## Phase 5: Debugging Tools

### Tool 5.1: ADB Logcat (Real-Time Android Logs)

Monitor watch logs in real-time:

```bash
adb logcat | grep -E "Silksong|NSD|zeroconf"
```

**Key log messages to look for:**

```
D/SilksongController: Starting service discovery...
D/NsdManager: discoverServices: _silksong._udp.
D/SilksongController: onServiceFound: SilksongController._silksong._udp.local.
D/SilksongController: Service resolved: 192.168.1.100:12345
I/SilksongController: ✅ Connected to host!
```

### Tool 5.2: Network Traffic Monitor

Verify UDP packets are being sent:

```bash
sudo tcpdump -i en0 -n udp port 12345
```

You should see packets when streaming is active:

```
192.168.1.50.54321 > 192.168.1.100.12345: UDP, length 256
192.168.1.50.54321 > 192.168.1.100.12345: UDP, length 256
```

### Tool 5.3: Service Discovery Verification (Mac)

Verify your Mac is advertising the service:

```bash
dns-sd -B _silksong._udp
```

**Expected output:**
```
Browsing for _silksong._udp
Timestamp     A/R  Flags  if Domain   Service Type         Instance Name
14:23:45.123  Add     2   4 local.    _silksong._udp.      SilksongController
```

### Tool 5.4: Check Python Process

Verify the Python script is running and listening:

```bash
lsof -i UDP:12345
```

**Expected output:**
```
COMMAND   PID  USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
Python    1234 cvk    3u  IPv4  0x...      0t0  UDP *:12345
```

---

## Troubleshooting Quick Reference

### ❌ "Searching..." Never Completes

**Symptoms:** Watch stays on "Searching..." indefinitely.

**Diagnostics:**
```bash
# On Mac - check if service is advertising
dns-sd -B _silksong._udp

# On Watch - check NSD logs
adb logcat | grep NSD
```

**Solutions:**
1. Verify both devices are on **same WiFi network**
2. Restart Python script
3. Check firewall isn't blocking multicast traffic
4. Use manual IP as fallback

### ❌ Python Script Fails to Start

**Symptoms:** `zeroconf` import error or socket binding error.

**Diagnostics:**
```bash
# Check if zeroconf is installed
pip list | grep zeroconf

# Check if port is already in use
lsof -i :12345
```

**Solutions:**
```bash
# Install zeroconf
pip install zeroconf

# Kill process using port 12345
kill -9 $(lsof -t -i:12345)
```

### ❌ No Data Received on Mac

**Symptoms:** Watch shows "Connected!" but Mac receives no packets.

**Diagnostics:**
```bash
# Monitor UDP traffic
sudo tcpdump -i en0 -n udp port 12345 -v
```

**Solutions:**
1. Toggle streaming switch OFF then ON
2. Check watch sensors are working: `adb shell dumpsys sensorservice`
3. Verify UDP socket code in `MainActivity.kt`

### ❌ App Crashes on Launch

**Symptoms:** App closes immediately after opening.

**Diagnostics:**
```bash
# Get crash logs
adb logcat | grep -E "AndroidRuntime|FATAL"
```

**Common causes:**
1. Missing permissions in `AndroidManifest.xml`
2. Null pointer in `MainActivity.kt`
3. Incompatible Android version

**Solution:**
```bash
# Reinstall app
adb uninstall com.cvk.silksongcontroller
./gradlew installDebug
```

---

## Success Criteria Checklist

You've successfully completed Phase 1 testing when:

- [ ] **Python script starts** without errors and advertises service
- [ ] **Watch app launches** and shows "Searching..." status
- [ ] **Automatic discovery** completes within 5 seconds
- [ ] **Status changes** from 🟠 "Searching..." to 🟢 "Connected!"
- [ ] **IP address** auto-fills in the watch UI
- [ ] **Stream switch** becomes enabled
- [ ] **Data packets** appear in Python terminal when streaming
- [ ] **Manual IP entry** works as fallback
- [ ] **Reconnection** works after Python script restart

---

## What You Can Do Next

### Experiment 1: Sensor Data Visualization

Add real-time graphing to the Python script:

```bash
pip install matplotlib
```

Modify `udp_listener.py` to plot acceleration data.

### Experiment 2: Gesture Recognition Prep

Start collecting training data:

1. Enable streaming
2. Perform specific gestures (punch, kick, jump)
3. Label the data in the Python script
4. Save to CSV for machine learning in Phase 2

### Experiment 3: Latency Measurement

Measure round-trip latency:

1. Add timestamp to watch data
2. Compute difference between send time and receive time
3. Log in Python terminal

Example:
```python
latency = time.time() * 1000 - data['timestamp']
print(f"⏱️  Latency: {latency:.1f}ms")
```

### Experiment 4: Connection Quality Metrics

Monitor connection health:

```bash
# Watch packet rate
watch -n 1 'netstat -an | grep 12345'

# Watch packet loss
# (Compare sent packets on watch vs received on Mac)
```

---

## Next Phase Preview

Once all success criteria are met, you're ready for **Phase 2: Sensor Data Acquisition & Calibration**, where we'll:

1. Implement sensor fusion algorithms
2. Build a calibration routine for watch orientation
3. Create gesture detection pipelines
4. Establish data collection for ML training

---

## Quick Start Cheat Sheet

**Every time you want to test:**

```bash
# Terminal 1: Start Python host
cd /Users/cvk/Downloads/CODELocalProjects/v3-watch_SilksongController_25TPE/src
python udp_listener.py

# Terminal 2: Monitor logs (optional)
adb logcat | grep Silksong
```

**On Pixel Watch:**
1. Launch "Silksong Controller" app
2. Wait for "Connected!" (🟢)
3. Toggle "Stream" switch ON
4. Move wrist to generate data

**Stop streaming:**
- Toggle switch OFF on watch
- Press Ctrl+C in Python terminal

---

## Support Resources

- **Android NSD Docs**: https://developer.android.com/training/connect-devices-wirelessly/nsd
- **Zeroconf Python**: https://python-zeroconf.readthedocs.io/
- **ADB Reference**: https://developer.android.com/studio/command-line/adb
- **Wear OS Debugging**: https://developer.android.com/training/wearables/apps/debugging

---

**Ready to test? Start with Phase 1, Step 1.1! 🚀**
