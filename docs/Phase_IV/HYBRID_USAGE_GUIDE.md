# Hybrid System Usage Guide

## Quick Start

### 1. Enable Hybrid Mode

Edit `config.json`:

```json
{
  "hybrid_system": {
    "enabled": true
  }
}
```

### 2. Start Controller

```bash
cd src
python udp_listener.py
```

Look for:
```
--- Silksong Controller v2.0 (HYBRID (Reflex + ML)) ---
✓ Hybrid System Active
  Reflex Layer: Jump & Attack (<50ms latency)
  ML Layer: Turn & Complex Gestures (~500ms)
```

### 3. Test Gestures

**Jump** (Reflex):
- Quick upward wrist flick
- Should see: `[REFLEX] JUMP`
- Instant response

**Attack** (Reflex):
- Forward punch with stable base
- Should see: `[REFLEX] ATTACK`
- Instant response

**Turn** (ML):
- Rotate wrist 180°
- Should see: `[ML] TURN`
- ~500ms delay (normal)

---

## Configuration Tuning

### Adjust Reflex Sensitivity

**Too Sensitive** (false positives):
```json
{
  "reflex_layer": {
    "jump_threshold": 18.0,      // Increase (was 15.0)
    "attack_threshold": 15.0,    // Increase (was 12.0)
    "cooldown_seconds": 0.4      // Increase (was 0.3)
  }
}
```

**Not Sensitive Enough** (missed gestures):
```json
{
  "reflex_layer": {
    "jump_threshold": 12.0,      // Decrease
    "attack_threshold": 10.0,    // Decrease
    "cooldown_seconds": 0.2      // Decrease
  }
}
```

### Disable Hybrid Mode

To use ML-only or test without reflex layer:

```json
{
  "hybrid_system": {
    "enabled": false
  }
}
```

Controller will fall back to ML-only mode.

---

## Understanding the Layers

### Reflex Layer

**What it does:**
- Transforms acceleration to world coordinates
- Checks simple thresholds
- Executes actions immediately

**When to use:**
- Critical survival actions (jump, attack)
- Fast-paced gameplay
- When latency matters most

**Limitations:**
- Lower accuracy than ML (80-85%)
- Simple patterns only
- No context awareness

### ML Layer

**What it does:**
- Collects 2.5 seconds of sensor data
- Extracts 60+ features
- Predicts with SVM model
- Confidence scoring

**When to use:**
- Complex patterns (turn)
- Nuanced gestures
- When accuracy matters most

**Limitations:**
- ~500ms latency
- Requires model files
- Higher CPU usage

### Execution Arbitrator

**What it does:**
- Prevents duplicate actions
- Enforces cooldown periods
- Coordinates between layers

**Configuration:**
```json
{
  "reflex_layer": {
    "cooldown_seconds": 0.3  // Adjust if needed
  }
}
```

**How it works:**
```
Time: 0.0s  → Jump triggered (reflex)
Time: 0.1s  → Jump triggered (ML) → BLOCKED (cooldown)
Time: 0.4s  → Jump triggered (user) → ALLOWED (cooldown expired)
```

---

## Troubleshooting

### Issue: Jump Not Working

**Check:**
1. Hybrid enabled in config?
2. Gesture is upward motion in world coordinates?
3. Threshold too high?

**Fix:**
```json
{
  "reflex_layer": {
    "jump_threshold": 12.0  // Lower from 15.0
  }
}
```

### Issue: Attack Not Working

**Check:**
1. Stable base (not jumping)?
2. Forward motion magnitude?
3. Z-axis stability?

**Fix:**
```json
{
  "reflex_layer": {
    "attack_threshold": 10.0,      // Lower
    "stability_threshold": 7.0     // Increase tolerance
  }
}
```

### Issue: Turn Not Working

**Possible Causes:**
- ML model not loaded
- Insufficient rotation angle
- Low confidence

**Check Console:**
```
[ML] TURN
  Confidence: 0.65  ← Below 0.70 threshold
```

**Fix:**
```json
{
  "ml_layer": {
    "confidence_threshold": 0.60  // Lower from 0.70
  }
}
```

### Issue: Too Many False Positives

**Solution 1: Increase Thresholds**
```json
{
  "reflex_layer": {
    "jump_threshold": 18.0,
    "attack_threshold": 15.0
  }
}
```

**Solution 2: Increase Cooldown**
```json
{
  "reflex_layer": {
    "cooldown_seconds": 0.5  // From 0.3
  }
}
```

---

## Performance Monitoring

### Enable Debug Output

Add to `udp_listener.py` (temporary):

```python
# In detect_reflex_actions()
print(f"World Accel: X={world_accel[0]:.2f}, Y={world_accel[1]:.2f}, Z={world_accel[2]:.2f}")
```

**Watch for:**
- Jump: Z > 15.0
- Attack: sqrt(X² + Y²) > 12.0 AND |Z| < 5.0

### Measure Latency

Use high-speed video:
1. Record yourself performing gesture
2. Note frame when gesture starts
3. Note frame when action executes
4. Calculate: latency = (action_frame - gesture_frame) / fps

**Target:**
- Reflex: <50ms (3 frames at 60fps)
- ML: ~500ms (30 frames at 60fps)

---

## Best Practices

### 1. Calibrate Per User

Each user has different gesture patterns:
- Test all gestures
- Adjust thresholds based on personal style
- Save user-specific config files

### 2. Test in Stages

**Stage 1:** Test reflex layer only
```json
{"hybrid_system": {"enabled": true}}
```

**Stage 2:** Add ML layer
- Verify both layers work independently
- Check for conflicts/duplicates

**Stage 3:** Tune arbitrator
- Adjust cooldown as needed
- Monitor for duplicates

### 3. Profile Performance

```bash
# In separate terminal
top -p $(pgrep -f udp_listener.py)
```

**Watch:**
- CPU usage: Should be <30%
- Memory: Should be <200MB
- If high: Reduce prediction_interval

---

## Advanced Configuration

### Custom Gesture Mapping

Map reflex actions to different keys:

```json
{
  "keyboard_mappings": {
    "jump": "space",      // Instead of 'z'
    "attack": "c"         // Instead of 'x'
  }
}
```

### ML Layer Gesture Selection

Choose which gestures ML handles:

```json
{
  "ml_layer": {
    "gestures": ["turn", "punch"]  // Add punch to ML
  }
}
```

**Note:** This requires code modification in `udp_listener.py`

### Multiple Configurations

Create configs for different scenarios:

```bash
config_normal.json      # Balanced settings
config_aggressive.json  # Low thresholds, fast response
config_conservative.json # High thresholds, fewer false positives
```

Load with:
```bash
cp config_aggressive.json config.json
python udp_listener.py
```

---

## Migration from ML-Only

### Step 1: Test Compatibility

Run with hybrid disabled first:
```json
{"hybrid_system": {"enabled": false}}
```

Verify ML-only mode still works.

### Step 2: Enable Hybrid Gradually

Start with conservative thresholds:
```json
{
  "reflex_layer": {
    "jump_threshold": 18.0,    // High threshold
    "attack_threshold": 15.0,
    "cooldown_seconds": 0.5    // Long cooldown
  }
}
```

### Step 3: Tune to Preference

Gradually lower thresholds until comfortable.

---

## FAQ

**Q: Can I use reflex-only mode?**

A: Not directly, but you can set ML confidence very high:
```json
{"ml_layer": {"confidence_threshold": 0.99}}
```

**Q: Why is jump faster than attack?**

A: Both use reflex layer and should be equally fast. If attack feels slow, check stability_threshold.

**Q: Can I add more gestures to reflex layer?**

A: Yes! Modify `detect_reflex_actions()` in `udp_listener.py`. See `HYBRID_SYSTEM_DESIGN.md` for examples.

**Q: Does hybrid work without ML models?**

A: Yes! Reflex layer works independently. ML layer fails gracefully.

**Q: How do I know which layer triggered an action?**

A: Check console output:
- `[REFLEX] JUMP` - Reflex layer
- `[ML] TURN` - ML layer

---

**For more details, see:**
- `HYBRID_SYSTEM_DESIGN.md` - Architecture documentation
- `README.md` - System overview
- `QUICK_TEST.md` - Testing procedures
