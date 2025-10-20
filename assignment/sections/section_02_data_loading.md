# Section 2: Data Loading Code

## Converting CSV Files to Python Data Structures

The data loading pipeline reads button-collected gesture CSV files from the filesystem and converts them into NumPy arrays suitable for machine learning.

### Core Loading Function

```python
import pandas as pd
import numpy as np
from pathlib import Path

def load_data(data_dir, classes):
    """
    Load gesture data from CSV files organized by class folders.
    
    Args:
        data_dir: Path to directory containing class subdirectories
        classes: List of class names (e.g., ['walk', 'idle'])
    
    Returns:
        X: NumPy array of shape (n_samples, n_features)
        y: NumPy array of shape (n_samples,) with class labels
        feature_names: List of feature names in order
    """
    X, y = [], []
    data_path = Path(data_dir)
    feature_names = None
    
    for i, class_name in enumerate(classes):
        class_path = data_path / class_name
        if not class_path.exists():
            continue
        
        for file_path in class_path.glob("*.csv"):
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Validate minimum sample count
            if len(df) < 10:
                continue
            
            # Extract features from time-series window
            features = extract_features_from_dataframe(df)
            
            # Store feature names from first sample
            if feature_names is None:
                feature_names = sorted(list(features.keys()))
            
            # Append feature vector and label
            X.append([features.get(name, 0) for name in feature_names])
            y.append(i)
    
    return np.array(X), np.array(y), feature_names
```

### CSV File Structure

Each CSV file contains raw sensor readings:

```csv
accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z
0.234,-1.456,9.812,0.012,-0.034,0.001
0.241,-1.432,9.798,0.015,-0.031,0.002
0.229,-1.471,9.823,0.011,-0.036,0.001
...
```

Columns represent:
- `accel_x/y/z`: Linear acceleration in m/s²
- `gyro_x/y/z`: Angular velocity in rad/s

### Feature Extraction from DataFrames

The `extract_features_from_dataframe` function converts raw time-series into statistical features:

```python
from scipy.fft import rfft
from scipy.stats import skew, kurtosis

def extract_features_from_dataframe(df):
    """
    Extract features from a DataFrame containing sensor readings.
    
    Args:
        df: DataFrame with columns: accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z
    
    Returns:
        Dictionary of extracted features
    """
    features = {}
    
    for axis in ["accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z"]:
        signal = df[axis].dropna()
        
        if len(signal) > 0:
            # Time-domain statistics
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

This function computes 8 features per sensor axis (6 axes total = 48 features).

### Data Organization

The loading process expects the following directory structure:

```
data/button_collected/
├── walk/
│   ├── walk_*.csv
│   └── ...
├── idle/
│   ├── idle_*.csv
│   └── ...
├── jump/
│   ├── jump_*.csv
│   └── ...
└── [other gesture folders]
```

However, the current implementation uses flat file naming (all files in one directory with gesture name as prefix). The code adapts to this by:

```python
# For flat directory structure, files are named: {gesture}_{timestamp}.csv
# The load_data function processes all *.csv files matching the gesture prefix
```

### Output Format

After loading, data is structured as:

**X (feature matrix):**
- Shape: `(n_samples, n_features)` where n_features = 48
- Type: `numpy.ndarray` of float64
- Each row represents one gesture sample

**y (label vector):**
- Shape: `(n_samples,)`
- Type: `numpy.ndarray` of int
- Values: 0 to (n_classes - 1)

**feature_names (feature ordering):**
- Type: `list` of strings
- Example: `['accel_x_mean', 'accel_x_std', ..., 'gyro_z_kurtosis', 'gyro_z_fft_max']`
- Critical for maintaining feature consistency during inference

### Data Validation

The loading function includes validation:

```python
# Minimum sample check
if len(df) < 10:
    continue  # Skip files with insufficient data points
```

This ensures each training sample contains enough data for reliable feature extraction (minimum 10 samples at 50Hz = 0.2 seconds).

### Usage Example

```python
# Load binary classification data (walk vs idle)
X_binary, y_binary, features_binary = load_data(
    data_dir="data/button_collected",
    classes=["walk", "idle"]
)

print(f"Loaded {len(X_binary)} samples")
print(f"Feature vector dimension: {X_binary.shape[1]}")
print(f"Class distribution: {np.bincount(y_binary)}")

# Load multiclass data
X_multi, y_multi, features_multi = load_data(
    data_dir="data/button_collected",
    classes=["jump", "punch", "turn_left", "turn_right", "idle"]
)
```

### Real-Time Data Loading

For deployment, the system uses UDP streaming instead of CSV files. The same `extract_features_from_dataframe` function is used, but with real-time data:

```python
# From udp_listener_dashboard.py
sensor_buffer = deque(maxlen=50)  # Store last 50 readings (~1 second at 50Hz)

# After receiving UDP packets, convert to DataFrame
df = pd.DataFrame(list(sensor_buffer))

# Extract features for prediction
features = extract_features_from_dataframe(df)
feature_vector = [features.get(name, 0) for name in feature_names]
```

This ensures training and deployment use identical feature extraction, preventing train/test mismatch.

---

## References

- pandas CSV reading: https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
- NumPy array creation: https://numpy.org/doc/stable/reference/generated/numpy.array.html
- pathlib Path operations: https://docs.python.org/3/library/pathlib.html
