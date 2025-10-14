# Phase II: Data Collection Implementation Checklist

## Pre-Collection Verification

### Hardware Setup
- [ ] Wear OS watch is charged (>50% battery)
- [ ] Watch is securely fastened to wrist
- [ ] Watch app is installed and launches successfully
- [ ] Both devices (watch + computer) are on the same Wi-Fi network
- [ ] `network_utils.py` has detected and updated the correct IP address

### Software Configuration
- [ ] `data_collector.py` contains **all 14 gesture definitions**
- [ ] `GESTURES` dictionary includes:
  - [ ] 1 × `punch_forward` (TARGET class: PUNCH)
  - [ ] 1 × `jump_quick` (TARGET class: JUMP)
  - [ ] 1 × `turn_body` (TARGET class: TURN)
  - [ ] 1 × `walk_in_place` (TARGET class: WALK)
  - [ ] 1 × `rest` (BASELINE class: REST)
  - [ ] 9 × `noise_*` gestures (CRITICAL class: NOISE)
- [ ] `SAMPLES_PER_GESTURE` is set to `40`
- [ ] `RECORDING_DURATION_SEC` is set to `2.5` (or your preferred duration)
- [ ] Color class (`Colors`) is defined with GREEN, RED, YELLOW, BLUE, RESET, BOLD

### Environment Setup
- [ ] Clear physical space of at least 2m × 2m
- [ ] Water bottle is within reach
- [ ] Comfortable clothing allows free movement
- [ ] No distractions (phone on silent, door closed)

---

## Connection Verification

### Initial Test
- [ ] Run `python data_collector.py` (or `python3 data_collector.py`)
- [ ] Script displays colored welcome message
- [ ] Script shows comprehensive protocol overview with sample counts
- [ ] Press Enter to proceed to connection check

### Connection Check Phase
- [ ] Script displays: `CONNECTION CHECK` in yellow
- [ ] Watch app is open with **streaming toggle ON**
- [ ] Real-time countdown appears: `⏳ Waiting for data... X.Xs remaining`
- [ ] Within 15 seconds, message changes to: `✓ Connection verified! Receiving sensor data.` (GREEN)

### If Connection Fails
- [ ] Error message displays in RED with troubleshooting steps
- [ ] Verify watch app is streaming (toggle should be ON)
- [ ] Verify both devices are on same network
- [ ] Check `config.json` has correct `listen_ip`
- [ ] Restart watch app and try again

---

## Data Collection Execution

### For Each Gesture Type (14 total)

#### Before Recording
- [ ] Script displays stance instructions in colored box
- [ ] Read the stance description carefully
- [ ] Adopt the correct physical stance
- [ ] Press Enter when ready

#### During Each Sample (40 per gesture)
- [ ] Script displays gesture name and description in yellow
- [ ] Read the specific execution instructions
- [ ] Press Enter when ready to record
- [ ] Countdown appears: `3... 2... 1...` in yellow
- [ ] Message displays: `🔴 RECORDING - EXECUTE GESTURE NOW!` in bold red
- [ ] **Execute the gesture immediately and deliberately**
- [ ] Watch the real-time recording status:
  ```
  ⏱️  Recording: 1.8s | ✓ CONNECTED | 📊 125 pts (69 pts/s)
  ```
- [ ] Verify connection stays **GREEN** (✓ CONNECTED) throughout
- [ ] Recording completes automatically after set duration
- [ ] Script displays: `✓ Recording complete!` in green
- [ ] Script shows data point count (should be >50 for 2.5s at 20Hz)

#### After Each Sample
- [ ] If data count is low (<50), connection warning appears
- [ ] Choose to retry the sample if prompted
- [ ] Take a brief pause to return to stance (2 seconds)
- [ ] Repeat for all 40 samples

#### Between Gestures
- [ ] Script displays: `✓ Gesture complete! Take a short break if needed.`
- [ ] Take a break if fatigued (quality > speed!)
- [ ] Press Enter to continue to next gesture or 'q' to quit

---

## Quality Control During Collection

### Watch for These Signs of Good Data
- ✅ Data rate consistently >40 pts/s during recording
- ✅ Connection indicator stays GREEN throughout
- ✅ Each sample file shows >50 data points
- ✅ Gestures feel consistent and repeatable

### Warning Signs (Stop and Troubleshoot)
- ❌ Connection indicator turns RED during recording
- ❌ Data rate drops below 30 pts/s
- ❌ "No data recorded" warnings after multiple samples
- ❌ You're feeling fatigued or sloppy with gestures

---

## Post-Collection Verification

### Immediate Checks
- [ ] Script displays final summary in green
- [ ] Summary confirms total samples collected
- [ ] Summary shows output directory path
- [ ] No error messages during cleanup

### File System Verification
Navigate to the output directory (e.g., `training_data/session_YYYYMMDD_HHMMSS/`)

#### Count Files
```bash
cd training_data/session_YYYYMMDD_HHMMSS/
ls -1 *.csv | wc -l
# Expected: 560 files (14 gestures × 40 samples)
```

#### Verify File Naming
- [ ] TARGET class files exist:
  - `punch_forward_sample01.csv` through `punch_forward_sample40.csv`
  - `jump_quick_sample01.csv` through `jump_quick_sample40.csv`
  - `turn_body_sample01.csv` through `turn_body_sample40.csv`
  - `walk_in_place_sample01.csv` through `walk_in_place_sample40.csv`

- [ ] BASELINE class files exist:
  - `rest_sample01.csv` through `rest_sample40.csv`

- [ ] NOISE class files exist (9 types × 40 samples = 360 files):
  - `noise_cough_sample01.csv` through `noise_cough_sample40.csv`
  - `noise_scratch_sample01.csv` through `noise_scratch_sample40.csv`
  - `noise_stretch_sample01.csv` through `noise_stretch_sample40.csv`
  - `noise_typing_sample01.csv` through `noise_typing_sample40.csv`
  - `noise_drinking_sample01.csv` through `noise_drinking_sample40.csv`
  - `noise_phone_sample01.csv` through `noise_phone_sample40.csv`
  - `noise_check_watch_sample01.csv` through `noise_check_watch_sample40.csv`
  - `noise_partial_punch_sample01.csv` through `noise_partial_punch_sample40.csv`
  - `noise_fidget_sample01.csv` through `noise_fidget_sample40.csv`

#### Spot Check File Contents
Open a random sample file (e.g., `punch_forward_sample15.csv`):

- [ ] File is not empty (>0 bytes)
- [ ] File contains CSV header row with columns like:
  - `timestamp`, `sensor`, `gesture`, `stance`, `sample`
  - `rot_x`, `rot_y`, `rot_z`, `rot_w` (for rotation_vector)
  - `accel_x`, `accel_y`, `accel_z` (for linear_acceleration)
  - `gyro_x`, `gyro_y`, `gyro_z` (for gyroscope)
- [ ] File contains >50 data rows (for 2.5s recording at 20Hz)
- [ ] `gesture` column matches filename (e.g., "punch_forward")
- [ ] `sample` column shows correct sample number

```bash
# Quick check command:
head punch_forward_sample15.csv
wc -l punch_forward_sample15.csv
# Should show >50 lines (excluding header)
```

---

## Critical Success Criteria

### PASS Conditions
To proceed to Phase III (Model Training), ALL of the following must be true:

1. **File Count:** Exactly **560 CSV files** in the session directory
2. **Class Balance:** Each gesture type has exactly **40 samples**
3. **Noise Class:** All **9 noise gesture types** are present with full sample counts
4. **File Integrity:** Random spot checks show no empty or corrupted files
5. **Data Density:** Files contain >50 data points per 2.5s recording
6. **Metadata Accuracy:** `gesture`, `stance`, and `sample` fields are correctly labeled

### FAIL Conditions (Re-collect Required)
- ❌ Missing any gesture types (<14 types present)
- ❌ Unbalanced samples (some gestures have <40 samples)
- ❌ Missing or incomplete Noise class
- ❌ Multiple corrupted files or connection issues during collection
- ❌ Files show very low data density (<30 points per file)

---

## Troubleshooting Common Issues

### "Connection Lost" During Recording
**Cause:** Watch app paused or Wi-Fi interruption
**Solution:**
1. Check watch app is still open and streaming
2. Verify Wi-Fi connection on both devices
3. Restart watch app if needed
4. Re-collect the affected sample

### Low Data Point Count
**Cause:** Sensor sampling rate too low or packet loss
**Solution:**
1. Move closer to Wi-Fi router
2. Close other apps on watch to reduce load
3. Restart watch if performance is degraded
4. Consider increasing `RECORDING_DURATION_SEC` to 3.0

### Fatigue During Long Session
**Solution:**
1. This is NORMAL - collection takes 45-60 minutes
2. Take breaks between gesture types (script allows this)
3. Drink water frequently
4. If too fatigued, quit gracefully and resume later
5. The script saves files incrementally - partial sessions are not lost

---

## Post-Collection Next Steps

Once all criteria pass:

1. **Backup Your Data**
   ```bash
   cp -r training_data/session_YYYYMMDD_HHMMSS ~/backup_location/
   ```

2. **Document Your Session**
   - Note any observations about difficult gestures
   - Record any deviations from protocol
   - Save notes for the Discussion section of your paper

3. **Proceed to Phase III**
   - Open `CS156_Silksong_Watch.ipynb` (to be created)
   - Begin ML pipeline implementation
   - Start with data loading and verification

---

**Checklist Version:** 1.0
**Last Updated:** October 14, 2025
**Status:** Ready for execution
