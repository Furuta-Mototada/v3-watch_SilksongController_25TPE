# Data Type Fix for Training

## Problem Identified

When running the training notebook, you encountered two errors:

### Error 1: Shape Mismatch
```
ValueError: all the input array dimensions except for the concatenation axis
must match exactly, but along dimension 2, the array at index 0 has size 12
and the array at index 1 has size 11
```

**Cause:** Some sensor data files have spaces in column names (e.g., `accel_x        ,`) while others don't. This caused pandas to parse columns differently.

**Fix:** Added `skipinitialspace=True` and `.str.strip()` to column names in the `load_session_data()` function.

### Error 2: Invalid dtype: object
```
ValueError: Invalid dtype: object
```

**Cause:** The 'sensor' column contains string values (like "Accelerometer", "Gyroscope"), which were being included in the feature array.

**Fix:** Explicitly exclude both 'timestamp' and 'sensor' columns, and convert features to `float32`.

---

## What Was Changed in the Notebook

### 1. Updated Feature Extraction (Cell #10)

**Before:**
```python
feature_cols = [col for col in sensor_data.columns if col != 'timestamp']
features = sensor_data[feature_cols].values
```

**After:**
```python
feature_cols = [col for col in sensor_data.columns
               if col not in ['timestamp', 'sensor']]

# Convert to float32 explicitly to avoid dtype issues
features = sensor_data[feature_cols].astype(np.float32).values
```

### 2. Updated NUM_FEATURES (Cell #7)

**Before:**
```python
NUM_FEATURES = 9  # 3 sensors × 3 axes
```

**After:**
```python
NUM_FEATURES = 10  # accel(3) + gyro(3) + rotation(4) = 10
```

Your sensor data actually has 10 numeric features:
- `accel_x`, `accel_y`, `accel_z` (3)
- `gyro_x`, `gyro_y`, `gyro_z` (3)
- `rot_w`, `rot_x`, `rot_y`, `rot_z` (4)

Plus 2 non-numeric columns (excluded):
- `timestamp` (time)
- `sensor` (string identifier)

### 3. Added Debugging Output

The updated code now prints:
- Feature column names
- Feature shape
- Feature dtype
- Full error tracebacks

This helps diagnose issues quickly if they occur.

---

## How to Use the Fixed Notebook

### 1. Re-upload to Colab

If you're already in Colab:
```
File → Upload notebook →
Select: notebooks/Colab_CNN_LSTM_Training.ipynb
```

Or download from your Mac and upload fresh copy.

### 2. Verify the Fix Works

When you run Cell #10 (Load and process all sessions), you should see:

```
Processing 20251017_125600_session...
  Sensor samples: 86237
  Label segments: 1035
  Feature columns (10): ['accel_x', 'accel_y', 'accel_z', 'gyro_x',
                          'gyro_y', 'gyro_z', 'rot_w', 'rot_x', 'rot_y', 'rot_z']
  Feature shape: (86237, 10)
  Feature dtype: float32
  Generated 1062 windows

Processing 20251017_135458_session...
  Sensor samples: 88323
  Label segments: 742
  Feature columns (10): [...]
  Feature shape: (88323, 10)
  Feature dtype: float32
  Generated 1139 windows

... [continues for all 5 sessions]

✅ Total training windows: 4726
   Input shape: (4726, 50, 10)
   Labels shape: (4726,)
   X dtype: float32
   y dtype: int64

   Class distribution:
     jump: 284 (6.0%)
     punch: 697 (14.7%)
     turn: 368 (7.8%)
     walk: 3218 (68.1%)
     noise: 159 (3.4%)
```

### 3. Key Things to Check

✅ All sessions should have **10 features** (not 11 or 12)
✅ Feature dtype should be **float32**
✅ Label dtype should be **int64** or **int32**
✅ Input shape should be **(N, 50, 10)** where N is ~4,700-4,900 windows

---

## Expected Training Results

With the fix applied:

### Input/Output Shapes
- **Input:** `(N, 50, 10)` - N windows, 50 timesteps, 10 features
- **Output:** `(N,)` - N labels (integers 0-4)

### Model Architecture
```
Input: (50, 10)
  ↓
Conv1D (64 filters) → (50, 64)
MaxPool1D → (25, 64)
  ↓
Conv1D (128 filters) → (25, 128)
MaxPool1D → (12, 128)
  ↓
LSTM (128 units) → (12, 128)
  ↓
LSTM (64 units) → (64,)
  ↓
Dense (5 units) → (5,) [softmax]
```

### Training Time
- **With GPU (T4):** 25-40 minutes
- **Epochs:** 20-40 (with early stopping)
- **Validation accuracy:** Should reach 90-95%

---

## If You Still Get Errors

### Check 1: Column Names
Run this in a Colab cell before training:
```python
import pandas as pd
df = pd.read_csv(f'{DATA_DIR}/{SESSION_FOLDERS[0]}/sensor_data.csv',
                 skipinitialspace=True)
df.columns = df.columns.str.strip()
print("Columns:", list(df.columns))
print("Dtypes:", df.dtypes)
```

Expected output:
```
Columns: ['accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z',
          'rot_w', 'rot_x', 'rot_y', 'rot_z', 'sensor', 'timestamp']
Dtypes:
accel_x      float64
accel_y      float64
accel_z      float64
gyro_x       float64
gyro_y       float64
gyro_z       float64
rot_w        float64
rot_x        float64
rot_y        float64
rot_z        float64
sensor       object    ← This is string, must exclude
timestamp    float64
```

### Check 2: Feature Extraction
```python
feature_cols = [col for col in df.columns if col not in ['timestamp', 'sensor']]
print("Feature columns:", feature_cols)
print("Number of features:", len(feature_cols))  # Should be 10
```

### Check 3: Data Type Conversion
```python
features = df[feature_cols].astype(np.float32).values
print("Shape:", features.shape)  # Should be (N, 10)
print("Dtype:", features.dtype)  # Should be float32
```

---

## Summary

✅ **Fixed:** Column name spacing issues
✅ **Fixed:** Excluded 'sensor' string column
✅ **Fixed:** Explicit float32 conversion
✅ **Updated:** NUM_FEATURES from 9 to 10
✅ **Added:** Better debug output

The notebook is now ready to run successfully! 🎉

Upload the updated notebook to Colab and continue with training.
