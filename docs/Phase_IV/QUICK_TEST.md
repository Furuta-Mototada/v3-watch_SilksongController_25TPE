# Quick Test: ML-Powered Controller

## Pre-Flight Checklist

✅ **Models Trained**
```bash
ls models/gesture_classifier.pkl models/feature_scaler.pkl models/feature_names.pkl
```

✅ **Dependencies Installed**
```bash
pip install joblib scikit-learn scipy pandas numpy
```

✅ **Smartwatch Connected**
- Android app running
- Watch on wrist
- UDP connection established

---

## Test Procedure

### 1. Start the Controller

```bash
cd src
python udp_listener.py
```

**Expected Output:**
```
🔍 Auto-detecting IP address...
✓ IP address configured: 192.168.x.x
--- Silksong Controller v2.0 (HYBRID (Reflex + ML)) ---
Listening on 192.168.x.x:5005
✓ Hybrid System Active
  Reflex Layer: Jump & Attack (<50ms latency)
  ML Layer: Turn & Complex Gestures (~500ms)
  Reflex Cooldown: 0.3s
Official Hollow Knight/Silksong key mappings:
  Movement: a/d (direction-based)
  Jump: z | Attack: x
---------------------------------------
```

**Mode Indicators:**
- `(HYBRID (Reflex + ML))` - Full hybrid system active (best performance)
- `(ML-POWERED)` - ML-only mode (if hybrid disabled in config)
- `(THRESHOLD-BASED)` - Legacy mode (if model files missing)

---

### 2. Test Each Gesture

In **Hybrid Mode**, gestures are handled by different layers:

#### **Jump Test** (Reflex Layer)
- **Action**: Quick upward flick of wrist
- **Expected**: `[REFLEX] JUMP`
- **Keyboard**: Z key press
- **Latency**: Should feel instant (<50ms)
- **Note**: World-coordinate transformation makes this work in any orientation

#### **Attack Test** (Reflex Layer)
- **Action**: Forward punch motion (stable stance)
- **Expected**: `[REFLEX] ATTACK`
- **Keyboard**: X key press
- **Latency**: Should feel instant (<50ms)
- **Note**: Requires stable base (not jumping)

#### **Turn Test** (ML Layer)
- **Action**: Rotate wrist 180° horizontally
- **Expected**: `[ML] TURN` with confidence
- **Result**: `Facing:` changes from RIGHT to LEFT
- **Latency**: ~500ms delay (normal for ML)
- **Confidence**: Should be >0.70 for smooth turns

#### **Walk Test** (Legacy System)
- **Action**: Natural walking steps
- **Expected**: `Walk:` changes to WALKING
- **Fuel Bar**: `[####----]` fills with each step
- **Note**: Walking uses step detector, independent of hybrid system

---

### 3. Confidence Monitoring

Watch the confidence values for each prediction:

```
[ML] JUMP (0.85)    ← Strong prediction
[ML] ATTACK (0.72)  ← Threshold level
[ML] TURN (0.68)    ← Borderline (may not execute)
```

**Ideal Ranges:**
- Jump: 0.75-0.95
- Attack: 0.70-0.90
- Turn: 0.65-0.85

---

### 4. False Positive Check

Perform non-gesture movements and verify they're ignored:

- Adjust watch band → Should see no predictions
- Scratch nose → Should see no predictions
- Fidget with hand → Should see no predictions

If false positives occur frequently, increase confidence threshold:
```python
ML_CONFIDENCE_THRESHOLD = 0.75  # Was 0.70
```

---

### 5. Response Time Test

Measure the delay between gesture and action:

1. Perform a jump gesture
2. Count: "one-thousand-one"
3. Action should occur before you finish counting

**Target**: <0.5 seconds from gesture start to key press

If too slow, reduce prediction interval:
```python
PREDICTION_INTERVAL = 0.3  # Was 0.5
```

---

## Validation Checklist

- [ ] Jump gesture detected with >75% confidence
- [ ] Attack gesture detected with >70% confidence
- [ ] Turn gesture changes direction reliably
- [ ] Walking fuel system works correctly
- [ ] No false positives during normal movements
- [ ] Response time <0.5 seconds
- [ ] Console shows `(ML-POWERED)` mode

---

## Common Issues & Fixes

### Issue: Low Confidence Scores

**Symptoms:** All predictions below 0.60

**Fixes:**
1. Perform more exaggerated gestures
2. Check watch is snug on wrist
3. Verify you're using the same stance as training (combat/neutral/travel)
4. Retrain model with more varied samples

### Issue: No Predictions Appearing

**Symptoms:** No `[ML]` messages in console

**Fixes:**
1. Check sensor buffer is filling: Add debug print after line 398
   ```python
   print(f"Buffer size: {len(sensor_buffer)}")
   ```
2. Verify smartwatch is sending data (dashboard should update)
3. Check prediction interval hasn't been set too high

### Issue: Wrong Gestures Detected

**Symptoms:** Jump detected as attack, etc.

**Fixes:**
1. Collect more training data for confused gestures
2. Retrain model with cleaner samples
3. Check sensor calibration on smartwatch
4. Verify feature extraction function matches training

---

## Performance Benchmarks

### Good Performance
```
[ML] JUMP (0.88)     ← Clean detection
[ML] ATTACK (0.79)   ← Good confidence
[ML] TURN (0.71)     ← Acceptable
```

### Poor Performance
```
[ML] JUMP (0.52)     ← Below threshold, ignored
[ML] ATTACK (0.45)   ← Way too low
[ML] TURN (0.39)     ← Model uncertain
```

If seeing poor performance:
1. Retrain with more samples (40+ per gesture minimum)
2. Verify sensor data quality in training set
3. Check for sensor hardware issues

---

## Next Steps After Successful Test

1. **Test in-game**: Open Hollow Knight and perform gestures
2. **Tune responsiveness**: Adjust confidence and interval for gameplay
3. **Collect edge cases**: Note any missed gestures and retrain
4. **Document patterns**: Which gestures work best for your movement style

---

## Emergency Fallback

If ML system is unreliable, force threshold mode:

```bash
mv models models_backup
python udp_listener.py
```

You'll see:
```
--- Silksong Controller v2.0 (THRESHOLD-BASED) ---
⚠️  ML model files not found
   Running in threshold-based mode (legacy)
```

This uses hardcoded thresholds instead of ML predictions.

---

**Ready to test? Start the controller and begin with Jump!** 🎮
