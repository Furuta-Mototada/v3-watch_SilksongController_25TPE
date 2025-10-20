# Section 6: Model Training

## Training Procedure

The model training process follows standard scikit-learn workflow:

```python
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
import joblib

# 1. Prepare data
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 2. Initialize model
model = SVC(kernel='rbf', C=1.0, gamma='scale', random_state=42)

# 3. Train model
model.fit(X_train_scaled, y_train)

# 4. Evaluate
train_score = model.score(X_train_scaled, y_train)
test_score = model.score(X_test_scaled, y_test)

print(f"Training accuracy: {train_score:.3f}")
print(f"Test accuracy: {test_score:.3f}")

# 5. Save model
joblib.dump(model, 'models/gesture_classifier.pkl')
joblib.dump(scaler, 'models/feature_scaler.pkl')
```

## Training Separate Models

The system trains two independent models:

### Binary Model (Walk vs Idle)

```python
# Load binary data
X_binary, y_binary, features_binary = load_data(
    data_dir="data/button_collected",
    classes=["walk", "idle"]
)

# Train binary classifier
model_binary = train_and_evaluate(
    X_binary, y_binary, 
    classes=["walk", "idle"],
    model_name="Binary",
    models_dir="models",
    feature_names=features_binary
)
```

### Multiclass Model (All Actions)

```python
# Load multiclass data
X_multi, y_multi, features_multi = load_data(
    data_dir="data/button_collected",
    classes=["jump", "punch", "turn_left", "turn_right", "idle"]
)

# Train multiclass classifier
model_multi = train_and_evaluate(
    X_multi, y_multi,
    classes=["jump", "punch", "turn_left", "turn_right", "idle"],
    model_name="Multiclass",
    models_dir="models",
    feature_names=features_multi
)
```

## Training Function

Complete training implementation from `SVM_Local_Training.py`:

```python
def train_and_evaluate(X, y, classes, model_name, models_dir, feature_names):
    print(f"\n{'='*20} Training {model_name} Classifier {'='*20}")
    
    # Check class distribution
    unique, counts = np.unique(y, return_counts=True)
    min_samples = counts.min()
    
    print(f"Dataset: {len(X)} samples, {len(unique)} classes")
    for cls_idx, count in zip(unique, counts):
        print(f"  - {classes[cls_idx]}: {count} samples")
    
    # Train/test split with stratification
    if min_samples < 10:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=None
        )
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )
    
    # Normalize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train SVM
    model = SVC(kernel='rbf', C=1.0, gamma='scale', random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    train_acc = model.score(X_train_scaled, y_train)
    test_acc = model.score(X_test_scaled, y_test)
    
    print(f"\nTraining Accuracy: {train_acc:.3f}")
    print(f"Test Accuracy: {test_acc:.3f}")
    
    # Generate predictions for confusion matrix
    y_pred = model.predict(X_test_scaled)
    
    # Classification report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=classes))
    
    # Save model artifacts
    model_path = Path(models_dir) / f"gesture_classifier_{model_name.lower()}.pkl"
    scaler_path = Path(models_dir) / f"feature_scaler_{model_name.lower()}.pkl"
    features_path = Path(models_dir) / f"feature_names_{model_name.lower()}.pkl"
    
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    joblib.dump(feature_names, features_path)
    
    print(f"\nModel saved to: {model_path}")
    
    return model
```

## Training Output Example

```
==================== Training Binary Classifier ====================
Dataset: 60 samples, 2 classes
  - walk: 30 samples
  - idle: 30 samples

Training Accuracy: 0.952
Test Accuracy: 0.889

Classification Report:
              precision    recall  f1-score   support

        walk       0.90      0.90      0.90         9
        idle       0.88      0.88      0.88         9

    accuracy                           0.89        18
   macro avg       0.89      0.89      0.89        18
weighted avg       0.89      0.89      0.89        18

Model saved to: models/gesture_classifier_binary.pkl
```

## Hyperparameter Selection

The system uses default hyperparameters that work well for this dataset size and feature dimensionality:

- **C = 1.0**: Standard regularization strength
- **gamma = 'scale'**: Automatically set to $1/(n_{features} \times X.var())$
- **kernel = 'rbf'**: Radial basis function for nonlinear boundaries

These defaults are effective because:
1. Features are normalized (StandardScaler)
2. Dataset is relatively small (50-100 samples)
3. Feature space is moderate-dimensional (48 features)

## Training Time

Typical training times on standard hardware (Intel Core i7):
- Binary model: 0.1-0.5 seconds
- Multiclass model: 0.2-1.0 seconds

SVM training is fast enough for rapid iteration and experimentation.

## Model Validation

After training, verify the model loads correctly:

```python
# Test model loading
loaded_model = joblib.load('models/gesture_classifier_binary.pkl')
loaded_scaler = joblib.load('models/feature_scaler_binary.pkl')
loaded_features = joblib.load('models/feature_names_binary.pkl')

# Verify prediction works
test_features = extract_features_from_dataframe(test_df)
test_vector = [test_features.get(name, 0) for name in loaded_features]
test_vector_scaled = loaded_scaler.transform([test_vector])
prediction = loaded_model.predict(test_vector_scaled)

print(f"Prediction: {classes[prediction[0]]}")
```

This ensures the saved model can be used for deployment without errors.

---

## References

- scikit-learn SVC: https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html
- scikit-learn model persistence: https://scikit-learn.org/stable/model_persistence.html
- joblib documentation: https://joblib.readthedocs.io/
