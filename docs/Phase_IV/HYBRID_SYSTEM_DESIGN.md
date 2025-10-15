# Hybrid System Design Document

## Problem Statement

Based on live testing feedback, the ML-only controller exhibits two critical issues:

1. **Latency**: Sliding window inference causes 500ms+ lag between gesture and action
2. **Misclassification**: ML occasionally mistakes critical gestures (e.g., jump misclassified as noise)

### User Feedback Analysis

**Critical Issues:**
- "Jump feels sluggish - I fall into pits before the controller reacts"
- "Sometimes my punch doesn't register at all"
- "The ML is smart but too slow for fast-paced gameplay"

### Root Causes

1. **Sliding Window Latency**:
   - Requires 2.5 seconds of buffered data
   - Prediction runs every 0.5 seconds
   - Total delay: 500-750ms from gesture start to action

2. **Feature Extraction Overhead**:
   - Computing 60+ features takes 10-15ms
   - SVM prediction takes 20-30ms
   - Combined: 30-45ms per prediction

3. **Lack of World-Coordinate Transformation**:
   - Features are computed in device-local coordinates
   - Same gesture in different orientations produces different features
   - ML struggles with orientation invariance

## Solution: Hybrid Dual-Layer Architecture

### Design Philosophy

**"Reflexes for Survival, Intelligence for Strategy"**

The hybrid system combines:
- **Reflex Layer**: Instant (<50ms) responses for survival actions
- **ML Layer**: Intelligent (500ms) decisions for complex patterns

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    SENSOR INPUT STREAM                       │
│              (Linear Accel, Gyro, Rotation)                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Split into parallel paths
                       │
        ┌──────────────┴──────────────┐
        │                              │
        ▼                              ▼
┌──────────────────┐          ┌──────────────────┐
│  REFLEX LAYER    │          │    ML LAYER      │
│  (Threshold)     │          │  (Intelligent)   │
└─────────┬────────┘          └────────┬─────────┘
          │                            │
          │ <50ms latency              │ ~500ms latency
          │ 80-85% accuracy            │ 85-95% accuracy
          │                            │
          ▼                            ▼
    ┌─────────┐                  ┌─────────┐
    │  Jump   │                  │  Turn   │
    │  Attack │                  │ Complex │
    └────┬────┘                  └────┬────┘
         │                            │
         └────────────┬───────────────┘
                      │
                      ▼
              ┌───────────────┐
              │   EXECUTION   │
              │   ARBITRATOR  │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │  GAME INPUT   │
              └───────────────┘
```

### Layer Responsibilities

#### Reflex Layer (Threshold-Based)

**Purpose**: Instant response for critical survival actions

**Handles**:
- Jump detection (vertical acceleration)
- Attack detection (forward punch motion)

**Characteristics**:
- Latency: <50ms
- Accuracy: 80-85%
- World-coordinate transformation applied
- No machine learning overhead

**Detection Logic**:
```python
# Transform acceleration to world coordinates
world_accel = rotate_vector_by_quaternion(device_accel, quaternion)

# Jump: Strong upward acceleration in world Z-axis
if world_accel[2] > JUMP_THRESHOLD:
    execute_jump()

# Attack: Forward punch in current facing direction
if abs(world_accel[0]) > ATTACK_THRESHOLD and stable_stance:
    execute_attack()
```

#### ML Layer (SVM-Based)

**Purpose**: Intelligent recognition of complex patterns

**Handles**:
- Turn detection (requires orientation history)
- Gesture disambiguation (complex patterns)
- Future: Combo moves, special techniques

**Characteristics**:
- Latency: ~500ms
- Accuracy: 85-95%
- Context-aware predictions
- Confidence scoring

**Detection Logic**:
```python
# Collect 2.5s window
if buffer_full and time_elapsed > PREDICTION_INTERVAL:
    features = extract_window_features(buffer)
    prediction, confidence = ml_model.predict(features)
    
    # Only execute non-critical actions
    if prediction == "turn" and confidence > 0.70:
        execute_turn()
```

### Execution Arbitrator

**Purpose**: Coordinate between reflex and ML layers

**Rules**:
1. **Priority**: Reflex layer has priority for jump/attack
2. **Non-interference**: ML layer only handles turn/complex gestures
3. **Redundancy**: Both layers can trigger same action (filtered)
4. **Cooldowns**: Prevent duplicate actions within 300ms

```python
class ExecutionArbitrator:
    def __init__(self):
        self.last_action_time = {}
        self.cooldown = 0.3  # seconds
    
    def execute(self, action, source):
        now = time.time()
        last_time = self.last_action_time.get(action, 0)
        
        # Check cooldown
        if now - last_time < self.cooldown:
            return False
        
        # Execute action
        perform_keyboard_action(action)
        self.last_action_time[action] = now
        return True
```

## Implementation Plan

### Phase 1: World-Coordinate Transformation

**File**: `src/feature_extractor.py`

Add world-coordinate transformation to feature extraction:

```python
def extract_window_features(window_df):
    """Extract features with world-coordinate transformation."""
    features = {}
    
    # Separate by sensor type
    accel = window_df[window_df['sensor'] == 'linear_acceleration']
    rot = window_df[window_df['sensor'] == 'rotation_vector']
    
    # NEW: Transform acceleration to world coordinates
    if len(accel) > 0 and len(rot) > 0:
        # Match each accel reading with closest rotation
        for idx, accel_row in accel.iterrows():
            # Find closest rotation reading
            closest_rot = rot.iloc[(rot.index - idx).abs().argmin()]
            
            # Transform to world coordinates
            device_accel = [
                accel_row['accel_x'],
                accel_row['accel_y'],
                accel_row['accel_z']
            ]
            quaternion = {
                'x': closest_rot['rot_x'],
                'y': closest_rot['rot_y'],
                'z': closest_rot['rot_z'],
                'w': closest_rot['rot_w']
            }
            
            world_accel = rotate_vector_by_quaternion(device_accel, quaternion)
            
            # Add world-coordinate features
            accel.loc[idx, 'world_accel_x'] = world_accel[0]
            accel.loc[idx, 'world_accel_y'] = world_accel[1]
            accel.loc[idx, 'world_accel_z'] = world_accel[2]
        
        # Extract features from world coordinates
        for axis in ['world_accel_x', 'world_accel_y', 'world_accel_z']:
            values = accel[axis].dropna()
            if len(values) > 0:
                features[f'{axis}_mean'] = values.mean()
                features[f'{axis}_std'] = values.std()
                features[f'{axis}_max'] = values.max()
                # ... more features
    
    # Continue with existing features
    # ...
```

### Phase 2: Reflex Layer Implementation

**File**: `src/udp_listener.py`

Add reflex detection alongside ML:

```python
# Reflex thresholds (world coordinates)
REFLEX_JUMP_THRESHOLD = 15.0  # m/s² upward in world Z
REFLEX_ATTACK_THRESHOLD = 12.0  # m/s² forward in world X/Y
REFLEX_STABILITY_THRESHOLD = 5.0  # m/s² for stable stance

def detect_reflex_actions(accel_values, rotation_quaternion):
    """Fast threshold-based detection in world coordinates."""
    
    # Transform to world coordinates
    device_accel = [
        accel_values.get('x', 0),
        accel_values.get('y', 0),
        accel_values.get('z', 0)
    ]
    world_accel = rotate_vector_by_quaternion(device_accel, rotation_quaternion)
    
    # Jump: Strong upward motion in world Z
    if world_accel[2] > REFLEX_JUMP_THRESHOLD:
        return 'jump', world_accel[2] / REFLEX_JUMP_THRESHOLD
    
    # Attack: Forward motion with stable base
    forward_mag = math.sqrt(world_accel[0]**2 + world_accel[1]**2)
    if (forward_mag > REFLEX_ATTACK_THRESHOLD and 
        abs(world_accel[2]) < REFLEX_STABILITY_THRESHOLD):
        return 'attack', forward_mag / REFLEX_ATTACK_THRESHOLD
    
    return None, 0.0

# In main loop:
if sensor_type == "linear_acceleration":
    # Try reflex detection first
    reflex_action, confidence = detect_reflex_actions(
        parsed_json.get("values", {}),
        last_known_orientation
    )
    
    if reflex_action:
        arbitrator.execute(reflex_action, 'reflex')
```

### Phase 3: ML Layer Scope Reduction

**File**: `src/udp_listener.py`

Restrict ML to complex gestures only:

```python
# ML prediction (runs every 0.5s)
if ML_ENABLED and time_for_prediction:
    prediction, confidence = ml_predict(buffer)
    
    # Only handle complex gestures via ML
    if prediction in ['turn'] and confidence > ML_CONFIDENCE_THRESHOLD:
        arbitrator.execute(prediction, 'ml')
```

### Phase 4: Configuration Updates

**File**: `config.json`

Add hybrid system configuration:

```json
{
  "hybrid_system": {
    "enabled": true,
    "reflex_layer": {
      "jump_threshold": 15.0,
      "attack_threshold": 12.0,
      "stability_threshold": 5.0
    },
    "ml_layer": {
      "confidence_threshold": 0.70,
      "prediction_interval": 0.5,
      "gestures": ["turn"]
    },
    "arbitrator": {
      "cooldown_seconds": 0.3
    }
  }
}
```

## Performance Targets

### Latency Improvements

| Action  | Before (ML-only) | After (Hybrid) | Improvement |
|---------|------------------|----------------|-------------|
| Jump    | 500-750ms        | <50ms          | 90% faster  |
| Attack  | 500-750ms        | <50ms          | 90% faster  |
| Turn    | 500-750ms        | 500ms (ML)     | Unchanged   |

### Accuracy Targets

| Action  | Reflex Layer | ML Layer | Combined |
|---------|--------------|----------|----------|
| Jump    | 80-85%       | 85-95%   | 95%+     |
| Attack  | 80-85%       | 85-95%   | 95%+     |
| Turn    | N/A          | 85-95%   | 85-95%   |

**Combined Accuracy**: Both layers can trigger actions, providing redundancy

## Testing Strategy

### Unit Tests

```python
def test_world_coordinate_transformation():
    """Verify quaternion rotation produces correct world coordinates."""
    # Device pointing up, punch forward
    device_accel = [10, 0, 0]
    quaternion = {'x': 0, 'y': 0, 'z': 0, 'w': 1}
    world_accel = rotate_vector_by_quaternion(device_accel, quaternion)
    assert abs(world_accel[0] - 10) < 0.01

def test_reflex_jump_detection():
    """Verify jump detection in world coordinates."""
    accel = {'x': 0, 'y': 0, 'z': 20}
    quat = {'x': 0, 'y': 0, 'z': 0, 'w': 1}
    action, conf = detect_reflex_actions(accel, quat)
    assert action == 'jump'
    assert conf > 1.0
```

### Integration Tests

1. **Latency Test**: Measure time from gesture to action
   - Target: <50ms for reflex actions
   - Method: High-speed video + timestamp logging

2. **Accuracy Test**: Count correct detections vs false positives
   - Target: >95% for critical actions
   - Method: 100 gestures per action type

3. **Arbitrator Test**: Verify no duplicate actions
   - Target: 0 duplicates within cooldown window
   - Method: Rapid gesture repetition

## Rollout Plan

### Stage 1: Feature Addition (No Breaking Changes)
- Add world-coordinate transformation to feature extraction
- Retrain ML model with new features
- Deploy updated models

### Stage 2: Reflex Layer (Additive)
- Implement reflex detection alongside ML
- Both systems run in parallel
- Monitor performance metrics

### Stage 3: Optimization (Refinement)
- Tune reflex thresholds based on user data
- Adjust ML confidence thresholds
- Optimize arbitrator cooldowns

### Stage 4: Documentation
- Update user guides with hybrid system explanation
- Add troubleshooting for threshold tuning
- Create performance comparison charts

## Fallback Strategy

If hybrid system has issues:

1. **Disable Reflex Layer**: Set `hybrid_system.enabled = false` in config
2. **ML-Only Mode**: System falls back to current behavior
3. **Threshold-Only Mode**: If ML fails, reflex layer provides basic functionality

## Success Criteria

✅ Jump latency reduced from 500ms to <50ms
✅ Attack latency reduced from 500ms to <50ms
✅ Overall accuracy maintained or improved (>85%)
✅ Zero performance regression on turn detection
✅ Smooth gameplay experience confirmed by user testing

## Future Enhancements

- **Adaptive Thresholds**: Learn optimal thresholds per user
- **Combo Detection**: ML layer recognizes multi-gesture sequences
- **Predictive Reflex**: Anticipate actions based on ML context
- **Gesture Confidence**: Reflex layer reports confidence scores

---

**Status**: Design Complete - Ready for Implementation
**Next Step**: Implement world-coordinate transformation in feature extraction
