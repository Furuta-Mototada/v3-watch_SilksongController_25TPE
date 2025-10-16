# CNN/LSTM Architecture Deep Dive

## Overview

This document provides a detailed technical explanation of the CNN/LSTM hybrid architecture for real-time gesture recognition.

---

## Why Hybrid CNN/LSTM?

### The Two-Stage Problem

Gesture recognition from sensor data requires:
1. **Spatial Feature Extraction**: Identify patterns within sensor readings
2. **Temporal Sequence Modeling**: Understand how patterns evolve over time

**CNN**: Excellent at spatial patterns (what is happening)  
**LSTM**: Excellent at temporal dependencies (how it's changing)

### Why Not Just CNN?

CNNs alone can't capture long-term dependencies:
```
Window 1: [accel spike] → CNN says "maybe jump"
Window 2: [return to baseline] → CNN says "maybe noise"
Window 3: [continued motion] → CNN says "maybe walk"

Problem: Each window is independent. No memory of previous state.
```

### Why Not Just LSTM?

LSTMs alone struggle with raw high-dimensional sensor data:
```
Input: 50 timesteps × 9 sensors = 450 input features
LSTM has to learn everything from scratch
Too many parameters, slow training, poor generalization
```

### Why CNN + LSTM?

**Best of Both Worlds**:
```
Raw Data → CNN (reduce dimensions, extract features)
         → LSTM (model temporal dependencies)
         → Classification
```

---

## Architecture Layers Explained

### Input Layer

**Shape**: `(batch_size, timesteps, features)`

Example: `(32, 50, 9)`
- 32 samples in batch
- 50 timesteps (1 second at 50Hz)
- 9 features (3 sensors × 3 axes)

**Feature Layout**:
```
[accel_x, accel_y, accel_z,  # Linear acceleration
 gyro_x,  gyro_y,  gyro_z,   # Gyroscope
 rot_x,   rot_y,   rot_z]    # Rotation vector
```

### Layer 1: Conv1D (Feature Extraction)

```python
Conv1D(filters=64, kernel_size=5, activation='relu')
```

**What it does**:
- Slides a 5-timestep kernel across the input
- Learns 64 different patterns
- Each filter detects specific features

**Example Learned Filters**:
```
Filter 1: Detects "sudden acceleration spike"
  [0.1, 0.2, 0.8, 0.2, 0.1]  ← Weights learned during training

Filter 2: Detects "gradual increase"
  [0.1, 0.3, 0.5, 0.7, 0.9]

Filter 3: Detects "oscillation"
  [0.5, -0.5, 0.5, -0.5, 0.5]
```

**Output Shape**: `(batch, 46, 64)`
- 46 = 50 - 5 + 1 (sliding window)
- 64 = number of filters

**Visualization**:
```
Input:
Time:  1  2  3  4  5  6  7  8  ...
Data: [2, 3, 8, 3, 2, 1, 1, 2, ...]

Conv1D with kernel=5:
Position 1: [2, 3, 8, 3, 2] → Filter applies → Output: 0.87
Position 2:    [3, 8, 3, 2, 1] → Filter applies → Output: 0.23
Position 3:       [8, 3, 2, 1, 1] → Filter applies → Output: 0.15
...
```

### Layer 2: BatchNormalization

```python
BatchNormalization()
```

**What it does**:
- Normalizes activations to have mean=0, std=1
- Stabilizes training
- Prevents exploding/vanishing gradients

**Why needed**:
```
Without BatchNorm:
Layer 1 output range: [-100, 500]  ← Huge variance
Layer 2 struggles to train

With BatchNorm:
Layer 1 output range: [-1, 1]  ← Normalized
Layer 2 trains smoothly
```

### Layer 3: MaxPooling1D

```python
MaxPooling1D(pool_size=2)
```

**What it does**:
- Takes max value in every 2-timestep window
- Reduces temporal dimension by half
- Creates translation invariance

**Output Shape**: `(batch, 23, 64)`
- 23 = 46 / 2 (pooling)

**Visualization**:
```
Before pooling (46 timesteps):
[0.87, 0.23, 0.15, 0.62, 0.44, 0.91, ...]

After pooling (23 timesteps):
[0.87,       0.62,       0.91, ...]
 ↑            ↑           ↑
max(0.87,0.23) max(0.15,0.62) max(0.44,0.91)
```

### Layer 4: Conv1D (Deeper Features)

```python
Conv1D(filters=128, kernel_size=3, activation='relu')
```

**What it does**:
- Learns 128 higher-level patterns
- Combines features from first Conv layer
- Detects complex multi-feature patterns

**Example Learned Patterns**:
```
Pattern 1: "Acceleration spike + gyro rotation"
  → Detects jump gesture

Pattern 2: "Forward accel + stable rotation"
  → Detects punch gesture

Pattern 3: "Rhythmic acceleration + steady orientation"
  → Detects walking pattern
```

**Output Shape**: `(batch, 21, 128)`

### Layers 5-6: BatchNorm + MaxPooling

Same as before, output shape: `(batch, 10, 128)`

### Layer 7: LSTM (Temporal Memory)

```python
LSTM(units=128, return_sequences=True)
```

**What it does**:
- Processes sequence with memory of previous timesteps
- Learns temporal dependencies
- Outputs hidden state at each timestep

**LSTM Cell Structure**:
```
Input Gate:  Decide what new info to add
Forget Gate: Decide what old info to remove
Output Gate: Decide what to output

Cell State: Long-term memory
Hidden State: Short-term output
```

**Why `return_sequences=True`**:
- Outputs hidden state at ALL timesteps
- Allows second LSTM to process full sequence
- Shape: `(batch, 10, 128)`

**Temporal Learning Example**:
```
Timestep 1: "Acceleration increasing" → LSTM remembers
Timestep 2: "Peak acceleration" → LSTM sees context (was increasing)
Timestep 3: "Acceleration decreasing" → LSTM knows: "This was a jump!"

Without LSTM:
Each timestep analyzed independently, no pattern recognized
```

### Layer 8: Dropout

```python
Dropout(0.3)
```

**What it does**:
- Randomly drops 30% of neurons during training
- Prevents overfitting
- Forces network to learn robust features

**Training vs Inference**:
```
Training:   [1.0, 0.0, 0.8, 0.0, 1.2] ← 30% dropped
Inference:  [1.0, 0.7, 0.8, 0.6, 1.2] ← All active (scaled)
```

### Layer 9: LSTM (Final Temporal Processing)

```python
LSTM(units=64)
```

**What it does**:
- Second LSTM layer for deeper temporal understanding
- Outputs final hidden state only (not sequence)
- Shape: `(batch, 64)`

**Why second LSTM**:
- First LSTM: Low-level temporal patterns
- Second LSTM: High-level temporal patterns
- Similar to how CNNs have multiple conv layers

### Layer 10: Dropout

```python
Dropout(0.3)
```

Again for regularization.

### Layer 11: Dense (Pre-Classification)

```python
Dense(64, activation='relu')
```

**What it does**:
- Fully connected layer
- Combines all temporal features
- Prepares for final classification

**Computation**:
```
Input: 64 features from LSTM
Weights: 64 × 64 = 4,096 parameters
Output: 64 activations

activation = relu(sum(input_i × weight_i) + bias)
```

### Layer 12: Dropout

```python
Dropout(0.3)
```

Final regularization before classification.

### Layer 13: Output Layer

```python
Dense(5, activation='softmax')
```

**What it does**:
- 5 neurons (one per gesture class)
- Softmax ensures outputs sum to 1.0
- Outputs are probabilities

**Softmax Computation**:
```
Raw scores: [2.1, 0.5, -1.2, 0.8, -0.3]
              ↓ exp and normalize
Probabilities: [0.72, 0.15, 0.03, 0.08, 0.06]
                jump  walk  noise turn  punch

Model is 72% confident it's a jump
```

---

## Training Process

### Loss Function: Categorical Cross-Entropy

**Formula**:
```
Loss = -∑ y_true_i × log(y_pred_i)
```

**Example**:
```
True label: [1, 0, 0, 0, 0]  ← Jump
Prediction: [0.72, 0.15, 0.03, 0.08, 0.02]

Loss = -(1×log(0.72) + 0×log(0.15) + ... + 0×log(0.02))
     = -log(0.72)
     = 0.33

Lower loss = better prediction
```

### Optimizer: Adam

**What it does**:
- Adaptive learning rate
- Momentum for faster convergence
- Automatically adjusts step size

**Update Rule**:
```
For each parameter:
1. Compute gradient (direction to improve)
2. Update with momentum (consider previous updates)
3. Adjust learning rate adaptively
4. Apply update to parameter
```

### Training Loop

```python
for epoch in range(100):
    for batch in training_data:
        # Forward pass
        predictions = model.predict(batch_X)
        loss = compute_loss(predictions, batch_y)
        
        # Backward pass
        gradients = compute_gradients(loss)
        
        # Update weights
        optimizer.apply_gradients(gradients)
        
    # Validate
    val_loss, val_acc = model.evaluate(validation_data)
    
    # Early stopping if not improving
    if val_loss not improving for 10 epochs:
        break
```

---

## Inference Process

### Real-Time Prediction

```python
# Incoming sensor data
sensor_buffer = deque(maxlen=50)

while True:
    # Get new reading
    new_data = get_sensor_reading()  # 1 timestep × 9 features
    sensor_buffer.append(new_data)
    
    # Predict when buffer has enough data
    if len(sensor_buffer) >= 25:
        # Prepare input
        X = np.array(sensor_buffer)[-50:]  # Last 50 timesteps
        X = X.reshape(1, 50, 9)  # Add batch dimension
        
        # Single forward pass
        prediction = model.predict(X, verbose=0)  # ~10-30ms
        
        # Get result
        gesture_idx = np.argmax(prediction[0])
        confidence = prediction[0][gesture_idx]
        
        print(f"Gesture: {GESTURES[gesture_idx]}, Confidence: {confidence:.2f}")
```

### Latency Breakdown

```
Component               Time    Notes
─────────────────────────────────────────
Sensor buffering        0ms     Already have data
Array preparation       <1ms    Just reshaping
CNN forward pass        5-10ms  Parallel on CPU
LSTM forward pass       5-15ms  Sequential
Dense layers           <5ms    Small computation
─────────────────────────────────────────
Total inference        10-30ms Per prediction
```

**Why so fast?**:
- No feature engineering (skip 10-15ms)
- No scaling needed (skip 1-2ms)
- Optimized neural network libraries
- Can use GPU for even faster inference

---

## Model Parameters

### Total Parameters

```
Layer            Output Shape       Parameters
─────────────────────────────────────────────────
Conv1D           (None, 46, 64)     2,944
BatchNorm        (None, 46, 64)     256
MaxPooling       (None, 23, 64)     0
Conv1D           (None, 21, 128)    24,704
BatchNorm        (None, 21, 128)    512
MaxPooling       (None, 10, 128)    0
LSTM             (None, 10, 128)    131,584
Dropout          (None, 10, 128)    0
LSTM             (None, 64)         49,408
Dropout          (None, 64)         0
Dense            (None, 64)         4,160
Dropout          (None, 64)         0
Dense            (None, 5)          325
─────────────────────────────────────────────────
Total Parameters: 213,893
```

**Size**: ~850 KB (using float32)

**Comparison**:
- SVM model: ~50 KB
- CNN/LSTM: ~850 KB
- Still very small and fast!

---

## Advantages Over Hand-Engineered Features

### What SVM Does

```python
# Manual feature extraction
def extract_features(window):
    features = []
    
    # We guess these are important
    features.append(np.mean(accel_x))
    features.append(np.std(accel_x))
    features.append(np.max(accel_x))
    features.append(fft_peak(accel_x))
    # ... 56 more features we manually designed
    
    return features  # 60 features
```

**Problems**:
- We might miss important patterns
- We might include irrelevant features
- No temporal understanding

### What CNN/LSTM Does

```python
# Automatic feature learning
# CNN learns filters automatically
# No manual design needed

# Example learned filter (simplified):
filter_1 = [0.2, 0.4, 0.9, 0.3, 0.1]  ← Learned from data
# This might detect "jump acceleration pattern"
# We didn't tell it to look for this - it discovered it!
```

**Advantages**:
- Discovers optimal features automatically
- Learns temporal patterns (LSTM)
- Adapts to new data during training
- No human bias in feature selection

---

## Hyperparameter Tuning

### Key Hyperparameters

**Architecture**:
- CNN filters: 64, 128 (can try 32, 64 or 128, 256)
- LSTM units: 128, 64 (can try 64, 32 or 256, 128)
- Dense units: 64 (can try 32 or 128)

**Training**:
- Learning rate: 0.001 (Adam default)
- Batch size: 32 (can try 16, 64, 128)
- Dropout rate: 0.3 (can try 0.2, 0.4, 0.5)

**Data**:
- Window size: 50 timesteps (can try 25, 75, 100)
- Overlap: 50% (can try 25%, 75%)

### How to Tune

1. **Start with defaults** (as specified above)
2. **Train baseline model**
3. **If overfitting** (train acc >> val acc):
   - Increase dropout (0.3 → 0.5)
   - Add more training data
   - Reduce model size
4. **If underfitting** (both accuracies low):
   - Increase model size
   - Train longer
   - Reduce dropout
5. **If inference too slow**:
   - Reduce model size
   - Quantize model (float32 → float16)
   - Use ONNX runtime

---

## Comparison Table

| Aspect | SVM (Phase IV) | CNN/LSTM (Phase V) |
|--------|---------------|-------------------|
| Feature Engineering | Manual (60+) | Automatic |
| Temporal Modeling | None | LSTM memory |
| Training Data | Snippets | Continuous |
| Inference Speed | 30-50ms | 10-30ms |
| Model Size | 50 KB | 850 KB |
| Accuracy | 85-95% | 90-98% |
| Adaptability | Fixed features | Learns from data |
| Transition Handling | Poor | Excellent |

---

## Conclusion

The CNN/LSTM architecture is **purpose-built for time-series classification**. It combines:
- CNN's ability to extract spatial patterns
- LSTM's ability to model temporal dependencies
- End-to-end learning without manual feature engineering

This is the **state-of-the-art approach** used by Google, Apple, and other major companies for activity recognition.

---

**Next**: See `DATA_COLLECTION.md` for how to collect continuous training data.
