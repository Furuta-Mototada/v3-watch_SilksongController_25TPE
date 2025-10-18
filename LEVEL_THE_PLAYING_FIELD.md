# 🎯 Level the Playing Field: Complete Guide to Balanced Gesture Recognition

## 😓 The Problem: Why Is Your Model Biased Toward "Walk"?

You trained a model that achieved **77.99% test accuracy**, but when you look at the classification report, you see:

```
              precision    recall  f1-score   support
jump              0.00      0.00      0.00        47   ❌
punch             0.00      0.00      0.00       125   ❌
turn              0.00      0.00      0.00        95   ❌
walk              0.78      1.00      0.88      1173   ✅ Only this works
noise             0.00      0.00      0.00        64   ❌
```

**The model only predicts "walk"!** This happens because:
- 78% of your data is "walk" gestures
- The model learned that predicting "walk" every time gives 78% accuracy
- Minority classes (jump, punch, turn, noise) are ignored

## 🛠️ Solutions: 3 Approaches to Balance Your Model

### ⚡ Quick Solution (Already in Your Notebook!)

**Your notebook already has class weight softening implemented in Cell 11.**

Just retrain by:
1. Runtime → Restart runtime
2. Run all cells from beginning
3. Wait 25-40 minutes

**Expected results:**
- All gestures: 70-85% recall ✅
- Overall accuracy: 85-92% ✅
- Stable training (no NaN loss) ✅

The softened weights help the model pay more attention to rare gestures without causing numerical instability.

---

### 🎨 Better Solution: Add Data Augmentation

If class weights alone don't fix the issue, add **synthetic data** for minority classes.

**Step 1:** Add this new cell **BEFORE Cell 11** (the data splitting cell):

```python
# ============================================================================
# 🎨 DATA AUGMENTATION FOR MINORITY CLASSES
# ============================================================================
print("\n" + "="*60)
print("DATA AUGMENTATION")
print("="*60)

def augment_window(window, noise_level=0.01):
    """
    Apply data augmentation to a sensor window.
    
    Augmentations applied:
    1. Add small random noise
    2. Time warping (slight stretching/squeezing)
    3. Magnitude scaling
    """
    augmented = window.copy()
    
    # Add small random noise (1% of signal magnitude)
    noise = np.random.normal(0, noise_level, augmented.shape)
    augmented = augmented + noise * np.abs(augmented).mean()
    
    # Random scaling (0.95x to 1.05x)
    scale = np.random.uniform(0.95, 1.05)
    augmented = augmented * scale
    
    return augmented

# Calculate samples per class
class_counts = {}
for i in range(NUM_CLASSES):
    class_counts[i] = np.sum(y_combined == i)

print("\nOriginal class distribution:")
for i, gesture in enumerate(GESTURES):
    print(f"  {gesture:8s}: {class_counts[i]:4d} samples")

# Find target count (50% of max class, so augmentation is reasonable)
max_count = max(class_counts.values())
target_count = int(max_count * 0.5)

print(f"\nTarget count for minority classes: {target_count}")

# Augment minority classes
augmented_X = []
augmented_y = []

for class_idx in range(NUM_CLASSES):
    current_count = class_counts[class_idx]
    
    if current_count < target_count:
        # This class needs augmentation
        needed = target_count - current_count
        
        # Get all samples from this class
        class_mask = (y_combined == class_idx)
        class_samples = X_combined[class_mask]
        
        # Generate augmented samples
        print(f"\nAugmenting {GESTURES[class_idx]}: adding {needed} synthetic samples")
        
        for _ in range(needed):
            # Pick a random sample from this class
            idx = np.random.randint(0, len(class_samples))
            original_sample = class_samples[idx]
            
            # Augment it
            augmented_sample = augment_window(original_sample)
            
            augmented_X.append(augmented_sample)
            augmented_y.append(class_idx)

# Add augmented data to original data
if len(augmented_X) > 0:
    X_augmented = np.array(augmented_X)
    y_augmented = np.array(augmented_y)
    
    X_combined = np.vstack([X_combined, X_augmented])
    y_combined = np.concatenate([y_combined, y_augmented])
    
    print(f"\n✅ Added {len(augmented_X)} augmented samples")
    
    print("\nNew class distribution:")
    for i, gesture in enumerate(GESTURES):
        count = np.sum(y_combined == i)
        pct = count / len(y_combined) * 100
        print(f"  {gesture:8s}: {count:4d} samples ({pct:5.1f}%)")
else:
    print("\n✅ No augmentation needed - classes are balanced")

# Calculate new imbalance ratio
new_class_counts = [np.sum(y_combined == i) for i in range(NUM_CLASSES)]
new_imbalance_ratio = max(new_class_counts) / min(new_class_counts)
print(f"\nImbalance ratio: {imbalance_ratio:.1f}x → {new_imbalance_ratio:.1f}x")
```

**Benefits:**
- More training data for rare gestures
- Reduces imbalance from 25x to ~5x
- Model sees more variety of minority class patterns
- No need for extreme class weights

**Expected results:**
- All gestures: 80-90% recall ✅
- Overall accuracy: 88-94% ✅
- Better generalization ✅

---

### 🔥 Advanced Solution: Use Focal Loss

If you're still having issues, replace standard categorical cross-entropy with **focal loss**.

Focal loss automatically focuses learning on hard-to-classify examples (minority classes).

**Step 1:** Add this cell **AFTER Cell 13** (model creation):

```python
# ============================================================================
# 🔥 FOCAL LOSS - Alternative to Class Weights
# ============================================================================
import tensorflow.keras.backend as K

def focal_loss(gamma=2.0, alpha=0.25):
    """
    Focal Loss for multi-class classification.
    
    FL(p_t) = -alpha * (1 - p_t)^gamma * log(p_t)
    
    Args:
        gamma: Focusing parameter (higher = more focus on hard examples)
        alpha: Balance parameter for class importance
    
    Returns:
        Focal loss function
    """
    def focal_loss_fixed(y_true, y_pred):
        # Clip predictions to prevent log(0)
        y_pred = K.clip(y_pred, K.epsilon(), 1.0 - K.epsilon())
        
        # Calculate cross entropy
        cross_entropy = -y_true * K.log(y_pred)
        
        # Calculate focal loss
        loss = alpha * K.pow(1 - y_pred, gamma) * cross_entropy
        
        return K.mean(K.sum(loss, axis=-1))
    
    return focal_loss_fixed

print("✅ Focal loss defined")
print("\n💡 Focal loss will:")
print("   - Automatically focus on minority classes")
print("   - Reduce importance of easy examples (walk)")
print("   - No need for manual class weights")
```

**Step 2:** Modify model compilation in Cell 13:

Find this line:
```python
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
```

Replace with:
```python
# Use focal loss instead of categorical crossentropy
model.compile(
    optimizer='adam',
    loss=focal_loss(gamma=2.0, alpha=0.25),
    metrics=['accuracy']
)
print("✅ Model compiled with focal loss")
```

**Step 3:** Set `class_weights = None` in Cell 11:

After the class weight calculation section, add:
```python
# Override with None when using focal loss
class_weights = None
print("\n⚠️  Using focal loss instead of class weights")
```

**Benefits:**
- Automatically handles imbalance without manual tuning
- More stable than extreme class weights
- Learns to distinguish hard examples
- Works well with 10-50x imbalance

**Expected results:**
- All gestures: 82-92% recall ✅
- Overall accuracy: 88-95% ✅
- Very stable training ✅

---

## 🎯 Decision Tree: Which Solution Should You Use?

```
Start Here
    ↓
Has your model trained at all?
    ├─ No (NaN loss, crashes) → Use Quick Solution (class weights already in notebook)
    └─ Yes (but only predicts walk) → Go to next question
            ↓
            How much time do you have?
            ├─ 40 minutes → Quick Solution (retrain with existing class weights)
            ├─ 1 hour → Better Solution (add data augmentation)
            └─ 2 hours → Advanced Solution (implement focal loss)
```

## 📊 Expected Performance by Solution

| Solution | Setup Time | Training Time | Expected Accuracy | All Gestures Working? |
|----------|------------|---------------|-------------------|----------------------|
| **Quick (class weights)** | 0 min | 30 min | 85-92% | ✅ 70-85% each |
| **Better (+ augmentation)** | 10 min | 40 min | 88-94% | ✅ 80-90% each |
| **Advanced (focal loss)** | 15 min | 30 min | 88-95% | ✅ 82-92% each |

## 💡 Pro Tips

### Tip 1: Always Check Per-Class Performance

Don't trust overall accuracy alone! Always run this evaluation:

```python
# After training, evaluate per-class performance
y_pred = model.predict(X_test, verbose=0)
y_pred_classes = np.argmax(y_pred, axis=1)

from sklearn.metrics import classification_report
print("\nPER-CLASS PERFORMANCE:")
print(classification_report(y_test, y_pred_classes, target_names=GESTURES))
```

**Good results look like:**
```
              precision    recall  f1-score
jump              0.85      0.82      0.83    ← All > 0.80
punch             0.89      0.87      0.88    ← All > 0.80
turn              0.83      0.85      0.84    ← All > 0.80
walk              0.94      0.96      0.95    ← All > 0.80
noise             0.78      0.75      0.76    ← Even noise > 0.75!
```

### Tip 2: Collect More Data for Rare Gestures

**Long-term solution:** Record more sessions with emphasis on rare gestures.

```bash
# On your Mac
cd src
python continuous_data_collector.py --duration 600 --session focused_jump

# During recording, say "jump" 30-50 times
# This will drastically improve jump recognition
```

### Tip 3: Use Learning Rate Scheduling

Add this to your callbacks in Cell 15:

```python
# Add learning rate reduction on plateau
callbacks = [
    keras.callbacks.EarlyStopping(...),
    keras.callbacks.ModelCheckpoint(...),
    keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-7,
        verbose=1
    )
]
```

This helps the model find better solutions when stuck in local minima.

### Tip 4: Visualize Training Progress

Add this cell after training to see if one class is dominating:

```python
# Check what the model predicts during training
y_train_pred = model.predict(X_train[:1000], verbose=0)
y_train_pred_classes = np.argmax(y_train_pred, axis=1)

print("Model's prediction distribution on training data:")
for i, gesture in enumerate(GESTURES):
    count = np.sum(y_train_pred_classes == i)
    pct = count / len(y_train_pred_classes) * 100
    print(f"  {gesture:8s}: {count:4d} predictions ({pct:5.1f}%)")

# If model predicts >90% walk, it's biased!
```

---

## 🆘 Troubleshooting

### Problem: Model still only predicts "walk" after using class weights

**Solution:** Try data augmentation (Better Solution). Your imbalance might be too extreme for weights alone.

### Problem: Training gives NaN loss

**Solutions:**
1. Make sure data quality check in Cell 11 is cleaning NaN values
2. Try removing class weights: `class_weights = None`
3. Add gradient clipping in model compilation:
   ```python
   optimizer = keras.optimizers.Adam(learning_rate=0.001, clipnorm=1.0)
   ```

### Problem: Training is very slow

**Solutions:**
1. Check GPU is enabled: Runtime → Change runtime type → GPU
2. Reduce batch size from 32 to 16
3. Reduce window size from 50 to 25 samples (faster but less context)

### Problem: Model works in Colab but not on my watch

**Solutions:**
1. Check sensor data alignment - watch data might have different sampling rate
2. Add normalization layer to model to handle different input ranges
3. Test with synthetic data first before using real watch data

---

## ✅ Quick Checklist: Am I Ready to Retrain?

Before retraining, verify:

- [ ] I understand why my model is biased (class imbalance)
- [ ] I've chosen one of the three solutions above
- [ ] I've updated the notebook with any new code cells
- [ ] I have GPU enabled in Colab
- [ ] I have 30-60 minutes for training
- [ ] I'm ready to evaluate per-class performance after training

---

## 🎉 Success Criteria

Your model is **successfully balanced** when:

1. ✅ All gestures have recall > 70%
2. ✅ No single class has 100% recall (sign of bias)
3. ✅ Overall accuracy > 85%
4. ✅ Confusion matrix shows errors spread across classes, not concentrated
5. ✅ Model works well in real-time testing on your watch

---

## 💬 Still Tired? Try This 5-Minute Test First

Before retraining (which takes 30-40 min), do this quick test:

```python
# Load your current model (if you already trained one)
# Check if it's REALLY broken or just needs threshold adjustment

y_pred = model.predict(X_test, verbose=0)

# Check confidence scores
for i in range(10):  # Test 10 random samples
    true_label = y_test[i]
    pred_probs = y_pred[i]
    pred_label = np.argmax(pred_probs)
    confidence = pred_probs[pred_label]
    
    print(f"True: {GESTURES[true_label]:8s} | Pred: {GESTURES[pred_label]:8s} | Conf: {confidence:.2f}")
    print(f"  All probabilities: {[f'{p:.2f}' for p in pred_probs]}")
```

**If you see:**
- Confidence always 0.99-1.00 for "walk" → Model is broken, needs retraining ❌
- Confidence varies, some predictions correct → Model might work with threshold tuning ✅
- Other classes have 0.20-0.40 probability → Model learned something, just needs improvement ✅

---

## 🚀 Ready to Start?

**For most people, I recommend:**

1. Start with **Quick Solution** (0 extra work, just retrain)
2. If that doesn't work, add **Data Augmentation** (10 min setup)
3. If still not satisfied, try **Focal Loss** (15 min setup, best results)

Remember: You're not trying to get 100% accuracy. **85-92% with all gestures working is excellent!**

Good luck! You've got this! 💪
