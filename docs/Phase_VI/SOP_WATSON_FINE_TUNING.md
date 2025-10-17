# Standard Operating Procedure: Watson's Two-Stage Fine-Tuning

**ID:** `SOP-ML-DEBUG-001`  
**Date:** October 17, 2025  
**Author:** Professor Patrick Watson (Interpreted)  
**Subject:** Resolving model collapse and class imbalance issues in 1D time-series gesture recognition

## 1.0 Objective

To systematically diagnose and resolve training failure ("model collapse") observed in the `Colab_CNN_LSTM_Training.ipynb` notebook, where the model exclusively predicts the majority class ('walk'). This procedure establishes a working baseline and guides training of a high-performance, stable model using a two-stage, fine-tuning approach.

## 2.0 Prerequisites

### 2.1 Environment
- Configured Google Colab notebook (`Colab_CNN_LSTM_Training.ipynb`)
- GPU runtime enabled (Runtime → Change runtime type → GPU)
- TensorFlow 2.x installed

### 2.2 Data
- Full, imbalanced dataset loaded (`X_combined`, `y_combined`)
- Data split into `X_train`, `X_val`, `X_test`
- Class distribution analyzed (showing severe imbalance)

### 2.3 Problem State
- Current model plateaus at majority class percentage (~78%)
- Classification report shows zero precision/recall for minority classes
- `create_cnn_lstm_model` function is defined

### 2.4 Prerequisites Code

```python
# Verify these are defined in your notebook
print(f"X_train shape: {X_train.shape}")
print(f"y_train shape: {y_train.shape}")
print(f"Number of classes: {NUM_CLASSES}")
print(f"Gestures: {GESTURES}")
print(f"Class weights calculated: {class_weights}")
```

## 3.0 Procedure

This procedure has **three phases**, moving from simple to complex:

### Phase 1: De-Risk the Problem - "Sandbox Test"

**Purpose:** Verify the model architecture can learn when class imbalance is not a factor.

#### Step 1.1: Create Small, Balanced "Toy" Dataset

**Purpose:** Create ideal, miniature dataset where every class has equal samples.

**Action:** Add this cell after your train/test split:

```python
# ============================================================================
# PHASE 1, STEP 1.1: Create Small, Balanced "Toy" Dataset
# ============================================================================
print("="*70)
print("PHASE 1: DE-RISK THE PROBLEM - SANDBOX TEST")
print("="*70)

from sklearn.model_selection import train_test_split

# Take a small, stratified sample from full training set
# Aim for ~200 samples per class for rapid testing
_, X_toy, _, y_toy = train_test_split(
    X_train,
    y_train,
    test_size=0.15,  # Take 15% sample, adjust as needed
    random_state=42,
    stratify=y_train
)

print("\n✅ Created small, balanced 'toy' dataset for debugging")
print(f"Toy dataset shape: X={X_toy.shape}, y={y_toy.shape}")

# Verify the balance
toy_class_counts = np.bincount(y_toy)
print("\nToy dataset class distribution:")
for i, count in enumerate(toy_class_counts):
    pct = count / len(y_toy) * 100
    print(f"  Class {i} ({GESTURES[i]}): {count:4d} samples ({pct:5.1f}%)")
```

**Success Criteria:**
- Code executes without errors
- Variables `X_toy` and `y_toy` created
- Sample contains all classes

#### Step 1.2: Train Full Model on Toy Dataset

**Purpose:** Confirm CNN/LSTM architecture can learn given manageable problem.

**Action:** Add this cell:

```python
# ============================================================================
# PHASE 1, STEP 1.2: Train Full Model on Toy Dataset
# ============================================================================
print("\n" + "="*70)
print("STEP 1.2: Training full model on toy dataset")
print("="*70)

# Create fresh instance of full model
sandbox_model = create_cnn_lstm_model(
    input_shape=(WINDOW_SIZE, NUM_FEATURES),
    num_classes=NUM_CLASSES
)

# Compile with same optimizer settings
sandbox_model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001, clipnorm=1.0),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print("\n🚀 Training full model on small 'toy' dataset...")
print("Looking for signs of learning, not perfect model")

# Train for few epochs
history_toy = sandbox_model.fit(
    X_toy,
    y_toy,
    validation_split=0.2,  # Use portion of toy set for validation
    epochs=30,
    batch_size=32,
    class_weight=class_weights,  # Use calculated class weights
    verbose=1
)

# Plot results
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

ax1.plot(history_toy.history['accuracy'], label='Train Accuracy')
ax1.plot(history_toy.history['val_accuracy'], label='Val Accuracy')
ax1.set_title('Sandbox Test: Model Accuracy')
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Accuracy')
ax1.legend()
ax1.grid(True)
ax1.axhline(y=0.2, color='r', linestyle='--', label='Random Chance (20%)')

ax2.plot(history_toy.history['loss'], label='Train Loss')
ax2.plot(history_toy.history['val_loss'], label='Val Loss')
ax2.set_title('Sandbox Test: Model Loss')
ax2.set_xlabel('Epoch')
ax2.set_ylabel('Loss')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.show()

final_val_acc = history_toy.history['val_accuracy'][-1]
print(f"\n📊 Final validation accuracy: {final_val_acc*100:.2f}%")

if final_val_acc > 0.6:
    print("✅ SUCCESS: Model architecture is fundamentally sound!")
    print("   Validation accuracy > 60% proves model can learn.")
    print("   Proceeding to Phase 2...")
else:
    print("❌ WARNING: Model not learning effectively on toy dataset")
    print("   Validation accuracy should be > 60%")
    print("   Review model architecture and data preprocessing")
```

**Success Criteria:**
- Validation accuracy **consistently** rises above random chance (20%)
- Ideally surpasses 60-70%
- If successful, model architecture is fundamentally sound → Proceed to Phase 2

**Troubleshooting:**
- If accuracy stuck near random chance: fundamental issue in model architecture or data preprocessing
- Review `create_windows` function
- Check for NaN/Inf in data
- Verify input shapes are correct

---

### Phase 2: Establish CNN as Baseline Feature Extractor

**Purpose:** Follow Watson's "hacky, quick way" - prove CNN can extract meaningful features.

#### Step 2.1: Isolate CNN Architecture

**Purpose:** Create simplified model with only convolutional layers (no LSTM).

**Action:** Add this cell:

```python
# ============================================================================
# PHASE 2, STEP 2.1: Define CNN-Only Model
# ============================================================================
print("\n" + "="*70)
print("PHASE 2: ESTABLISH CNN AS BASELINE FEATURE EXTRACTOR")
print("="*70)

def create_cnn_only_model(input_shape, num_classes):
    """
    Creates model with only convolutional base.
    This is the 'whack off the LSTM' step Watson advised.
    """
    model = keras.Sequential([
        layers.Input(shape=input_shape),
        
        # Same CNN layers from original model
        layers.Conv1D(filters=64, kernel_size=3, padding='same', 
                     activation='relu', name='conv1d_1'),
        layers.BatchNormalization(name='batch_norm_1'),
        layers.MaxPooling1D(pool_size=2, name='max_pool_1'),
        
        layers.Conv1D(filters=128, kernel_size=3, padding='same', 
                     activation='relu', name='conv1d_2'),
        layers.BatchNormalization(name='batch_norm_2'),
        # No second pooling layer (as in original design)
        
        # Simple classifier head
        layers.GlobalAveragePooling1D(),  # Flatten temporal dimension
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation='softmax', name='output')
    ], name='CNN_Only_Model')
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001, clipnorm=1.0),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    return model

print("✅ CNN-only model architecture defined")
```

**Success Criteria:**
- Function defined without errors

#### Step 2.2: Train CNN-Only Model on Full Dataset

**Purpose:** Train convolutional filters to become effective pattern detectors using all data.

**Action:** Add this cell:

```python
# ============================================================================
# PHASE 2, STEP 2.2: Train CNN-Only Model on Full Dataset
# ============================================================================
print("\n" + "="*70)
print("STEP 2.2: Training CNN-only model on full dataset")
print("="*70)

cnn_only_model = create_cnn_only_model(
    input_shape=(WINDOW_SIZE, NUM_FEATURES),
    num_classes=NUM_CLASSES
)

print("\nModel Architecture:")
cnn_only_model.summary()

print("\n🚀 Training CNN-only model on full, imbalanced dataset...")
print("Using class weights to force simple classifier to learn minority classes")
print("Even if final classification is skewed, CNN filters will learn patterns")

# Define callbacks for this stage
cnn_callbacks = [
    keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True,
        verbose=1
    ),
    keras.callbacks.ModelCheckpoint(
        'cnn_only_best_model.h5',
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    ),
    keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-7,
        verbose=1
    )
]

history_cnn_only = cnn_only_model.fit(
    X_train,
    y_train,
    validation_data=(X_val, y_val),
    epochs=50,  # Train long enough for filters to learn
    batch_size=32,
    class_weight=class_weights,  # Use calculated class weights
    callbacks=cnn_callbacks,
    verbose=1
)

# Plot training history
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

ax1.plot(history_cnn_only.history['accuracy'], label='Train Accuracy')
ax1.plot(history_cnn_only.history['val_accuracy'], label='Val Accuracy')
ax1.set_title('CNN-Only Model: Accuracy')
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Accuracy')
ax1.legend()
ax1.grid(True)

ax2.plot(history_cnn_only.history['loss'], label='Train Loss')
ax2.plot(history_cnn_only.history['val_loss'], label='Val Loss')
ax2.set_title('CNN-Only Model: Loss')
ax2.set_xlabel('Epoch')
ax2.set_ylabel('Loss')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.show()

# Evaluate
cnn_val_acc = max(history_cnn_only.history['val_accuracy'])
print(f"\n📊 Best validation accuracy: {cnn_val_acc*100:.2f}%")

if cnn_val_acc > 0.80:
    print("✅ SUCCESS: CNN base is viable feature extractor!")
    print("   Validation accuracy > 80% proves CNN learned useful features")
    print("   Proceeding to Phase 3 (fine-tuning)...")
else:
    print("⚠️  WARNING: CNN-only model not performing well")
    print("   Expected >80% validation accuracy")
    print("   Review data preprocessing and CNN architecture")
```

**Success Criteria:**
- Model trains successfully
- Validation accuracy achieves reasonable score (>80%)
- Proves CNN base is viable feature extractor → Proceed to Phase 3

**Troubleshooting:**
- If model still collapses: issue in preprocessing or data separability
- Re-run Phase 1
- Visualize data (plot sample windows for each class)

---

### Phase 3: Fine-Tuning the Full Model (Two-Stage Training)

**Purpose:** Implement Watson's core strategy - freeze trained CNN, train only LSTM/Dense layers.

#### Step 3.1: Create Frozen Feature Extractor Base

**Purpose:** Load CNN weights and lock them to prevent changes in next training stage.

**Action:** Add this cell:

```python
# ============================================================================
# PHASE 3, STEP 3.1: Create Frozen CNN Base
# ============================================================================
print("\n" + "="*70)
print("PHASE 3: FINE-TUNING THE FULL MODEL (TWO-STAGE TRAINING)")
print("="*70)

print("\nSTEP 3.1: Creating frozen CNN base...")

# Re-create CNN-only architecture
cnn_base = create_cnn_only_model(
    input_shape=(WINDOW_SIZE, NUM_FEATURES),
    num_classes=NUM_CLASSES
)

# Load best weights from Phase 2 training
cnn_base.load_weights('cnn_only_best_model.h5')
print("✅ Loaded trained CNN weights from Phase 2")

# Remove the classifier layers (the "whack off the last layer" step)
# We keep only the convolutional feature extractor
cnn_base.pop()  # Remove Dense output layer
cnn_base.pop()  # Remove Dropout
cnn_base.pop()  # Remove GlobalAveragePooling1D

# Freeze the convolutional base
cnn_base.trainable = False

print("✅ CNN base created and frozen")
print(f"   Total params: {cnn_base.count_params():,}")
print(f"   Trainable params: {sum([tf.size(w).numpy() for w in cnn_base.trainable_weights]):,}")
print(f"   Non-trainable params: {sum([tf.size(w).numpy() for w in cnn_base.non_trainable_weights]):,}")

print("\nFrozen CNN base architecture:")
cnn_base.summary()
```

**Success Criteria:**
- Code executes without errors
- Summary shows convolutional layers as non-trainable
- `trainable_params` should be 0 for the base

#### Step 3.2: Build Full Model with Frozen Base

**Purpose:** Stack LSTM and Dense layers on top of frozen CNN base.

**Action:** Add this cell:

```python
# ============================================================================
# PHASE 3, STEP 3.2: Build Full Model with Frozen Base
# ============================================================================
print("\n" + "="*70)
print("STEP 3.2: Adding LSTM and Dense layers on frozen CNN base")
print("="*70)

def build_composite_model(frozen_base, num_classes):
    """
    Build full model with frozen CNN base and trainable LSTM/Dense head.
    """
    model = keras.Sequential([
        frozen_base,  # Frozen CNN base is first layer
        
        # Same LSTM and Dense layers from original model
        layers.LSTM(64, return_sequences=True, name='lstm_1'),
        layers.Dropout(0.3, name='dropout_1'),
        layers.LSTM(32, name='lstm_2'),
        layers.Dropout(0.3, name='dropout_2'),
        layers.Dense(64, activation='relu', name='dense_1'),
        layers.Dropout(0.3, name='dropout_3'),
        layers.Dense(num_classes, activation='softmax', name='output')
    ], name='Fine_Tuned_Model')
    
    return model

final_model = build_composite_model(cnn_base, NUM_CLASSES)

final_model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001, clipnorm=1.0),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print("✅ Final composite model built")
print(f"   Total params: {final_model.count_params():,}")
print(f"   Trainable params: {sum([tf.size(w).numpy() for w in final_model.trainable_weights]):,}")
print(f"   Non-trainable params: {sum([tf.size(w).numpy() for w in final_model.non_trainable_weights]):,}")

print("\nFull model architecture:")
final_model.summary()

# Verify CNN base is frozen
print("\n" + "="*60)
print("VERIFICATION: CNN base should be frozen")
print("="*60)
for layer in final_model.layers:
    if hasattr(layer, 'layers'):  # Sequential model
        print(f"\n{layer.name}:")
        for sublayer in layer.layers:
            trainable_str = "✅ trainable" if sublayer.trainable else "🔒 frozen"
            print(f"  {sublayer.name}: {trainable_str}")
    else:
        trainable_str = "✅ trainable" if layer.trainable else "🔒 frozen"
        print(f"{layer.name}: {trainable_str}")
```

**Success Criteria:**
- Model summary shows CNN base as single layer with 0 trainable params
- New LSTM and Dense layers have trainable parameters
- Verification shows CNN layers are frozen (🔒)

#### Step 3.3: Train Classifier Head (Fine-Tuning)

**Purpose:** Train only LSTM/Dense layers to interpret features from stable CNN base.

**Action:** Add this cell:

```python
# ============================================================================
# PHASE 3, STEP 3.3: Train Classifier Head (Fine-Tuning)
# ============================================================================
print("\n" + "="*70)
print("STEP 3.3: Fine-tuning - Training LSTM and Dense layers")
print("="*70)

print("\n🚀 Starting fine-tuning stage...")
print("Training only LSTM and Dense layers")
print("CNN base is frozen and provides stable features")
print("Class weights are now SAFE to use (won't destabilize CNN gradients)")

# Define callbacks for fine-tuning
final_callbacks = [
    keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=15,
        restore_best_weights=True,
        verbose=1
    ),
    keras.callbacks.ModelCheckpoint(
        'final_model_best.h5',
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    ),
    keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=7,
        min_lr=1e-7,
        verbose=1
    )
]

history_final = final_model.fit(
    X_train,
    y_train,
    validation_data=(X_val, y_val),
    epochs=100,  # Can train longer now
    batch_size=32,
    class_weight=class_weights,  # Safe to use class weights now!
    callbacks=final_callbacks,
    verbose=1
)

# Plot training history
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# Accuracy plot
axes[0, 0].plot(history_final.history['accuracy'], label='Train Accuracy')
axes[0, 0].plot(history_final.history['val_accuracy'], label='Val Accuracy')
axes[0, 0].set_title('Fine-Tuned Model: Accuracy')
axes[0, 0].set_xlabel('Epoch')
axes[0, 0].set_ylabel('Accuracy')
axes[0, 0].legend()
axes[0, 0].grid(True)

# Loss plot
axes[0, 1].plot(history_final.history['loss'], label='Train Loss')
axes[0, 1].plot(history_final.history['val_loss'], label='Val Loss')
axes[0, 1].set_title('Fine-Tuned Model: Loss')
axes[0, 1].set_xlabel('Epoch')
axes[0, 1].set_ylabel('Loss')
axes[0, 1].legend()
axes[0, 1].grid(True)

# Compare all phases
epochs_toy = range(1, len(history_toy.history['val_accuracy']) + 1)
epochs_cnn = range(1, len(history_cnn_only.history['val_accuracy']) + 1)
epochs_final = range(1, len(history_final.history['val_accuracy']) + 1)

axes[1, 0].plot(epochs_toy, history_toy.history['val_accuracy'], 
               label='Phase 1: Toy Dataset', marker='o')
axes[1, 0].plot(epochs_cnn, history_cnn_only.history['val_accuracy'], 
               label='Phase 2: CNN-Only', marker='s')
axes[1, 0].plot(epochs_final, history_final.history['val_accuracy'], 
               label='Phase 3: Fine-Tuned', marker='^')
axes[1, 0].set_title('Comparison: All Phases')
axes[1, 0].set_xlabel('Epoch')
axes[1, 0].set_ylabel('Validation Accuracy')
axes[1, 0].legend()
axes[1, 0].grid(True)

# Final summary
final_val_acc = max(history_final.history['val_accuracy'])
final_train_acc = max(history_final.history['accuracy'])
axes[1, 1].axis('off')
summary_text = f"""
WATSON'S TWO-STAGE FINE-TUNING RESULTS

Phase 1 (Sandbox):
  Best Val Accuracy: {max(history_toy.history['val_accuracy'])*100:.2f}%
  
Phase 2 (CNN-Only):
  Best Val Accuracy: {max(history_cnn_only.history['val_accuracy'])*100:.2f}%
  
Phase 3 (Fine-Tuned):
  Best Train Accuracy: {final_train_acc*100:.2f}%
  Best Val Accuracy: {final_val_acc*100:.2f}%
  
Status: {'✅ SUCCESS!' if final_val_acc > 0.85 else '⚠️  REVIEW NEEDED'}
"""
axes[1, 1].text(0.1, 0.5, summary_text, fontsize=12, family='monospace',
               verticalalignment='center')

plt.tight_layout()
plt.show()

print("\n" + "="*70)
print("PHASE 3 COMPLETE")
print("="*70)
print(f"Final validation accuracy: {final_val_acc*100:.2f}%")

if final_val_acc > 0.85:
    print("✅ SUCCESS: Model trained successfully!")
    print("   Proceeding to final evaluation...")
else:
    print("⚠️  Model performance below expected threshold")
    print("   Review training logs and consider adjustments")
```

**Success Criteria:**
- Model trains successfully without collapsing
- Validation accuracy high and stable
- No single class dominates predictions

---

## 4.0 Final Evaluation

**Purpose:** Confirm success of the procedure with comprehensive testing.

**Action:** Add this cell:

```python
# ============================================================================
# FINAL EVALUATION
# ============================================================================
print("\n" + "="*70)
print("FINAL EVALUATION")
print("="*70)

# Evaluate on test set
test_loss, test_accuracy = final_model.evaluate(X_test, y_test, verbose=0)
print(f"\n📊 Test Accuracy: {test_accuracy*100:.2f}%")
print(f"📊 Test Loss: {test_loss:.4f}")

# Get predictions
y_pred = final_model.predict(X_test, verbose=0)
y_pred_classes = np.argmax(y_pred, axis=1)

# Classification report
from sklearn.metrics import classification_report, confusion_matrix

print("\n" + "="*70)
print("CLASSIFICATION REPORT")
print("="*70)
print(classification_report(y_test, y_pred_classes, target_names=GESTURES))

# Confusion matrix
cm = confusion_matrix(y_test, y_pred_classes)
cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

plt.figure(figsize=(10, 8))
sns.heatmap(cm_normalized, annot=True, fmt='.2f', cmap='Blues',
           xticklabels=GESTURES, yticklabels=GESTURES)
plt.title('Normalized Confusion Matrix\nWatson\'s Two-Stage Fine-Tuning')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.tight_layout()
plt.show()

# Per-class analysis
print("\n" + "="*70)
print("PER-CLASS PERFORMANCE ANALYSIS")
print("="*70)

from sklearn.metrics import precision_recall_fscore_support

precision, recall, f1, support = precision_recall_fscore_support(
    y_test, y_pred_classes, average=None
)

print(f"\n{'Gesture':<10} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Support':<10}")
print("-" * 70)
for i, gesture in enumerate(GESTURES):
    print(f"{gesture:<10} {precision[i]:>10.2%}  {recall[i]:>10.2%}  "
          f"{f1[i]:>10.2%}  {support[i]:>8d}")

# Success criteria check
print("\n" + "="*70)
print("SUCCESS CRITERIA CHECK")
print("="*70)

all_recall_good = all(r > 0.70 for r in recall)
overall_good = test_accuracy > 0.85

print(f"\n✓ Overall accuracy > 85%: {'✅ PASS' if overall_good else '❌ FAIL'}")
print(f"✓ All classes recall > 70%: {'✅ PASS' if all_recall_good else '❌ FAIL'}")

if overall_good and all_recall_good:
    print("\n" + "="*70)
    print("🎉 WATSON'S TWO-STAGE FINE-TUNING: SUCCESS!")
    print("="*70)
    print("\nYour journey from a failing model to a working prototype is complete.")
    print("\nModel is ready for:")
    print("  - Download to Google Drive")
    print("  - Deployment to watch application")
    print("  - Real-time gesture recognition")
else:
    print("\n⚠️  Model performance below success criteria")
    print("Consider:")
    print("  - Collecting more training data")
    print("  - Adjusting hyperparameters")
    print("  - Reviewing data preprocessing")
```

**Expected Outcome:**
- High-performance model (validation accuracy > 85-90%)
- All gestures correctly classified
- Classification report shows good precision/recall for all classes

---

## 5.0 Model Saving and Deployment

```python
# Save the final model
final_model.save('/content/drive/MyDrive/silksong_data/watson_fine_tuned_model.h5')
print("✅ Model saved to Google Drive")

# Also save to Colab for immediate download
final_model.save('watson_fine_tuned_model.h5')

from google.colab import files
files.download('watson_fine_tuned_model.h5')
print("✅ Model available for download")
```

## 6.0 Success Criteria

- [ ] Phase 1: Sandbox model achieves >60% validation accuracy
- [ ] Phase 2: CNN-only model achieves >80% validation accuracy
- [ ] Phase 3: Fine-tuned model achieves >85% validation accuracy
- [ ] All gestures show >70% recall in classification report
- [ ] No single class dominates predictions
- [ ] Model is stable and doesn't collapse during training

## 7.0 Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed guidance on:
- Phase 1 failures
- Phase 2 issues
- Phase 3 problems
- Data quality issues
- Hyperparameter tuning

## 8.0 References

- Professor Watson's methodology
- Andrej Karpathy's "Recipe for Training Neural Networks"
- Transfer learning best practices
- Fine-tuning strategies for imbalanced data
