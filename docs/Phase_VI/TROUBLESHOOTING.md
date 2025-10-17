# Troubleshooting Guide: Watson's Two-Stage Fine-Tuning

## Overview

This guide addresses common issues encountered during Watson's three-phase training procedure. Each section corresponds to a phase and provides specific solutions.

---

## Phase 1: Sandbox Test Issues

### Problem: Validation Accuracy Stuck at ~20% (Random Chance)

**Symptoms:**
- Toy dataset training shows no learning
- Validation accuracy remains near 20% (1/5 classes)
- Training and validation curves are flat

**Diagnosis:**
```python
# Check model is actually changing weights
initial_weights = sandbox_model.get_weights()[0].copy()
# Train for 1 epoch
sandbox_model.fit(X_toy, y_toy, epochs=1, verbose=0)
new_weights = sandbox_model.get_weights()[0]
print(f"Weights changed: {not np.allclose(initial_weights, new_weights)}")
# Should print: Weights changed: True
```

**Possible Causes & Solutions:**

#### 1. Data Preprocessing Issue
```python
# Verify data is valid
print(f"X_toy - NaN count: {np.isnan(X_toy).sum()}")
print(f"X_toy - Inf count: {np.isinf(X_toy).sum()}")
print(f"X_toy - Min: {X_toy.min()}, Max: {X_toy.max()}")
print(f"X_toy - Mean: {X_toy.mean()}, Std: {X_toy.std()}")

# If NaN/Inf found:
X_toy = np.nan_to_num(X_toy, nan=0.0, posinf=1e6, neginf=-1e6)
```

#### 2. Learning Rate Too Low
```python
# Try higher learning rate
sandbox_model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.01),  # 10x higher
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)
```

#### 3. Model Architecture Issue
```python
# Verify model output shape matches number of classes
print(f"Model output shape: {sandbox_model.output.shape}")
print(f"Number of classes: {NUM_CLASSES}")
# Should match

# Check model can forward pass
test_output = sandbox_model.predict(X_toy[:1], verbose=0)
print(f"Test output shape: {test_output.shape}")
print(f"Test output sum: {test_output.sum()}")  # Should be ~1.0 (softmax)
```

#### 4. Labels Issue
```python
# Verify labels are valid
print(f"Unique labels in y_toy: {np.unique(y_toy)}")
print(f"Expected labels: {list(range(NUM_CLASSES))}")
print(f"Label range: {y_toy.min()} to {y_toy.max()}")

# Labels should be 0, 1, 2, 3, 4 (not 1, 2, 3, 4, 5)
if y_toy.min() == 1:
    print("⚠️  Labels start at 1, should start at 0")
    y_toy = y_toy - 1  # Shift to 0-indexed
```

**If Still Failing:**
- Visualize sample data from each class
- Check if classes are actually separable
- Try even simpler model (just Dense layers)

---

## Phase 2: CNN-Only Training Issues

### Problem: Validation Accuracy Stuck at ~78% (Majority Class)

**Symptoms:**
- CNN-only model plateaus at majority class percentage
- Classification report shows all predictions are "walk"
- Model hasn't learned minority classes

**Diagnosis:**
```python
# Check what CNN is predicting
y_val_pred = cnn_only_model.predict(X_val, verbose=0)
y_val_pred_classes = np.argmax(y_val_pred, axis=1)

print("CNN predictions distribution:")
for i, gesture in enumerate(GESTURES):
    count = np.sum(y_val_pred_classes == i)
    pct = count / len(y_val_pred_classes) * 100
    print(f"  {gesture:8s}: {count:4d} predictions ({pct:5.1f}%)")
```

**Possible Causes & Solutions:**

#### 1. Class Weights Not Applied
```python
# Verify class weights are being used
if class_weights is None:
    print("❌ Class weights are None!")
    # Recalculate
    from sklearn.utils.class_weight import compute_class_weight
    class_weights_array = compute_class_weight(
        'balanced',
        classes=np.unique(y_train),
        y=y_train
    )
    # Apply softening
    class_weights_array = np.sqrt(class_weights_array)
    class_weights = dict(enumerate(class_weights_array))
    
print("Class weights:")
for i, gesture in enumerate(GESTURES):
    print(f"  {gesture:8s}: {class_weights[i]:.3f}")
```

#### 2. Class Weights Too Weak
```python
# Try less softening (or no softening)
class_weights_array = compute_class_weight(
    'balanced',
    classes=np.unique(y_train),
    y=y_train
)
# Option A: Use full weights (no softening)
class_weights = dict(enumerate(class_weights_array))

# Option B: Use cube root instead of square root
class_weights_array = np.power(class_weights_array, 1/3)
class_weights = dict(enumerate(class_weights_array))

print("Stronger class weights:")
for i, gesture in enumerate(GESTURES):
    print(f"  {gesture:8s}: {class_weights[i]:.3f}")
```

#### 3. Batch Size Too Large
```python
# Try smaller batch size for better gradient updates
history_cnn_only = cnn_only_model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=50,
    batch_size=16,  # Reduced from 32
    class_weight=class_weights,
    callbacks=cnn_callbacks
)
```

#### 4. Need More Training
```python
# Train for more epochs
history_cnn_only = cnn_only_model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=100,  # Increased from 50
    batch_size=32,
    class_weight=class_weights,
    callbacks=cnn_callbacks
)
```

**If Still Failing:**
- Combine with data augmentation (Cell 12)
- Try focal loss instead of class weights
- Collect more data for minority classes

---

### Problem: NaN Loss During CNN Training

**Symptoms:**
- Training starts but loss becomes NaN
- Model performance degrades suddenly
- Training terminates early

**Solutions:**

#### 1. Gradient Clipping
```python
# Already in code, but verify it's active
cnn_only_model.compile(
    optimizer=keras.optimizers.Adam(
        learning_rate=0.001,
        clipnorm=1.0  # Should be present
    ),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)
```

#### 2. Lower Learning Rate
```python
cnn_only_model.compile(
    optimizer=keras.optimizers.Adam(
        learning_rate=0.0001,  # 10x lower
        clipnorm=1.0
    ),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)
```

#### 3. Check for Data Issues
```python
# Clean data before training
X_train_clean = np.nan_to_num(X_train, nan=0.0, posinf=1e6, neginf=-1e6)
X_val_clean = np.nan_to_num(X_val, nan=0.0, posinf=1e6, neginf=-1e6)

# Verify no extreme values
print(f"X_train range: {X_train_clean.min():.4f} to {X_train_clean.max():.4f}")
```

#### 4. Reduce Class Weight Strength
```python
# Use even more softening
class_weights_array = np.power(class_weights_array, 1/4)  # Fourth root
class_weights = dict(enumerate(class_weights_array))
```

---

## Phase 3: Fine-Tuning Issues

### Problem: Model Still Collapses in Phase 3

**Symptoms:**
- Fine-tuned model predicts only majority class
- Performance worse than CNN-only model
- Validation accuracy drops

**Diagnosis:**
```python
# Verify CNN base is actually frozen
print("\nChecking if CNN is frozen:")
for i, layer in enumerate(final_model.layers[0].layers):  # First layer is CNN base
    print(f"Layer {i} ({layer.name}): trainable={layer.trainable}")
    
# All should show: trainable=False
```

**Possible Causes & Solutions:**

#### 1. CNN Not Actually Frozen
```python
# Force freeze all CNN layers
cnn_base = final_model.layers[0]
for layer in cnn_base.layers:
    layer.trainable = False
cnn_base.trainable = False

# Recompile after freezing
final_model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001, clipnorm=1.0),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# Verify
print(f"CNN trainable params: {sum([tf.size(w).numpy() for w in cnn_base.trainable_weights])}")
# Should be 0
```

#### 2. CNN Weights Not Loaded Correctly
```python
# Verify weights were loaded
import os
if not os.path.exists('cnn_only_best_model.h5'):
    print("❌ CNN weights file not found!")
    print("   Re-run Phase 2 to generate weights")
else:
    print("✅ Weights file exists")
    # Reload explicitly
    cnn_base.load_weights('cnn_only_best_model.h5')
    print("✅ Weights reloaded")
```

#### 3. LSTM Layers Too Large
```python
# Try smaller LSTM layers
def build_composite_model_small(frozen_base, num_classes):
    model = keras.Sequential([
        frozen_base,
        layers.LSTM(32, return_sequences=True),  # Reduced from 64
        layers.Dropout(0.4),  # Increased dropout
        layers.LSTM(16),  # Reduced from 32
        layers.Dropout(0.4),
        layers.Dense(32, activation='relu'),  # Reduced from 64
        layers.Dropout(0.4),
        layers.Dense(num_classes, activation='softmax')
    ])
    return model
```

#### 4. Learning Rate Too High
```python
# Use lower learning rate for fine-tuning
final_model.compile(
    optimizer=keras.optimizers.Adam(
        learning_rate=0.0001,  # 10x lower than Phase 2
        clipnorm=1.0
    ),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)
```

---

### Problem: Overfitting (Train >> Val Accuracy)

**Symptoms:**
- Training accuracy very high (>95%)
- Validation accuracy much lower (<85%)
- Large gap between train and val curves

**Solutions:**

#### 1. Increase Dropout
```python
def build_composite_model_dropout(frozen_base, num_classes):
    model = keras.Sequential([
        frozen_base,
        layers.LSTM(64, return_sequences=True),
        layers.Dropout(0.5),  # Increased from 0.3
        layers.LSTM(32),
        layers.Dropout(0.5),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation='softmax')
    ])
    return model
```

#### 2. Add L2 Regularization
```python
def build_composite_model_l2(frozen_base, num_classes):
    model = keras.Sequential([
        frozen_base,
        layers.LSTM(64, return_sequences=True, 
                   kernel_regularizer=keras.regularizers.l2(0.01)),
        layers.Dropout(0.3),
        layers.LSTM(32, kernel_regularizer=keras.regularizers.l2(0.01)),
        layers.Dropout(0.3),
        layers.Dense(64, activation='relu',
                    kernel_regularizer=keras.regularizers.l2(0.01)),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation='softmax')
    ])
    return model
```

#### 3. Early Stopping with Lower Patience
```python
final_callbacks = [
    keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=5,  # Reduced from 15
        restore_best_weights=True
    ),
    # ... other callbacks
]
```

#### 4. Use Data Augmentation
```python
# Enable Cell 12 (data augmentation) before Phase VI
# This increases effective training data size
```

---

## General Issues

### Problem: Training Very Slow (>2 hours)

**Solutions:**

1. **Verify GPU is enabled:**
```python
import tensorflow as tf
print("GPUs available:", tf.config.list_physical_devices('GPU'))
# Should show at least one GPU
```

2. **Enable GPU in Colab:**
   - Runtime → Change runtime type → GPU
   - Restart runtime

3. **Reduce batch size** (paradoxically, can speed up with GPU):
```python
batch_size=64  # Increased from 32
```

4. **Reduce epochs:**
```python
epochs=30  # Instead of 50 or 100
```

### Problem: Out of Memory

**Solutions:**

1. **Reduce batch size:**
```python
batch_size=16  # Reduced from 32
```

2. **Clear memory between phases:**
```python
import gc
import keras.backend as K

# After Phase 1
del sandbox_model
gc.collect()
K.clear_session()

# After Phase 2
del cnn_only_model
gc.collect()
K.clear_session()
```

3. **Use gradient checkpointing** (advanced):
```python
# Add to LSTM layers
layers.LSTM(64, return_sequences=True, unroll=False)
```

---

## Debugging Checklist

Before asking for help, verify:

- [ ] GPU is enabled in Colab
- [ ] All prerequisite cells have been run
- [ ] Data shapes are correct (`print(X_train.shape, y_train.shape)`)
- [ ] No NaN/Inf in data (`np.isnan(X_train).sum() == 0`)
- [ ] Class weights are defined and non-None
- [ ] CNN base is frozen in Phase 3
- [ ] Weights file exists from Phase 2
- [ ] You're using the same data splits across all phases

## Getting More Help

If issues persist:

1. **Check [THEORY.md](THEORY.md)** - Understanding why helps debug
2. **Review [SOP_WATSON_FINE_TUNING.md](SOP_WATSON_FINE_TUNING.md)** - Re-read procedure carefully
3. **Compare [RESULTS_COMPARISON.md](RESULTS_COMPARISON.md)** - See if your results match expected patterns
4. **Check previous PR solutions** - Watson's approach is an alternative; original solutions might work better for your case

## Summary

Most issues fall into these categories:

1. **Data quality** - NaN, Inf, incorrect shapes
2. **Architecture mismatch** - Layers don't align, wrong shapes
3. **Hyperparameters** - Learning rate, batch size, weights
4. **Process errors** - Skipped steps, wrong order
5. **Resource limits** - No GPU, out of memory

Follow this guide systematically, and you'll identify and resolve most issues quickly.
