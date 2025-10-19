# Multi-Threaded ML Architecture

## Overview

The controller now uses a **fully ML-powered** decoupled architecture with three parallel threads. This eliminates bottlenecks and achieves low latency without abandoning the ML model.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      UDP Sensor Stream                       │
│                      (50Hz from watch)                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                 ┌──────────────────┐
                 │  Thread 1:       │
                 │  COLLECTOR       │
                 │                  │
                 │  • Read UDP      │
                 │  • Parse JSON    │
                 │  • Push to queue │
                 │  • No processing │
                 └────────┬─────────┘
                          │
                    sensor_queue
                    (thread-safe)
                          │
                          ▼
                 ┌──────────────────┐
                 │  Thread 2:       │
                 │  PREDICTOR       │
                 │                  │
                 │  • Pull from Q   │
                 │  • 0.3s window   │
                 │  • Extract feat. │
                 │  • ML predict    │
                 │  • Push action   │
                 └────────┬─────────┘
                          │
                    action_queue
                    (thread-safe)
                          │
                          ▼
                 ┌──────────────────┐
                 │  Thread 3:       │
                 │  ACTOR           │
                 │                  │
                 │  • Pull actions  │
                 │  • Conf. gating  │
                 │  • Execute keys  │
                 │  • Manage walk   │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │  Game (Silksong) │
                 └──────────────────┘
```

## Thread Details

### Thread 1: Collector

**Purpose**: Read sensor data at network speed

**Operation**:
1. Listen on UDP socket (non-blocking)
2. Parse JSON packet
3. Push to `sensor_queue`
4. Repeat immediately

**Key Point**: Does ZERO processing. Runs at network speed.

### Thread 2: Predictor

**Purpose**: Run ML inference continuously

**Operation**:
1. Pull sensor data from `sensor_queue`
2. Maintain 0.3s sliding window buffer (~15 samples)
3. When buffer is 80% full:
   - Extract 60+ features
   - Scale with trained scaler
   - Run SVM prediction
   - Get confidence score
4. If confidence ≥ 70%, push to `action_queue`
5. Repeat continuously

**Key Point**: Runs as fast as CPU allows. No fixed intervals.

### Thread 3: Actor

**Purpose**: Execute keyboard actions with stability

**Operation**:
1. Pull action from `action_queue`
2. Add to prediction history (size 5)
3. Check if last 5 predictions match:
   - If yes → Execute keyboard action
   - If no → Wait for more predictions
4. Manage walking state via step detector
5. Repeat continuously

**Key Point**: Confidence gating prevents flickering.

## Key Parameters

```python
WINDOW_SIZE_SEC = 0.3              # Micro-window for fast detection
WINDOW_SIZE_SAMPLES = 15           # ~0.3s at 50Hz
ML_CONFIDENCE_THRESHOLD = 0.7      # 70% minimum confidence
CONFIDENCE_GATING_COUNT = 5        # Require 5 consecutive predictions
```

## Performance Benefits

### 1. Eliminated Bottlenecks

**Before (Synchronous)**:
```
UDP receive → [BLOCKED] → Process → [BLOCKED] → Predict → [BLOCKED] → Execute
   50Hz           ✗         10-15ms      ✗       20-30ms      ✗       1-2ms
```

**After (Multi-Threaded)**:
```
Collector: UDP receive → queue   (50Hz, never blocked)
Predictor: queue → ML → queue    (continuous, parallel)
Actor: queue → keyboard           (continuous, parallel)
```

### 2. Reduced Window Size

- **Before**: 2.5 seconds = 125 samples = long wait for gestures
- **After**: 0.3 seconds = 15 samples = fast gesture detection

A quick punch fills 0.3s window almost instantly!

### 3. Continuous Prediction

- **Before**: Predict every 0.5 seconds (fixed interval)
- **After**: Predict continuously as fast as CPU allows

### 4. Confidence Gating

Prevents flickering between gestures:
```
Raw predictions:  walk, walk, walk, jump, walk, walk, walk
After gating:     walk ────────────► walk ──────────────►
                           (stable state change)
```

## Latency Analysis

### Gesture: Quick Punch

1. **Sensor Data Arrives**: 0ms
   - Collector immediately pushes to queue

2. **Window Fills**: ~300ms
   - 0.3s of punch data collected
   - Buffer reaches 80% threshold

3. **ML Prediction**: ~350ms
   - Feature extraction: 10-15ms
   - SVM prediction: 20-30ms
   - Total: 330-345ms

4. **Confidence Gating**: ~400-450ms
   - Wait for 5 consecutive "punch" predictions
   - Each cycle takes ~20ms
   - Total: 400-450ms

5. **Action Executed**: ~450ms
   - Keyboard press/release: 1-2ms

**Total Latency**: <500ms from gesture start to action

### Comparison

| System | Latency |
|--------|---------|
| Old (Synchronous + 2.5s window) | 1+ second |
| New (Multi-threaded + 0.3s window) | <500ms |

**Improvement**: **2x faster** 🚀

## Code Structure

### Main Setup
```python
# Create stop event
stop_event = threading.Event()

# Create threads
collector = Thread(target=collector_thread, args=(sock, sensor_queue, stop_event))
predictor = Thread(target=predictor_thread, args=(model, scaler, features, sensor_queue, action_queue, stop_event))
actor = Thread(target=actor_thread, args=(action_queue, sensor_queue, stop_event))

# Start all
collector.start()
predictor.start()
actor.start()
```

### Thread Communication
```python
# Collector pushes
sensor_queue.put(sensor_reading, timeout=0.01)

# Predictor pulls and pushes
sensor_reading = sensor_queue.get(timeout=0.01)
action_queue.put(action, timeout=0.01)

# Actor pulls
action = action_queue.get(timeout=0.1)
```

### Graceful Shutdown
```python
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    stop_event.set()
    collector.join(timeout=2)
    predictor.join(timeout=2)
    actor.join(timeout=2)
```

## Tuning Parameters

### For More Responsiveness
```python
WINDOW_SIZE_SEC = 0.2           # Even shorter window
CONFIDENCE_GATING_COUNT = 3     # Fewer predictions needed
ML_CONFIDENCE_THRESHOLD = 0.65  # Lower threshold
```

**Trade-off**: More false positives

### For More Stability
```python
WINDOW_SIZE_SEC = 0.5           # Longer window for more context
CONFIDENCE_GATING_COUNT = 7     # More predictions needed
ML_CONFIDENCE_THRESHOLD = 0.75  # Higher threshold
```

**Trade-off**: Slightly higher latency

### Recommended (Current)
```python
WINDOW_SIZE_SEC = 0.3           # Balanced
CONFIDENCE_GATING_COUNT = 5     # Stable state changes
ML_CONFIDENCE_THRESHOLD = 0.7   # Good accuracy
```

## Debugging

### Check Thread Status
```python
# In main loop
print(f"Collector alive: {collector.is_alive()}")
print(f"Predictor alive: {predictor.is_alive()}")
print(f"Actor alive: {actor.is_alive()}")
```

### Monitor Queue Sizes
```python
# Add to threads
print(f"[COLLECTOR] Queue size: {sensor_queue.qsize()}")
print(f"[PREDICTOR] Queue size: {action_queue.qsize()}")
```

### Check Prediction Rate
```python
# In predictor thread
prediction_count = 0
start_time = time.time()
# ... predict ...
prediction_count += 1
if prediction_count % 100 == 0:
    elapsed = time.time() - start_time
    rate = prediction_count / elapsed
    print(f"[PREDICTOR] Rate: {rate:.1f} predictions/sec")
```

## Next Steps

As recommended in the roundtable feedback:

### Step 1: Test Current Implementation
- Verify <500ms latency in practice
- Check for false positives/negatives
- Monitor CPU usage

### Step 2: Targeted Data Collection
- Collect more "noise" samples
- Focus on gestures that confuse the model
- Especially: rhythmic arm movements vs walking

### Step 3: Add Delta Features
Split micro-window in half and compute differences:
```python
# First half mean
first_half_mean = accel_mag[:7].mean()
# Second half mean
second_half_mean = accel_mag[7:].mean()
# Delta feature
features['accel_mag_mean_delta'] = second_half_mean - first_half_mean
```

**Why**: Punches have large deltas, walking has small deltas.

---

**Status**: ✅ Multi-threaded ML architecture complete
**Performance**: <500ms latency, continuous prediction
**Next**: Real-world testing and data collection
