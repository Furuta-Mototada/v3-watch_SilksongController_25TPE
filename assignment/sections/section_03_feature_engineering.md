# Section 3: Feature Engineering and Preprocessing

## Statistical Feature Extraction

The system converts raw time-series sensor data into fixed-length feature vectors using statistical aggregation. This transformation is necessary because machine learning classifiers require fixed-dimensional inputs, while raw sensor windows have variable lengths.

### Feature Categories

The feature extraction computes **8 features per sensor axis** across 6 axes (accel_x/y/z, gyro_x/y/z), yielding 48 total features.

### Time-Domain Statistics

For each sensor axis, compute:

**Basic statistics:**
$$
\begin{aligned}
\mu &= \frac{1}{N}\sum_{i=1}^{N} x_i && \text{(Mean)} \\
\sigma &= \sqrt{\frac{1}{N}\sum_{i=1}^{N} (x_i - \mu)^2} && \text{(Standard deviation)} \\
x_{\min} &= \min(x_1, ..., x_N) && \text{(Minimum value)} \\
x_{\max} &= \max(x_1, ..., x_N) && \text{(Maximum value)}
\end{aligned}
$$

**Higher-order moments:**
$$
\begin{aligned}
\text{Skewness} &= \frac{1}{N}\sum_{i=1}^{N} \left(\frac{x_i - \mu}{\sigma}\right)^3 \\
\text{Kurtosis} &= \frac{1}{N}\sum_{i=1}^{N} \left(\frac{x_i - \mu}{\sigma}\right)^4 - 3
\end{aligned}
$$

These capture the shape and distribution of the sensor signal during the gesture.

### Frequency-Domain Features

Apply Fast Fourier Transform (FFT) to extract frequency characteristics:

$$
\text{FFT}(x)[k] = \sum_{n=0}^{N-1} x[n] \cdot e^{-i2\pi kn/N}
$$

From the magnitude spectrum $|\text{FFT}(x)|$, compute:

$$
\begin{aligned}
\text{FFT}_{\max} &= \max(|\text{FFT}(x)|) && \text{(Peak frequency power)} \\
\text{FFT}_{\text{mean}} &= \frac{1}{N/2}\sum_{k=0}^{N/2} |\text{FFT}(x)[k]| && \text{(Average spectral content)}
\end{aligned}
$$

Frequency features help distinguish gestures with different temporal patterns (e.g., walk has periodic ~2Hz oscillation, jump has sharp impulse).

### Implementation

```python
from scipy.fft import rfft
from scipy.stats import skew, kurtosis
import numpy as np

def extract_features_from_dataframe(df):
    features = {}
    
    for axis in ["accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z"]:
        signal = df[axis].dropna()
        
        if len(signal) > 0:
            # Time-domain features
            features[f"{axis}_mean"] = signal.mean()
            features[f"{axis}_std"] = signal.std()
            features[f"{axis}_min"] = signal.min()
            features[f"{axis}_max"] = signal.max()
            features[f"{axis}_skew"] = skew(signal)
            features[f"{axis}_kurtosis"] = kurtosis(signal)
            
            # Frequency-domain features
            if len(signal) > 2:
                fft_vals = np.abs(rfft(signal.to_numpy()))[: len(signal) // 2]
                if len(fft_vals) > 0:
                    features[f"{axis}_fft_max"] = fft_vals.max()
                    features[f"{axis}_fft_mean"] = fft_vals.mean()
    
    return features
```

### Feature Vector Structure

Final feature vector (48 dimensions):

| Feature Category | Count | Examples |
|-----------------|-------|----------|
| Mean | 6 | `accel_x_mean`, `gyro_z_mean` |
| Std Dev | 6 | `accel_x_std`, `gyro_z_std` |
| Min | 6 | `accel_x_min`, `gyro_z_min` |
| Max | 6 | `accel_x_max`, `gyro_z_max` |
| Skewness | 6 | `accel_x_skew`, `gyro_z_skew` |
| Kurtosis | 6 | `accel_x_kurtosis`, `gyro_z_kurtosis` |
| FFT Max | 6 | `accel_x_fft_max`, `gyro_z_fft_max` |
| FFT Mean | 6 | `accel_x_fft_mean`, `gyro_z_fft_mean` |

## Data Preprocessing

### Train/Test Split

Split data into training and testing sets:

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.3,      # 70% train, 30% test
    random_state=42,    # Reproducibility
    stratify=y          # Maintain class proportions
)
```

Stratified splitting ensures both train and test sets have similar class distributions.

### Feature Normalization

Apply StandardScaler to normalize features:

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)  # Fit on training data
X_test_scaled = scaler.transform(X_test)         # Apply to test data
```

StandardScaler performs z-score normalization:

$$
x_{\text{scaled}} = \frac{x - \mu_{\text{train}}}{\sigma_{\text{train}}}
$$

Where $\mu_{\text{train}}$ and $\sigma_{\text{train}}$ are computed from training data only. This prevents test set information from leaking into the model.

**Why normalize?**

Raw features have different scales:
- `accel_x_mean`: ~0-2 m/s²
- `accel_x_fft_max`: ~0-50 FFT magnitude units

Without normalization, SVM would be dominated by large-magnitude features. Normalization ensures all features contribute equally to the decision boundary.

### Handling Missing Values

The feature extraction handles missing data:

```python
signal = df[axis].dropna()  # Remove NaN values
if len(signal) > 0:
    # Compute features
```

This prevents errors from incomplete sensor readings while retaining valid data.

### Feature Ordering

Feature names are sorted alphabetically to ensure consistent ordering:

```python
feature_names = sorted(list(features.keys()))
```

This is critical because machine learning models expect features in the same order during training and inference. The feature names are saved with the trained model:

```python
import joblib
joblib.dump(feature_names, 'models/feature_names_binary.pkl')
```

### Preprocessing Pipeline Summary

Complete preprocessing workflow:

```python
# 1. Load data
X, y, feature_names = load_data(data_dir, classes)

# 2. Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# 3. Normalize features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 4. Save scaler and feature names for deployment
joblib.dump(scaler, 'models/feature_scaler_binary.pkl')
joblib.dump(feature_names, 'models/feature_names_binary.pkl')
```

This ensures:
- Training and test data are properly separated
- Feature scaling is consistent between training and deployment
- Feature ordering matches across all stages

### Deployment Preprocessing

During real-time inference, apply identical preprocessing:

```python
# Load saved preprocessor
scaler = joblib.load('models/feature_scaler_binary.pkl')
feature_names = joblib.load('models/feature_names_binary.pkl')

# Extract features from real-time data
features = extract_features_from_dataframe(df)
feature_vector = [features.get(name, 0) for name in feature_names]

# Normalize
feature_vector_scaled = scaler.transform([feature_vector])

# Predict
prediction = model.predict(feature_vector_scaled)
```

This maintains consistency between offline training and online deployment.

---

## References

- SciPy FFT: https://docs.scipy.org/doc/scipy/reference/fft.html
- SciPy Statistics: https://docs.scipy.org/doc/scipy/reference/stats.html
- scikit-learn StandardScaler: https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html
- scikit-learn train_test_split: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html
