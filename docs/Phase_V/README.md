# Phase V: CNN/LSTM Deep Learning Architecture

**Status:** 🚧 **PLANNING** - Next Major Evolution

---

## Overview

Phase V represents a **fundamental architectural shift** from classical machine learning (SVM with hand-engineered features) to modern **deep learning** for real-time time-series classification.

### The Vision

**"Both Quick AND Accurate"** - Achieve <100ms latency with 90%+ accuracy using state-of-the-art deep learning.

---

## Why Deep Learning?

### The Problem with Classical ML (SVM)

Our current Phase IV system uses:
```
Raw Signal → Manual Features → SVM → Prediction
             (60+ hand-crafted)  (static)
```

**Limitations**:
1. ❌ **Manual Feature Engineering**: We guess what features are important
2. ❌ **Static Windows**: Model sees summary statistics, not temporal patterns
3. ❌ **No Memory**: Each prediction is independent
4. ❌ **Snippet Training**: Trained on isolated clips, not continuous motion
5. ❌ **Speed/Context Trade-off**: Small windows (fast) miss patterns, large windows (accurate) are slow

### The Deep Learning Solution

```
Raw Signal → CNN → LSTM → Dense → Prediction
             (learns features) (temporal memory) (classification)
```

**Advantages**:
1. ✅ **Automatic Feature Learning**: Model discovers optimal patterns
2. ✅ **Temporal Awareness**: LSTM remembers previous states and transitions
3. ✅ **Continuous Motion**: Train on long recordings with all gestures
4. ✅ **Real-Time Inference**: Optimized for streaming data
5. ✅ **Speed AND Accuracy**: No trade-off needed

---

## Architecture: CNN/LSTM Hybrid

### Model Structure

```
Input: Raw Sensor Data (3 sensors × 3 axes = 9 channels)
  ↓
┌─────────────────────────────────────┐
│  1. Convolutional Layer (Feature    │
│     Extraction)                      │
│                                      │
│  Conv1D(filters=64, kernel=5)       │
│  → BatchNorm → ReLU → MaxPool       │
│                                      │
│  Conv1D(filters=128, kernel=3)      │
│  → BatchNorm → ReLU → MaxPool       │
│                                      │
│  Result: Learned spatial patterns   │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  2. LSTM Layer (Temporal Memory)    │
│                                      │
│  LSTM(units=128, return_sequences)  │
│  → Dropout(0.3)                     │
│                                      │
│  LSTM(units=64)                     │
│  → Dropout(0.3)                     │
│                                      │
│  Result: Temporal context & memory  │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  3. Dense Layers (Classification)   │
│                                      │
│  Dense(64) → ReLU → Dropout(0.3)    │
│  Dense(5, softmax)                  │
│                                      │
│  Output: [jump, punch, turn, walk,  │
│           noise] probabilities      │
└─────────────────────────────────────┘
```

### Why This Architecture?

**CNN (Convolutional)**: 
- Extracts local patterns from sensor data
- Learns filters automatically (no hand-engineering)
- Translation-invariant (gesture position doesn't matter)
- Example: "Sharp acceleration peak" is a learned filter

**LSTM (Long Short-Term Memory)**:
- Remembers previous states
- Learns temporal dependencies
- Understands gesture transitions
- Example: "Walk → Jump" is learned pattern

**Dense (Fully Connected)**:
- Final classification
- Outputs probabilities for each gesture
- Softmax ensures probabilities sum to 1

---

## Training Data: Continuous Motion

### The Revolutionary Change

**Old Way (Phase II)**:
```
Record 40 isolated 2.5-second clips per gesture
gesture_jump_01.csv (2.5s)
gesture_jump_02.csv (2.5s)
...
gesture_jump_40.csv (2.5s)
```

**Problems**:
- No transitions between gestures
- No context of previous motion
- Artificial start/stop in each clip

**New Way (Phase V)**:
```
Record ONE continuous 5-10 minute session performing all gestures naturally
continuous_session_01.csv (10 minutes)
  ├─ 0:00-0:15 → Walking
  ├─ 0:15-0:16 → Jump
  ├─ 0:16-0:30 → Walking
  ├─ 0:30-0:31 → Punch
  ├─ 0:31-0:45 → Walking
  ├─ 0:45-0:50 → Turn
  └─ ... continues naturally
```

**Advantages**:
- ✅ Natural transitions captured
- ✅ Continuous context for LSTM
- ✅ Realistic data distribution
- ✅ Models learn actual gameplay patterns

### Labeling Strategy

**During Recording**:
1. Perform continuous motion (walk, jump, punch, turn, repeat)
2. Use phone/keyboard to mark timestamps when gestures occur
3. Auto-generate labels file with gesture start/end times

**Label Format** (`session_labels.csv`):
```csv
start_time,end_time,gesture,confidence
0.0,15.2,walk,1.0
15.2,15.5,jump,1.0
15.5,30.1,walk,1.0
30.1,30.4,punch,1.0
30.4,45.0,walk,1.0
45.0,50.2,turn,1.0
```

**Training Process**:
1. Load continuous sensor data
2. Slide window across entire recording
3. At each timestep, predict current gesture
4. Compare prediction to label at that timestamp
5. Backpropagate error to update model weights

---

## Real-Time Inference

### Streaming Architecture

```python
# Continuous buffer for incoming data
sensor_buffer = deque(maxlen=50)  # 1 second at 50Hz

while True:
    # Receive new sensor reading
    new_data = get_sensor_reading()
    sensor_buffer.append(new_data)
    
    # Always predict on latest window
    if len(sensor_buffer) >= 25:  # 0.5s minimum
        # Prepare input tensor
        X = np.array(sensor_buffer)[-25:]  # Last 0.5s
        X = X.reshape(1, 25, 9)  # (batch, timesteps, features)
        
        # Predict (single forward pass)
        prediction = model.predict(X)
        gesture = np.argmax(prediction)
        confidence = prediction[0][gesture]
        
        # Execute if confident
        if confidence > 0.8:
            execute_action(gesture)
```

### Key Differences from SVM

**SVM Approach**:
1. Wait for full 2.5s window
2. Extract 60+ features (takes 10-15ms)
3. Scale features
4. SVM prediction
5. **Total: 300-500ms**

**CNN/LSTM Approach**:
1. Continuously buffer incoming data
2. Single forward pass through network
3. Prediction at every timestep
4. **Total: 10-50ms**

**Why Faster?**:
- No manual feature extraction
- No scaling needed
- Optimized GPU/CPU inference
- Model is smaller and faster

---

## Implementation Plan

### Step 1: Data Collection Tool

**File**: `src/continuous_data_collector.py`

**Features**:
- Record continuous sensor stream
- Keyboard shortcuts to mark gesture boundaries
- Real-time visualization
- Auto-save with timestamps

**Usage**:
```bash
python src/continuous_data_collector.py --duration 600  # 10 minutes
# Press keys during recording:
# 'j' = Jump (marks next 0.3s as jump)
# 'p' = Punch (marks next 0.3s as punch)
# 't' = Turn (marks next 0.5s as turn)
# Everything else = Walk
```

### Step 2: Model Architecture

**File**: `src/models/cnn_lstm_model.py`

**Framework**: TensorFlow/Keras or PyTorch

**Model Definition**:
```python
def create_cnn_lstm_model(input_shape=(50, 9), num_classes=5):
    """
    Creates CNN/LSTM hybrid model for gesture recognition.
    
    Args:
        input_shape: (timesteps, features) = (50, 9)
        num_classes: Number of gesture classes (5)
    
    Returns:
        Compiled Keras model
    """
    model = Sequential([
        # CNN Feature Extraction
        Conv1D(filters=64, kernel_size=5, activation='relu', 
               input_shape=input_shape),
        BatchNormalization(),
        MaxPooling1D(pool_size=2),
        
        Conv1D(filters=128, kernel_size=3, activation='relu'),
        BatchNormalization(),
        MaxPooling1D(pool_size=2),
        
        # LSTM Temporal Processing
        LSTM(128, return_sequences=True),
        Dropout(0.3),
        
        LSTM(64),
        Dropout(0.3),
        
        # Dense Classification
        Dense(64, activation='relu'),
        Dropout(0.3),
        
        Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model
```

### Step 3: Training Pipeline

**File**: `notebooks/Phase_V_Training.ipynb`

**Process**:
1. Load continuous recordings
2. Load label files
3. Create sliding window dataset
4. Split train/validation/test
5. Train model with early stopping
6. Evaluate on test set
7. Save model

**Expected Training Time**: 1-2 hours on CPU, 10-20 minutes on GPU

### Step 4: Real-Time Integration

**File**: `src/udp_listener_v3.py`

**Architecture**:
```python
# Load trained model
model = load_model('models/cnn_lstm_gesture.h5')

# Streaming buffer
sensor_buffer = deque(maxlen=50)

while True:
    # Collect sensor data
    data = sock.recvfrom(2048)
    sensor_reading = parse_sensor_data(data)
    sensor_buffer.append(sensor_reading)
    
    # Predict on every frame
    if len(sensor_buffer) >= 25:
        X = prepare_input(sensor_buffer)
        prediction = model.predict(X, verbose=0)
        
        gesture = GESTURES[np.argmax(prediction)]
        confidence = prediction[0].max()
        
        if confidence > 0.8:
            execute_gesture(gesture, confidence)
```

---

## Expected Performance

### Latency Targets

| Component | Time | Notes |
|-----------|------|-------|
| Sensor buffer | 0-500ms | Accumulate data |
| Model inference | 10-30ms | Single forward pass |
| Confidence gating | 20-50ms | 2-3 consecutive predictions |
| **Total** | **50-100ms** | **10x faster than SVM** |

### Accuracy Targets

| Gesture | SVM (Phase IV) | CNN/LSTM (Phase V) | Improvement |
|---------|----------------|-------------------|-------------|
| Jump | 85-95% | 90-98% | +5-10% |
| Punch | 85-95% | 90-98% | +5-10% |
| Turn | 85-95% | 88-96% | +3-8% |
| Walk | 85-95% | 92-99% | +7-12% |
| **Overall** | **85-95%** | **90-98%** | **+5-10%** |

### Why Better Accuracy?

1. **Temporal Context**: LSTM understands gesture flow
2. **Automatic Features**: CNN learns optimal patterns
3. **Continuous Training**: Model sees realistic transitions
4. **No Feature Loss**: Raw data preserves all information

---

## Migration Path

### Phase IV → Phase V Transition

**Week 1: Data Collection**
- [ ] Implement continuous data collector tool
- [ ] Record 5-10 continuous sessions (5-10 min each)
- [ ] Manually verify labels are accurate
- [ ] Split into train/val/test sets

**Week 2: Model Development**
- [ ] Implement CNN/LSTM architecture
- [ ] Train initial model on collected data
- [ ] Evaluate performance metrics
- [ ] Tune hyperparameters if needed

**Week 3: Integration**
- [ ] Create new udp_listener_v3.py
- [ ] Test real-time inference speed
- [ ] Implement confidence gating
- [ ] A/B test against Phase IV

**Week 4: Refinement**
- [ ] Collect more data if accuracy insufficient
- [ ] Fine-tune model architecture
- [ ] Optimize inference speed
- [ ] Deploy to production

### Backward Compatibility

Phase V will coexist with Phase IV:
```
config.json:
  "ml_mode": "cnn_lstm"  # or "svm" for Phase IV
```

Users can switch between architectures for comparison.

---

## Technical Requirements

### Dependencies

**New Packages**:
```bash
pip install tensorflow>=2.10.0  # or pytorch>=2.0.0
pip install keras>=2.10.0
pip install h5py  # For model saving
```

**Existing Packages** (already have):
- pandas, numpy, scipy
- pynput, zeroconf
- matplotlib (for visualization)

### Hardware Requirements

**Training**:
- CPU: 4+ cores (1-2 hours training)
- RAM: 8GB+ 
- GPU: Optional (10-20 min training)

**Inference**:
- CPU: 2+ cores
- RAM: 4GB+
- Latency: <50ms on modern CPU

---

## Advantages Over Phase IV

| Aspect | Phase IV (SVM) | Phase V (CNN/LSTM) | Winner |
|--------|----------------|-------------------|---------|
| **Latency** | ~500ms | <100ms | 🏆 Phase V |
| **Accuracy** | 85-95% | 90-98% | 🏆 Phase V |
| **Features** | Manual (60+) | Automatic | 🏆 Phase V |
| **Temporal** | None | LSTM memory | 🏆 Phase V |
| **Training Data** | Snippets | Continuous | 🏆 Phase V |
| **Transitions** | Poor | Excellent | 🏆 Phase V |
| **Setup** | Simpler | More complex | ⚠️ Phase IV |
| **Dependencies** | Lighter | TensorFlow/PyTorch | ⚠️ Phase IV |

**Verdict**: Phase V is superior in every performance metric, with slightly higher setup complexity.

---

## Risk Mitigation

### Potential Issues

1. **Training Data Insufficient**
   - Mitigation: Collect 10+ sessions, augment data
   
2. **Model Overfits**
   - Mitigation: Dropout, early stopping, validation split
   
3. **Inference Too Slow**
   - Mitigation: Model quantization, pruning, ONNX conversion

4. **GPU Not Available**
   - Mitigation: CPU training (slower but works), use Google Colab

5. **Transitions Confuse Model**
   - Mitigation: Add "transition" class, increase buffer size

---

## Success Criteria

Phase V will be considered successful when:

✅ **Latency**: <100ms from gesture start to keyboard action  
✅ **Accuracy**: >90% on all gesture types  
✅ **Smoothness**: No flickering between predictions  
✅ **Playability**: User can play game without noticing lag  
✅ **Robustness**: Works in different orientations and speeds  

---

## Future Enhancements (Phase VI+)

1. **Attention Mechanism**: Focus on important time segments
2. **Multi-Task Learning**: Predict gesture + confidence simultaneously
3. **Online Learning**: Model adapts to user over time
4. **Compressed Models**: TFLite for mobile deployment
5. **Ensemble Models**: Combine multiple networks for reliability

---

## References

**Academic Papers**:
- "Deep Learning for Sensor-Based Activity Recognition" (Ordóñez & Roggen, 2016)
- "Human Activity Recognition using Wearable Sensors by Deep Convolutional Neural Networks" (Yang et al., 2015)
- "LSTM Networks for Human Activity Recognition" (Hammerla et al., 2016)

**Similar Projects**:
- Google's Activity Recognition API (uses CNN/LSTM)
- Apple's Core ML for gesture recognition
- TensorFlow Lite micro gestures example

---

## Conclusion

Phase V represents the evolution from **classical ML to modern deep learning**. By training on continuous motion and leveraging temporal neural networks, we achieve both the **speed** and **accuracy** required for real-time gaming.

This is not just an incremental improvement - it's a fundamental architectural shift that puts us on par with state-of-the-art gesture recognition systems.

---

**Status**: 🚧 Planning Complete - Ready for Implementation  
**Next Step**: Create continuous data collection tool  
**Expected Completion**: 4 weeks from start  
**Performance Goal**: <100ms latency, >90% accuracy
