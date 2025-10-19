# Section 4: Classification Task and Data Splits

## Classification Problem Definition

This project implements gesture recognition as a supervised classification task with two separate models:

### Binary Classification (Locomotion)
$$
f_{\text{binary}}: \mathbb{R}^{48} \rightarrow \{0, 1\}
$$

Classes:
- 0: `idle` - stationary state
- 1: `walk` - walking motion

Purpose: Determines if the player is moving or stationary.

### Multiclass Classification (Actions)
$$
f_{\text{multi}}: \mathbb{R}^{48} \rightarrow \{0, 1, 2, 3, 4\}
$$

Classes:
- 0: `jump` - upward gesture
- 1: `punch` - forward strike
- 2: `turn_left` - counterclockwise rotation
- 3: `turn_right` - clockwise rotation
- 4: `idle` - rest state

Purpose: Detects discrete action commands.

## Data Splitting Strategy

### Stratified Train/Test Split

The system uses stratified random splitting to maintain class balance:

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.3,        # 30% for testing
    random_state=42,      # Fixed seed for reproducibility
    stratify=y            # Maintain class proportions
)
```

**Split ratio**: 70% training / 30% testing

**Stratification** ensures each set has proportional representation of all classes. For example, if the full dataset has 60% idle and 40% walk samples, both train and test sets will maintain this 60/40 ratio.

### Handling Small Datasets

When sample counts are low, the code adapts the splitting strategy:

```python
# Check class distribution
unique, counts = np.unique(y, return_counts=True)
min_samples = counts.min()

if min_samples < 10:
    # Skip stratification if any class has < 10 samples
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=random_state, stratify=None
    )
else:
    # Use stratified split when sufficient samples exist
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=random_state, stratify=y
    )
```

This prevents errors when a class has too few samples for stratified splitting.

### Multiple Random States

The training script tests multiple random seeds to ensure stable results:

```python
for attempt in range(max_attempts):
    random_state = 42 + attempt
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=random_state, stratify=y
    )
    # Train and evaluate model
```

This verifies that model performance is consistent across different data splits.

## Evaluation Metrics

### Classification Report

The system computes per-class metrics:

```python
from sklearn.metrics import classification_report

report = classification_report(y_test, y_pred, target_names=classes)
print(report)
```

Output includes:
- **Precision**: $\frac{TP}{TP + FP}$ - fraction of predicted positives that are correct
- **Recall**: $\frac{TP}{TP + FN}$ - fraction of actual positives that are detected
- **F1-score**: $2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$ - harmonic mean of precision and recall

### Confusion Matrix

Visualizes classification performance:

```python
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=classes, yticklabels=classes)
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.title('Confusion Matrix')
plt.savefig('confusion_matrix.png')
```

The confusion matrix shows where the model confuses classes. Diagonal elements represent correct classifications; off-diagonal elements show misclassifications.

### Cross-Validation

Optional cross-validation for more robust performance estimates:

```python
from sklearn.model_selection import cross_val_score

scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
print(f"Cross-validation accuracy: {scores.mean():.3f} ± {scores.std():.3f}")
```

5-fold cross-validation splits training data into 5 subsets, training on 4 and validating on 1, repeating for all combinations.

## Dataset Statistics

Typical dataset characteristics for this system:

**Binary classification:**
- Total samples: 40-80
- Idle samples: 20-40
- Walk samples: 20-40

**Multiclass classification:**
- Total samples: 50-100
- Jump samples: 10-20
- Punch samples: 10-20
- Turn left samples: 10-20
- Turn right samples: 10-20
- Idle samples: 10-20

These relatively small datasets work well with SVM classifiers, which perform effectively with limited training data.

---

## References

- scikit-learn train_test_split: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html
- scikit-learn classification_report: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html
- scikit-learn confusion_matrix: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html
