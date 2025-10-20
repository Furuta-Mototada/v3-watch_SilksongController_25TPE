# Section 5: Model Selection and Mathematical Foundations

## Support Vector Machine (SVM) Classifier

This project uses Support Vector Machines with Radial Basis Function (RBF) kernels for gesture classification.

### SVM Mathematical Formulation

**Objective**: Find the hyperplane that maximally separates two classes in feature space.

For linearly separable data, SVM solves:

$$
\begin{aligned}
\text{minimize} \quad & \frac{1}{2} \|w\|^2 \\
\text{subject to} \quad & y_i(w \cdot x_i + b) \geq 1 \quad \forall i
\end{aligned}
$$

Where:
- $w \in \mathbb{R}^d$ is the weight vector (normal to hyperplane)
- $b \in \mathbb{R}$ is the bias term
- $x_i$ is the feature vector for sample $i$
- $y_i \in \{-1, +1\}$ is the class label

**Decision function**:
$$
f(x) = \text{sign}(w \cdot x + b)
$$

### Soft-Margin SVM

For non-separable data, introduce slack variables $\xi_i$:

$$
\begin{aligned}
\text{minimize} \quad & \frac{1}{2} \|w\|^2 + C \sum_{i=1}^{n} \xi_i \\
\text{subject to} \quad & y_i(w \cdot x_i + b) \geq 1 - \xi_i, \quad \xi_i \geq 0 \quad \forall i
\end{aligned}
$$

The parameter $C$ controls the trade-off between:
- Maximizing margin (small $\|w\|$)
- Minimizing classification errors ($\sum \xi_i$)

**Large $C$**: Prioritize correct classification (low training error, risk overfitting)
**Small $C$**: Allow more errors, prefer larger margin (may underfit)

### RBF Kernel

The RBF (Gaussian) kernel maps features to infinite-dimensional space:

$$
K(x_i, x_j) = \exp\left(-\gamma \|x_i - x_j\|^2\right)
$$

Where:
- $\gamma$ controls kernel width
- $\|x_i - x_j\|^2$ is squared Euclidean distance

**Large $\gamma$**: Narrow kernel, follows training data closely (risk overfitting)
**Small $\gamma$**: Wide kernel, smoother decision boundary (may underfit)

### Multiclass Extension

For $K$ classes, use One-vs-Rest (OvR) strategy:
1. Train $K$ binary classifiers
2. Classifier $k$ separates class $k$ from all others
3. Final prediction: $\hat{y} = \arg\max_k f_k(x)$

## Model Implementation

```python
from sklearn.svm import SVC

# Create SVM classifier
model = SVC(
    kernel='rbf',                    # Radial basis function kernel
    C=1.0,                           # Regularization parameter
    gamma='scale',                   # Gamma = 1 / (n_features * X.var())
    decision_function_shape='ovr',   # One-vs-Rest for multiclass
    random_state=42                  # Reproducibility
)

# Train model
model.fit(X_train_scaled, y_train)

# Make predictions
y_pred = model.predict(X_test_scaled)
```

### Hyperparameter Selection

The default configuration uses:
- **C = 1.0**: Balanced regularization
- **gamma = 'scale'**: Automatically computed as $\frac{1}{n_{\text{features}} \cdot \text{var}(X)}$

These defaults work well for normalized features and moderate-sized datasets.

### Model Training Process

1. **Feature scaling**: Apply StandardScaler (Section 3)
2. **Model initialization**: Create SVC with specified hyperparameters
3. **Training**: Call `model.fit(X_train, y_train)`
4. **Prediction**: Use `model.predict(X_test)` for evaluation

### Why SVM for This Task

**Advantages**:
- Works well with small datasets (50-100 samples)
- Effective in high-dimensional spaces (48 features)
- Robust to overfitting with proper regularization
- Fast inference (important for real-time control)

**Limitations**:
- Requires feature engineering (manual feature design)
- Sensitive to feature scaling (requires normalization)
- Limited capacity for complex nonlinear patterns

For this gesture recognition task with button-collected data, SVM provides an effective baseline that:
- Trains quickly (<1 minute on CPU)
- Achieves reasonable accuracy (70-85%)
- Deploys efficiently (real-time prediction <10ms)

## Model Persistence

Save trained models for deployment:

```python
import joblib

# Save model
joblib.dump(model, 'models/gesture_classifier_binary.pkl')

# Save preprocessing artifacts
joblib.dump(scaler, 'models/feature_scaler_binary.pkl')
joblib.dump(feature_names, 'models/feature_names_binary.pkl')
```

Load for inference:

```python
model = joblib.load('models/gesture_classifier_binary.pkl')
scaler = joblib.load('models/feature_scaler_binary.pkl')
feature_names = joblib.load('models/feature_names_binary.pkl')
```

This ensures deployment uses the exact same model and preprocessing as training.

---

## References

- Cortes, C., & Vapnik, V. (1995). "Support-vector networks." *Machine Learning*, 20(3), 273-297.
- scikit-learn SVC: https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html
- scikit-learn SVM guide: https://scikit-learn.org/stable/modules/svm.html
