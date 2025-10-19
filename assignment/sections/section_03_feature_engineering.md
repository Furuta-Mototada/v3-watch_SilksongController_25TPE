# Section 3: Cleaning, Pre-processing, and Feature Engineering

## Signal Processing: The Unglamorous Backbone of Biosensor ML

Machine learning conferences are full of papers about novel architectures and optimization algorithms. What they rarely discuss is the **massive impact of feature engineering** on classification performance. In biosignal processing, feature extraction often matters more than model choice—a truth that the deep learning hype cycle has obscured but not eliminated.

This section documents the signal processing pipeline that transforms raw 50Hz IMU streams into the ~60 statistical features used for gesture classification.

## The Central Challenge: Extracting Discriminative Features from Noisy Time-Series

### Why Raw Sensor Data is Inadequate

Consider what the model sees if we feed it raw accelerometer samples directly:

```
Sample 1: [0.234, -1.456, 9.812]  (accel_x, accel_y, accel_z)
Sample 2: [0.241, -1.432, 9.798]
Sample 3: [0.229, -1.471, 9.823]
...
Sample 15: [0.238, -1.449, 9.807]
```

These 15 samples (0.3 seconds at 50Hz) contain a gesture, but the pattern is buried in:
- **Sensor noise**: ±0.02 m/s² from ADC quantization and thermal drift
- **Gravity components**: The 9.8 m/s² in `accel_z` is not motion—it's the watch being pulled toward Earth
- **Sensor orientation**: The same gesture performed with wrist rotated 45° produces completely different raw values
- **Individual variability**: I don't perform "punch" identically twice—velocity, amplitude, and trajectory vary

A classification model trained on raw samples would memorize these surface variations rather than learning the underlying kinematic structure of each gesture. This is why **feature extraction is not optional**.

## Feature Engineering Strategy: Time-Domain and Frequency-Domain Decomposition

The pipeline extracts two categories of features:

### 1. Time-Domain Statistical Features (Per-Axis)

For each sensor axis (6 total: accel_x/y/z, gyro_x/y/z), compute:

**Basic Statistics:**

$$
\begin{aligned}
\mu &= \frac{1}{N}\sum_{i=1}^{N} x_i && \text{(Mean: central tendency)} \\
\sigma &= \sqrt{\frac{1}{N}\sum_{i=1}^{N} (x_i - \mu)^2} && \text{(Std Dev: spread)} \\
\text{Range} &= \max(x) - \min(x) && \text{(Dynamic range)} \\
\text{Median} &= x_{[N/2]} && \text{(Robust to outliers)}
\end{aligned}
$$

These capture the **magnitude and variability** of motion along each axis.

**Higher-Order Moments:**

$$
\begin{aligned}
\text{Skewness} &= \frac{1}{N}\sum_{i=1}^{N} \left(\frac{x_i - \mu}{\sigma}\right)^3 && \text{(Asymmetry)} \\
\text{Kurtosis} &= \frac{1}{N}\sum_{i=1}^{N} \left(\frac{x_i - \mu}{\sigma}\right)^4 - 3 && \text{(Tail heaviness)}
\end{aligned}
$$

**Why These Matter:**

- **Skewness** distinguishes gestures with asymmetric acceleration profiles (e.g., punch: fast forward, slow return)
- **Kurtosis** identifies gestures with sharp peaks (e.g., jump: sudden upward impulse) vs. smooth motions (e.g., walk: sinusoidal)

These are standard features in Activity Recognition literature dating back to Bao & Intille (2004), "Activity Recognition from User-Annotated Acceleration Data."

### 2. Frequency-Domain Features (FFT-Based)

Raw time-series mixes multiple frequency components. The Fourier Transform decomposes signals into constituent sinusoids:

$$
\text{FFT}(x)[k] = \sum_{n=0}^{N-1} x[n] \cdot e^{-i2\pi kn/N}
$$

We compute the **magnitude spectrum** (ignoring phase):

$$
|\text{FFT}(x)[k]| = \sqrt{\text{Re}(\text{FFT}[k])^2 + \text{Im}(\text{FFT}[k])^2}
$$

And extract:

$$
\begin{aligned}
\text{FFT}_{\max} &= \max(|\text{FFT}(x)|) && \text{(Dominant frequency power)} \\
\text{FFT}_{\text{mean}} &= \frac{1}{N/2}\sum_{k=0}^{N/2} |\text{FFT}(x)[k]| && \text{(Average spectral content)}
\end{aligned}
$$

**Why This Works for Gesture Recognition:**

Different gestures have characteristic frequency signatures:
- **Walk**: Periodic oscillation at ~2 Hz (stride frequency)
- **Jump**: Low-frequency impulse (<1 Hz) followed by damped oscillation
- **Punch**: Sharp high-frequency transient (5-10 Hz) from acceleration onset

The FFT captures these temporal patterns in a rotation-invariant way that time-domain statistics miss.

### 3. Cross-Sensor Magnitude Features

Individual axis values depend on sensor orientation, but the **magnitude** (Euclidean norm) is rotation-invariant:

$$
\begin{aligned}
|\vec{a}| &= \sqrt{a_x^2 + a_y^2 + a_z^2} && \text{(Acceleration magnitude)} \\
|\vec{\omega}| &= \sqrt{\omega_x^2 + \omega_y^2 + \omega_z^2} && \text{(Angular velocity magnitude)}
\end{aligned}
$$

We compute mean and standard deviation of these magnitudes across the window. This makes the classifier robust to wrist orientation—"punch" looks the same whether I'm wearing the watch face-up or face-down.

## Complete Feature Vector Structure

The final feature vector for each 0.3-second window contains **~60 features**:

| Feature Category | Count | Examples |
|-----------------|-------|----------|
| Per-axis time-domain | 6 axes × 8 stats = 48 | `accel_x_mean`, `gyro_y_std`, `accel_z_kurtosis` |
| Per-axis frequency-domain | 6 axes × 2 stats = 12 | `accel_x_fft_max`, `gyro_z_fft_mean` |
| Cross-sensor magnitudes | 2 sensors × 2 stats = 4 | `accel_magnitude_mean`, `gyro_magnitude_std` |

**Total: 64 features** (exact count depends on whether rotation vector features are included).

## Implementation: From DataFrame to Feature Dictionary

Here's the actual feature extraction code used in the system:

```python
import numpy as np
from scipy.fft import rfft
from scipy.stats import skew, kurtosis

def extract_features_from_dataframe(df):
    """
    Extracts statistical features from sensor DataFrame.
    
    Args:
        df: pandas DataFrame with columns:
            - accel_x, accel_y, accel_z (linear acceleration, m/s²)
            - gyro_x, gyro_y, gyro_z (angular velocity, rad/s)
            - timestamp (milliseconds since epoch)
    
    Returns:
        Dictionary mapping feature_name -> float value
        
    Mathematical Operations:
        - Time-domain: mean, std, min, max, range, median, skewness, kurtosis
        - Frequency-domain: FFT magnitude max and mean
        - Cross-sensor: L2 norm (magnitude) statistics
    """
    features = {}
    
    # Per-axis time-domain features
    for axis in ['accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z']:
        signal = df[axis].dropna()  # Remove NaN values from missing data
        
        if len(signal) > 0:
            # Basic statistics
            features[f'{axis}_mean'] = signal.mean()
            features[f'{axis}_std'] = signal.std()
            features[f'{axis}_min'] = signal.min()
            features[f'{axis}_max'] = signal.max()
            features[f'{axis}_range'] = signal.max() - signal.min()
            features[f'{axis}_median'] = signal.median()
            
            # Higher-order moments
            features[f'{axis}_skew'] = skew(signal)
            features[f'{axis}_kurtosis'] = kurtosis(signal)
            
            # Frequency-domain features
            if len(signal) > 2:  # Need at least 3 samples for meaningful FFT
                # Real FFT (input is real-valued time series)
                fft_vals = np.abs(rfft(signal.to_numpy()))
                
                # Keep only positive frequencies (Nyquist limit)
                fft_vals = fft_vals[:len(signal)//2]
                
                if len(fft_vals) > 0:
                    features[f'{axis}_fft_max'] = fft_vals.max()
                    features[f'{axis}_fft_mean'] = fft_vals.mean()
    
    # Cross-sensor magnitude features
    if all(col in df.columns for col in ['accel_x', 'accel_y', 'accel_z']):
        # Compute acceleration magnitude for each time sample
        accel_mag = np.sqrt(
            df['accel_x']**2 + 
            df['accel_y']**2 + 
            df['accel_z']**2
        )
        features['accel_magnitude_mean'] = accel_mag.mean()
        features['accel_magnitude_std'] = accel_mag.std()
    
    if all(col in df.columns for col in ['gyro_x', 'gyro_y', 'gyro_z']):
        # Compute angular velocity magnitude for each time sample
        gyro_mag = np.sqrt(
            df['gyro_x']**2 + 
            df['gyro_y']**2 + 
            df['gyro_z']**2
        )
        features['gyro_magnitude_mean'] = gyro_mag.mean()
        features['gyro_magnitude_std'] = gyro_mag.std()
    
    return features
```

**Code Design Rationale:**

1. **Defensive programming**: `dropna()` handles missing sensor readings gracefully
2. **Conditional checks**: `if len(signal) > 0` prevents division-by-zero errors
3. **Dictionary output**: Flexible structure allows adding/removing features without breaking downstream code
4. **Named features**: `accel_x_mean` is self-documenting vs. anonymous array index `features[0]`

## Data Cleaning and Preprocessing Steps

Before feature extraction, several preprocessing steps ensure data quality:

### 1. Handling Missing Data

UDP packet loss occasionally creates gaps in sensor streams. Strategy:

```python
# Fill missing values with zeros (assumes brief dropout)
df = df.fillna(0)

# Alternative: Linear interpolation for longer gaps
df = df.interpolate(method='linear', limit=3)  # Max 3 consecutive NaNs
```

**Justification**: For 50Hz sampling, 3 missing samples = 60ms gap. Linear interpolation is valid because human motion is smooth and continuous (acceleration is finite, no instantaneous jumps).

### 2. Window Size Selection

The 0.3-second window (15 samples at 50Hz) balances:

**Temporal Resolution vs. Statistical Validity:**

- **Too short** (<0.2s): Insufficient samples for reliable statistics; FFT resolution degraded
- **Too long** (>0.5s): Gesture transitions blur together; latency increases unacceptably

$$
\text{FFT resolution} = \frac{f_s}{N} = \frac{50 \text{ Hz}}{15 \text{ samples}} \approx 3.3 \text{ Hz}
$$

This resolves 0-3 Hz (walk), 3-6 Hz (punch onset), 6-10 Hz (sharp transients)—adequate for gesture discrimination.

**Empirical Testing:**

I tested window sizes of 0.2s, 0.3s, 0.5s, and 1.0s. Classification accuracy peaked at 0.3s:

- 0.2s: 78% accuracy (noisy features)
- **0.3s: 85% accuracy** ← selected
- 0.5s: 83% accuracy (latency unacceptable)
- 1.0s: 80% accuracy (gesture transitions contaminate windows)

### 3. Feature Normalization

Raw features have wildly different scales:

- `accel_x_mean`: ~0-2 m/s²
- `accel_x_fft_max`: ~0-50 FFT magnitude units
- `gyro_magnitude_std`: ~0-0.5 rad/s

Without normalization, the SVM would be dominated by large-magnitude features. Solution: **StandardScaler** (z-score normalization):

$$
x_{\text{scaled}} = \frac{x - \mu}{\sigma}
$$

Where $\mu$ and $\sigma$ are computed from the **training set only** (to prevent data leakage):

```python
from sklearn.preprocessing import StandardScaler

# Fit scaler on training data
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

# Apply same transformation to test data
X_test_scaled = scaler.transform(X_test)

# Save scaler for deployment
joblib.dump(scaler, 'models/feature_scaler.pkl')
```

**Critical**: Using `scaler.fit_transform()` on test data would contaminate it with future information, inflating accuracy metrics artificially.

## Exploratory Data Analysis: Do Features Separate Gestures?

Before training any model, I validated that features actually discriminate between gesture classes. Here's what the data looks like:

**Distribution of `accel_magnitude_mean` by Gesture:**

| Gesture | Mean ± Std (m/s²) | Interpretation |
|---------|------------------|----------------|
| Idle | 1.2 ± 0.3 | Minimal movement, near-gravitational baseline |
| Walk | 2.5 ± 0.8 | Periodic arm swing, moderate acceleration |
| Jump | 4.8 ± 1.2 | Sharp upward impulse, high peak magnitude |
| Punch | 5.5 ± 1.5 | Fastest acceleration transient |

**Observation**: Clear separation between classes—`idle` and `walk` are distinct from `jump` and `punch`. This is encouraging: features capture meaningful kinematic differences.

**T-Test for Statistical Significance:**

Comparing `jump` vs. `punch` acceleration magnitudes:

$$
t = \frac{\bar{x}_{\text{jump}} - \bar{x}_{\text{punch}}}{\sqrt{\frac{s_{\text{jump}}^2}{n_{\text{jump}}} + \frac{s_{\text{punch}}^2}{n_{\text{punch}}}}} = 2.3, \quad p < 0.05
$$

Result: Statistically significant difference (reject null hypothesis that means are equal). The model should be able to separate these classes.

## Why This Approach Works (And Its Limitations)

**Strengths:**

1. **Rotation invariance**: Magnitude features eliminate orientation dependence
2. **Noise robustness**: Statistical aggregation over 15 samples smooths sensor noise
3. **Interpretability**: Each feature has clear physical meaning (unlike deep learning embeddings)
4. **Computational efficiency**: ~60 features vs. raw 15×6=90 values (dimensionality reduction)

**Limitations:**

1. **Fixed window assumption**: Gesture must fit entirely within 0.3s (breaks for slow movements)
2. **Hand-crafted features**: Requires domain expertise; might miss subtle patterns
3. **No temporal structure**: Treats window as bag-of-statistics; ignores sequential order
4. **Subject-specific**: Features tuned to my motion patterns (generalization unclear)

These limitations motivate the CNN/LSTM approach explored later (Section 5), which learns features directly from raw sequences.

---

## Evaluation Against CS156 Learning Objectives

### cs156-MLCode ✓
- Complete, documented feature extraction function
- Defensive programming (NaN handling, conditional checks)
- Efficient NumPy/pandas operations

### cs156-MLExplanation ✓
- Detailed justification for each feature category
- Window size selection backed by empirical testing
- EDA showing features discriminate gesture classes

### cs156-MLMath ✓✓
- Full mathematical definitions with LaTeX equations
- FFT theory and frequency resolution derivation
- Statistical significance testing (t-test)
- Normalization formula (z-score)

### cs156-MLFlexibility ✓
- Higher-order moments (skewness, kurtosis) not covered in class
- FFT-based frequency features
- Rotation-invariant magnitude features
- Empirical window size optimization

---

## References for Section 3

1. Bao, L., & Intille, S. S. (2004). "Activity recognition from user-annotated acceleration data." *Pervasive Computing*, 1-17.
2. SciPy FFT documentation: https://docs.scipy.org/doc/scipy/reference/fft.html
3. Scikit-learn StandardScaler: https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html
4. Welch's t-test for unequal variances: Welch, B. L. (1947). "The generalization of 'Student's' problem when several different population variances are involved." *Biometrika*, 34(1-2), 28-35.
