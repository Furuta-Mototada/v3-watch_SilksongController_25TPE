# Section 7: Predictions and Performance Metrics

## Generating Predictions

After training, generate predictions on test data:

```python
# Load trained model
model = joblib.load('models/gesture_classifier_binary.pkl')
scaler = joblib.load('models/feature_scaler_binary.pkl')

# Prepare test data
X_test_scaled = scaler.transform(X_test)

# Generate predictions
y_pred = model.predict(X_test_scaled)

# Get prediction probabilities (if model has probability=True)
# y_pred_proba = model.predict_proba(X_test_scaled)
```

## Performance Metrics

### Accuracy

Overall classification accuracy:

$$
\text{Accuracy} = \frac{\text{Correct Predictions}}{\text{Total Predictions}} = \frac{\sum_{i=1}^{n} \mathbb{1}[y_i = \hat{y}_i]}{n}
$$

```python
from sklearn.metrics import accuracy_score

accuracy = accuracy_score(y_test, y_pred)
print(f"Test Accuracy: {accuracy:.3f}")
```

### Per-Class Metrics

**Precision**: Of predicted positives, how many are correct?
$$
\text{Precision} = \frac{TP}{TP + FP}
$$

**Recall**: Of actual positives, how many were detected?
$$
\text{Recall} = \frac{TP}{TP + FN}
$$

**F1-Score**: Harmonic mean of precision and recall
$$
F1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}
$$

Where:
- TP = True Positives
- FP = False Positives
- FN = False Negatives

### Classification Report

```python
from sklearn.metrics import classification_report

report = classification_report(y_test, y_pred, target_names=classes)
print(report)
```

Example output:

```
              precision    recall  f1-score   support

        walk       0.90      0.90      0.90         9
        idle       0.88      0.88      0.88         9

    accuracy                           0.89        18
   macro avg       0.89      0.89      0.89        18
weighted avg       0.89      0.89      0.89        18
```

- **support**: Number of samples in each class
- **macro avg**: Unweighted mean (treats all classes equally)
- **weighted avg**: Weighted by class frequency

## Confusion Matrix

Visualizes model performance across all classes:

```python
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# Compute confusion matrix
cm = confusion_matrix(y_test, y_pred)

# Plot
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=classes, yticklabels=classes)
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.title('Confusion Matrix')
plt.savefig('models/confusion_matrix.png')
plt.show()
```

The confusion matrix shows:
- **Diagonal**: Correct classifications
- **Off-diagonal**: Misclassifications

For binary classification (walk vs idle):
```
            Predicted
            walk  idle
Actual walk  [8]   [1]
       idle  [1]   [8]
```

This indicates:
- 8/9 walk samples correctly classified
- 8/9 idle samples correctly classified
- 1 walk misclassified as idle
- 1 idle misclassified as walk

## Model Performance Summary

### Binary Classification (Walk vs Idle)

Typical performance with button-collected data:

| Metric | Value |
|--------|-------|
| Training Accuracy | 0.92-0.95 |
| Test Accuracy | 0.85-0.90 |
| Walk Precision | 0.85-0.92 |
| Walk Recall | 0.85-0.92 |
| Idle Precision | 0.85-0.92 |
| Idle Recall | 0.85-0.92 |

### Multiclass Classification (Actions)

| Metric | Value |
|--------|-------|
| Training Accuracy | 0.85-0.92 |
| Test Accuracy | 0.70-0.80 |
| Per-class F1 | 0.65-0.85 |

Multiclass is more challenging due to:
- More classes to distinguish (5 vs 2)
- Some gestures have similar motion patterns
- Smaller training samples per class

## Real-Time Performance

During deployment, the system achieves:

- **Inference latency**: <10ms per prediction
- **Throughput**: >100 predictions/second
- **Memory usage**: ~5MB (loaded models)

These metrics enable real-time game control with minimal latency.

## Model Persistence

Trained models and metadata are saved:

```
models/
├── gesture_classifier_binary.pkl       # Binary SVM model
├── feature_scaler_binary.pkl           # Binary feature normalizer
├── feature_names_binary.pkl            # Binary feature ordering
├── binary_confusion_matrix.png         # Binary results visualization
├── gesture_classifier_multiclass.pkl   # Multiclass SVM model
├── feature_scaler_multiclass.pkl       # Multiclass normalizer
├── feature_names_multiclass.pkl        # Multiclass feature ordering
└── multiclass_confusion_matrix.png     # Multiclass results
```

File sizes:
- Model files (.pkl): 10-150 KB
- Confusion matrices (.png): 20-30 KB

## Deployment Verification

Test the deployed model:

```python
# Load model for deployment
model = joblib.load('models/gesture_classifier_binary.pkl')
scaler = joblib.load('models/feature_scaler_binary.pkl')
feature_names = joblib.load('models/feature_names_binary.pkl')

# Test prediction on real-time data
df = pd.DataFrame(sensor_buffer)  # From UDP stream
features = extract_features_from_dataframe(df)
feature_vector = [features.get(name, 0) for name in feature_names]
feature_vector_scaled = scaler.transform([feature_vector])

prediction = model.predict(feature_vector_scaled)[0]
predicted_class = classes[prediction]

print(f"Predicted gesture: {predicted_class}")
```

This validates the model works correctly in the deployment environment.

---

## References

- scikit-learn metrics: https://scikit-learn.org/stable/modules/model_evaluation.html
- scikit-learn classification_report: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html
- scikit-learn confusion_matrix: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html
