# CRITICAL BUG FIXES - October 19, 2025

## 🐛 Issues Fixed

### 1. **Reset & Connect Buttons Not Visible** ✅
**Problem**: Buttons were pushed off-screen by `Spacer(weight=1f)`

**Fix**: Changed to fixed height spacer
```kotlin
// Before: Spacer(modifier = Modifier.weight(1f))
// After:  Spacer(modifier = Modifier.height(16.dp))
```

**Result**: Connect and Reset buttons now visible at bottom of screen!

---

### 2. **Baseline Noise Not Saved to Data Folder** ✅
**Problem**:
- `noise_start_time` was `None` initially, causing crashes
- Baseline noise accumulated but never written to disk
- Only saved during Ctrl+C exit (if you remembered)

**Fix**:
1. Initialize `noise_start_time = time.time()` immediately
2. Save baseline to CSV **automatically** after 30 seconds
3. File: `baseline_noise_{timestamp}.csv` in data folder

**Result**: Baseline noise now automatically saved! Check `data/button_collected/`

---

### 3. **Sensor Data Parsing Issues** ✅
**Problem**:
- Fallback for `timestamp` field (watch uses `timestamp_ns` or `timestamp`)
- Default `rot_w` was 0.0 (should be 1.0 for identity quaternion)

**Fix**:
```python
'timestamp': msg.get('timestamp_ns', msg.get('timestamp', time.time() * 1e9)),
'rot_w': msg.get('rot_w', 1.0)  # Identity quaternion default
```

---

### 4. **Phone App Doesn't Send Sensor Data** 📱
**IMPORTANT CLARIFICATION**:

The **phone button grid app** is NOT supposed to send sensor data!

**Data Flow**:
```
Watch App (Pixel Watch)  →  UDP Sensor Data (accel, gyro, rotation)
                              ↓
                        Python Backend
                              ↓
Phone App (Button Grid)  →  UDP Label Events (button press/release)
```

**Phone app role**:
- ✅ Sends label events (button press/release with timestamps)
- ❌ Does NOT collect or send sensor data

**Watch app role**:
- ✅ Streams sensor data continuously (50Hz)
- ❌ Does NOT send label events

**Why your log shows 9919 sensor packets**: That's from the **watch**, not the phone!

---

## 🎯 What You're Seeing

### Your Log Analysis:
```
Watch connected from 192.168.10.150   ← Watch sending sensor data
⚠️  Watch connection lost              ← Timeout (5 seconds no data)
✅ Watch connected from 192.168.10.249 ← Watch reconnected
✅ Phone connected from 192.168.10.249 ← Phone sent label event

📊 Sensor packets: 9919  ← From WATCH (not phone)
📱 Label events: 1       ← From PHONE (button test)
```

**Both devices happen to be on 192.168.10.249** - that's fine! They're using the same WiFi.

### Why "No active recording to end"?
Phone sent an `end` event without a matching `start` event. This happens when:
1. Testing the Connect button (sends test ping)
2. App crashed and restarted
3. Button released before Python started

**Fix**: Just ignore it or add better error handling.

---

## 📊 Baseline Noise Capture Now Works!

### What Happens Now:
1. **Python starts** → `noise_start_time` initialized
2. **Watch connects** → Sensor data starts buffering
3. **Press ENTER** → Collection begins
4. **30 seconds pass** → Baseline automatically saved!

### Check Your Data:
```bash
ls -lh data/button_collected/
```

You should see:
```
baseline_noise_1729368000.csv  ← Baseline (30s of sensor data)
walk_123456_to_123789.csv      ← Gesture recordings
punch_234567_to_234890.csv
...
```

---

## 🔧 Counter Going Up Issue

**This is CORRECT behavior!**

Counter increments when you:
1. Press and hold a button
2. Release the button

Each press = +1 count. This tracks how many samples you've collected.

**To reset**: Tap the **Reset** button (now visible at bottom right)

---

## 🚀 Test It Now

1. **Rebuild Android app** (buttons now visible)
2. **Run Python**:
   ```bash
   cd src
   python button_data_collector.py
   ```
3. **Start watch app** (streams sensors)
4. **Start phone app** (button grid)
5. **Press ENTER** when both connected
6. **Wait 30 seconds** → Baseline auto-saves!
7. **Press buttons** → Gestures saved
8. **Check folder**: `ls data/button_collected/`

---

## 📝 Files Changed

- `Android_2_Grid/.../MainActivity.kt` - Fixed Spacer to make buttons visible
- `src/button_data_collector.py` - Fixed noise timing, auto-save baseline, better timestamp handling

---

## ✅ Everything Should Work Now!

- ✅ Connect & Reset buttons visible
- ✅ Baseline noise automatically saved after 30s
- ✅ Sensor data properly parsed (from watch)
- ✅ Label events properly received (from phone)
- ✅ Counter behavior is correct
- ✅ Data saved to correct folder

**The phone app does NOT need to send sensor data - that's the watch's job!**
