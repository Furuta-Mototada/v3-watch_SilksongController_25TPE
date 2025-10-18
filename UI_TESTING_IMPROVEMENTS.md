# UI & Testing Improvements - October 19, 2025

## 🎨 Android - Sleek Dark Theme

### New Design Philosophy
Replaced vibrant "goofy" colors with sophisticated dark gradient theme inspired by modern banking apps.

### Dark Color Palette
**Button Backgrounds** (subtle dark variations):
- WALK: `#2C2C2C` (Dark charcoal)
- IDLE: `#2E2E2E` (Dark gray)
- PUNCH: `#3A2B2B` (Dark brown-red)
- JUMP: `#2F2F2F` (Dark neutral)
- TURN_LEFT: `#2A2D2E` (Dark blue-gray)
- TURN_RIGHT: `#302A2E` (Dark purple-gray)

**Accent Colors** (subtle highlights when recording):
- WALK: `#4A90E2` (Soft blue)
- IDLE: `#9B9B9B` (Light gray)
- PUNCH: `#E74C3C` (Soft red)
- JUMP: `#F39C12` (Soft orange)
- TURN_LEFT: `#3498DB` (Light blue)
- TURN_RIGHT: `#E91E63` (Soft pink)

### Visual Features
- **Dark card backgrounds** with minimal elevation (2dp default, 8dp recording)
- **Subtle accent overlay** (20% opacity) when recording
- **Light white text** (90% opacity for labels, 60% for counts)
- **Large minimalist count display** (24sp, Light weight)
- **Smooth transitions** between recording states

### Bottom Action Bar
Two side-by-side buttons in dark theme:

**Connect Button** (Left):
- Dark gray background (`#2C2C2C`)
- Sends test ping to verify connection
- White text with 90% opacity

**Reset Button** (Right):
- Soft red background (`#FF6B6B`)
- Resets all counters
- White text

Both buttons: 50dp height, medium font weight, clean appearance

---

## 🐍 Python - Skip Noise Flag

### New Command Line Option
```bash
python button_data_collector.py --skip-noise
```

### What It Does
- **Skips 30-second baseline noise capture** for faster testing
- **Immediately ready for button presses** after both devices connect
- **No noise segments saved** on exit (useful for quick action testing)

### When To Use
✅ **Use `--skip-noise` when:**
- Testing button app connectivity
- Debugging label event handling
- Quick gesture recording tests
- You already have enough noise samples

❌ **Don't use `--skip-noise` when:**
- Collecting data for training
- Need noise class samples
- Building final dataset

### Implementation Details
```python
class ButtonDataCollector:
    def __init__(self, skip_noise=False):
        self.skip_noise = skip_noise
        self.baseline_noise_captured = skip_noise  # Skip if flag set
```

**Output with flag**:
```
🚀 Collection started!
⚡ SKIP NOISE MODE: Noise capture disabled for testing
✋ Ready for button presses immediately!
```

**Output without flag**:
```
🚀 Collection started!
🔇 DEFAULT STATE: NOISE MODE (all data labeled as noise unless button pressed)
📊 Capturing 30s baseline noise...
```

---

## 📱 New Android Features

### 1. Test Connection Button
- **Location**: Bottom left of screen
- **Function**: Sends test ping to Python backend
- **Feedback**: Updates connection status display
- **Use case**: Verify UDP connectivity before data collection

### 2. Reset Button (Redesigned)
- **Location**: Bottom right of screen
- **Function**: Resets all action counters to 0
- **Style**: Soft red color matching dark theme
- **Size**: Same as Connect button for balance

### 3. ViewModel Addition
```kotlin
fun testConnection() {
    // Send a test ping message to verify connection
    val testMessage = """{"type":"test_ping","timestamp_ms":${System.currentTimeMillis()}}"""
    sendUdpMessage(testMessage)
    connectionStatus.value = "Test ping sent to ${serverIP.value}"
}
```

---

## 🎯 Files Changed

### Android
**File**: `Android_2_Grid/app/src/main/java/com/example/grid_watch_udp_datacollector/MainActivity.kt`
- Lines 245-319: Updated `ActionButton` composable with dark theme
- Lines 97-120: Added bottom action bar with Connect + Reset buttons

**File**: `Android_2_Grid/app/src/main/java/com/example/grid_watch_udp_datacollector/DataCollectorViewModel.kt`
- Lines 141-154: Added `testConnection()` method

### Python
**File**: `src/button_data_collector.py`
- Line 1-13: Updated docstring with `--skip-noise` option
- Line 22: Added `import sys`
- Line 30: Added `skip_noise` parameter to `__init__`
- Line 36: Set `baseline_noise_captured = skip_noise`
- Lines 127-137: Conditional output based on skip_noise flag
- Lines 169-172: Skip noise segmentation if flag set
- Lines 433-440: Parse `--skip-noise` from sys.argv

---

## 🚀 Testing the Updates

### Android App
1. **Rebuild in Android Studio**
2. **Deploy to phone**
3. **Notice the sleek dark theme** - all buttons now dark with subtle differences
4. **Test recording** - see soft accent overlay when holding button
5. **Try Connect button** - verify it sends test ping
6. **Try Reset button** - see all counters go to 0

### Python Script

**Normal mode** (with noise capture):
```bash
cd src
python button_data_collector.py
```

**Skip noise mode** (for testing):
```bash
cd src
python button_data_collector.py --skip-noise
```

### Visual Comparison

**Before**: Bright rainbow colors (blue, purple, orange, yellow, cyan, pink, neon green)
**After**: Sophisticated dark cards (#2C-#30 range) with subtle accent overlays

**Before**: One big pink reset button
**After**: Two balanced buttons (Connect + Reset) in dark/red theme

---

## 🎨 Design Inspiration

The new UI takes inspiration from modern fintech apps:
- **Dark backgrounds** create premium feel
- **Minimal contrast** reduces eye strain
- **Accent colors on interaction** provide subtle feedback
- **Large numbers** prioritize key information
- **Light typography** maintains readability

Similar to the banking app example provided, each card maintains its identity through subtle color variations rather than loud contrasts.

---

## 💡 Usage Tips

**For Quick Testing**:
```bash
# Start Python with skip-noise
python button_data_collector.py --skip-noise

# On phone: Tap "Connect" button to test
# Hold gesture buttons to verify labeling
# No 30-second wait!
```

**For Production Collection**:
```bash
# Start Python normally
python button_data_collector.py

# Wait for 30s baseline noise
# Then collect labeled gestures
# Ctrl+C saves everything including noise segments
```

---

## ✅ What's Fixed

✅ Android UI now has sophisticated dark theme (not goofy)
✅ Reset button visible and styled to match
✅ Connect button added for testing
✅ Python script accepts `--skip-noise` flag
✅ Faster testing workflow without noise capture
✅ Clean modern aesthetic matching banking apps

Enjoy the sleek new look! 🌙
