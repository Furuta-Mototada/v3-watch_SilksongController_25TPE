# ML Pipeline Preview (Phase III)

This document previews how the collected data will be used in Phase III for machine learning model training.

## Data Flow

Phase II Output              | Phase III Processing           | Phase IV Deployment
:--------------------------- | :----------------------------- | :-------------------------
`training_data/`               | **Feature Engineering**            | **Real-time Controller**
├── `session_*/`            →  | ├── Time-domain features    →  | ├── Load trained model
│   ├── `*.csv`                | ├── Frequency features         | ├── Stream sensor data
│   └── `metadata.json`        | ├── Statistical features       | ├── Extract features
|                            | └── Window sliding             | └── Predict gesture
|                            |                                |
|                            | **Model Training**             |
|                            | ├── Train/test split           |
|                            | ├── Cross-validation           |
|                            | └── Hyperparameter tuning      |

## Example ML Workflow

### Step 1: Load and Merge Data

```python
import pandas as pd
import glob
import os

def load_session_data(session_dir):
   """Load all CSV files from a session."""
   csv_files = glob.glob(os.path.join(session_dir, "*.csv"))
   data_frames = []

   for csv_file in csv_files:
       df = pd.read_csv(csv_file)
       data_frames.append(df)

   # Combine all recordings
   combined = pd.concat(data_frames, ignore_index=True)
   return combined

# Load multiple sessions if available
session_dirs = glob.glob("training_data/session_*")
all_data = pd.concat([load_session_data(d) for d in session_dirs])

print(f"Total recordings: {len(all_data)}")
print(f"Unique gestures: {all_data['gesture'].unique()}")
print(f"Samples per gesture: {all_data.groupby('gesture')['sample'].nunique()}")
```

### Step 2: Feature Engineering

```python
import numpy as np
from scipy import stats
from scipy.fft import fft

def extract_window_features(window_df):
   """Extract features from a time window of sensor data."""
   features = {}

   # Separate by sensor type
   accel = window_df[window_df['sensor'] == 'linear_acceleration']
   gyro = window_df[window_df['sensor'] == 'gyroscope']
   rot = window_df[window_df['sensor'] == 'rotation_vector']

   # Acceleration features
   if len(accel) > 0:
       for axis in ['accel_x', 'accel_y', 'accel_z']:
           values = accel[axis].dropna()
           if len(values) > 0:
               # Time-domain statistics
               features[f'{axis}_mean'] = values.mean()
               features[f'{axis}_std'] = values.std()
               features[f'{axis}_max'] = values.max()
               features[f'{axis}_min'] = values.min()
               features[f'{axis}_range'] = values.max() - values.min()
               features[f'{axis}_skew'] = stats.skew(values)
               features[f'{axis}_kurtosis'] = stats.kurtosis(values)

               # Peak detection
               features[f'{axis}_peak_count'] = len(values[values > values.mean() + 2*values.std()])

               # Frequency domain (FFT)
               fft_vals = np.abs(fft(values))[:len(values)//2]
               features[f'{axis}_fft_max'] = fft_vals.max()
               features[f'{axis}_dominant_freq'] = fft_vals.argmax()

   # Gyroscope features (similar structure)
   if len(gyro) > 0:
       for axis in ['gyro_x', 'gyro_y', 'gyro_z']:
           values = gyro[axis].dropna()
           if len(values) > 0:
               features[f'{axis}_mean'] = values.mean()
               features[f'{axis}_std'] = values.std()
               features[f'{axis}_max_abs'] = values.abs().max()

   # Rotation features
   if len(rot) > 0:
       # Quaternion to Euler angles
       for comp in ['rot_x', 'rot_y', 'rot_z', 'rot_w']:
           values = rot[comp].dropna()
           if len(values) > 0:
               features[f'{comp}_mean'] = values.mean()
               features[f'{comp}_change'] = values.iloc[-1] - values.iloc

   # Cross-sensor features
   if len(accel) > 0:
       # Overall acceleration magnitude
       mag = np.sqrt(
           accel['accel_x']**2 +
           accel['accel_y']**2 +
           accel['accel_z']**2
       )
       features['accel_magnitude_mean'] = mag.mean()
       features['accel_magnitude_max'] = mag.max()

   return features

# Apply to each recording
features_list = []
labels_list = []

for gesture in all_data['gesture'].unique():
   gesture_data = all_data[all_data['gesture'] == gesture]

   for sample in gesture_data['sample'].unique():
       sample_data = gesture_data[gesture_data['sample'] == sample]

       # Extract features from this sample
       features = extract_window_features(sample_data)
       features_list.append(features)
       labels_list.append(gesture)

# Create feature matrix
X = pd.DataFrame(features_list).fillna(0)
y = pd.Series(labels_list)

print(f"Feature matrix shape: {X.shape}")
print(f"Number of features: {X.shape}")
```

### Step 3: Train Models

```python
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# Split data
X_train, X_test, y_train, y_test = train_test_split(
   X, y, test_size=0.2, random_state=42, stratify=y
)

# Normalize features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train Random Forest
rf_model = RandomForestClassifier(
   n_estimators=100,
   max_depth=10,
   random_state=42
)
rf_model.fit(X_train_scaled, y_train)

# Evaluate
y_pred = rf_model.predict(X_test_scaled)
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Cross-validation
cv_scores = cross_val_score(rf_model, X_train_scaled, y_train, cv=5)
print(f"\nCross-validation accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")

# Feature importance
feature_importance = pd.DataFrame({
   'feature': X.columns,
   'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

print("\nTop 10 Most Important Features:")
print(feature_importance.head(10))

# Save model and scaler
joblib.dump(rf_model, 'models/gesture_classifier.pkl')
joblib.dump(scaler, 'models/feature_scaler.pkl')
print("\nModel saved!")
```

### Step 4: Real-time Deployment

```python
# In udp_listener.py (Phase IV integration)

import joblib
from collections import deque

# Load trained model
model = joblib.load('models/gesture_classifier.pkl')
scaler = joblib.load('models/feature_scaler.pkl')

# Buffer for collecting sensor data
sensor_buffer = deque(maxlen=150)  # ~3 seconds at 50Hz

def process_sensor_data(parsed_json):
   """Process incoming sensor data and predict gesture."""

   # Add to buffer
   sensor_buffer.append(parsed_json)

   # Check if we have enough data for prediction
   if len(sensor_buffer) >= 100:  # Minimum window size
       # Convert buffer to DataFrame
       buffer_df = pd.DataFrame(list(sensor_buffer))

       # Extract features
       features = extract_window_features(buffer_df)

       # Convert to feature vector
       feature_vector = pd.DataFrame([features]).fillna(0)
       feature_vector = feature_vector.reindex(columns=X.columns, fill_value=0)

       # Scale features
       feature_vector_scaled = scaler.transform(feature_vector)

       # Predict gesture
       prediction = model.predict(feature_vector_scaled)
       confidence = model.predict_proba(feature_vector_scaled).max()

       # Only act if confidence is high
       if confidence > 0.7:
           execute_gesture(prediction)
           sensor_buffer.clear()  # Clear buffer after prediction

       return prediction, confidence

   return None, 0.0

def execute_gesture(gesture):
   """Execute the predicted gesture."""
   if gesture == "punch_forward" or gesture == "punch_upward":
       keyboard.press(KEY_MAP["attack"])
       keyboard.release(KEY_MAP["attack"])
   elif gesture == "jump_quick" or gesture == "jump_sustained":
       keyboard.press(KEY_MAP["jump"])
       keyboard.release(KEY_MAP["jump"])
   elif gesture == "turn_left":
       facing_direction = "left"
   elif gesture == "turn_right":
       facing_direction = "right"
   # ... etc
```

## Alternative Approaches

### Deep Learning (Neural Networks)

```python
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

# Prepare sequential data (time series)
def prepare_sequences(data, sequence_length=100):
   """Prepare time-series sequences for LSTM."""
   # Implementation details...
   pass

X_sequences, y_sequences = prepare_sequences(all_data)

# Build LSTM model
model = Sequential([
   LSTM(64, input_shape=(sequence_length, num_features), return_sequences=True),
   Dropout(0.2),
   LSTM(32),
   Dropout(0.2),
   Dense(len(gesture_classes), activation='softmax')
])

model.compile(
   optimizer='adam',
   loss='categorical_crossentropy',
   metrics=['accuracy']
)

# Train
history = model.fit(
   X_sequences, y_sequences,
   epochs=50,
   batch_size=32,
   validation_split=0.2
)

# Save
model.save('models/lstm_gesture_classifier.h5')
```

### Online Learning

For personalization, use online learning to adapt to individual users:

```python
from sklearn.linear_model import SGDClassifier

# Initialize with partial_fit
online_model = SGDClassifier(loss='log_loss')

# Train incrementally
for batch in data_batches:
   X_batch, y_batch = prepare_batch(batch)
   online_model.partial_fit(X_batch, y_batch, classes=gesture_classes)

# User can provide corrections in real-time
# Model adapts to their specific movement patterns
```

## Performance Expectations

Based on similar IMU gesture recognition projects:

| Metric                | Expected Range |
|-----------------------|----------------|
| Overall Accuracy      | 85-95%         |
| Precision (per class) | 80-95%         |
| Recall (per class)    | 80-95%         |
| Inference Time        | 10-50 ms       |
| False Positive Rate   | 5-15%          |

**Confusion Prone Pairs:**

- `punch_forward` ↔ `punch_upward` (both involve forward motion)
- `turn_left` ↔ `turn_right` (symmetrical motions)
- `jump_quick` ↔ `jump_sustained` (timing differences)

**Robust Detections:**

- `rest` (no motion baseline)
- `walk_in_place` (periodic pattern)

## Evaluation Metrics

```python
from sklearn.metrics import (
   accuracy_score,
   precision_recall_fscore_support,
   cohen_kappa_score
)

# Calculate comprehensive metrics
accuracy = accuracy_score(y_test, y_pred)
precision, recall, f1, support = precision_recall_fscore_support(
   y_test, y_pred, average='weighted'
)
kappa = cohen_kappa_score(y_test, y_pred)

print(f"Accuracy: {accuracy:.3f}")
print(f"Precision: {precision:.3f}")
print(f"Recall: {recall:.3f}")
print(f"F1 Score: {f1:.3f}")
print(f"Cohen's Kappa: {kappa:.3f}")

# Per-class metrics
per_class = precision_recall_fscore_support(
   y_test, y_pred, average=None, labels=gesture_classes
)

metrics_df = pd.DataFrame({
   'gesture': gesture_classes,
   'precision': per_class,
   'recall': per_class,
   'f1': per_class,
   'support': per_class
})

print("\nPer-Gesture Performance:")
print(metrics_df)
```

## Hyperparameter Tuning

```python
from sklearn.model_selection import GridSearchCV

# Define parameter grid
param_grid = {
   'n_estimators':,
   'max_depth': [5, 10, 15, None],
   'min_samples_split':,
   'min_samples_leaf':
}

# Grid search
grid_search = GridSearchCV(
   RandomForestClassifier(random_state=42),
   param_grid,
   cv=5,
   scoring='accuracy',
   n_jobs=-1
)

grid_search.fit(X_train_scaled, y_train)

print(f"Best parameters: {grid_search.best_params_}")
print(f"Best cross-validation score: {grid_search.best_score_:.3f}")

# Use best model
best_model = grid_search.best_estimator_
```

## Data Augmentation

To improve robustness, augment training data:

```python
def augment_sensor_data(df, noise_level=0.1):
   """Add noise to sensor data for augmentation."""
   augmented = df.copy()

   # Add Gaussian noise to acceleration
   for col in ['accel_x', 'accel_y', 'accel_z']:
       if col in augmented.columns:
           noise = np.random.normal(0, noise_level, len(augmented))
           augmented[col] = augmented[col] + noise

   # Add noise to gyroscope
   for col in ['gyro_x', 'gyro_y', 'gyro_z']:
       if col in augmented.columns:
           noise = np.random.normal(0, noise_level * 0.1, len(augmented))
           augmented[col] = augmented[col] + noise

   return augmented

# Create augmented versions
augmented_samples = []
for i in range(3):  # 3x augmentation
   augmented = augment_sensor_data(all_data)
   augmented_samples.append(augmented)

# Combine original and augmented data
training_data = pd.concat([all_data] + augmented_samples)
```

## Visualization Tools

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Plot confusion matrix
def plot_confusion_matrix(y_true, y_pred, classes):
   cm = confusion_matrix(y_true, y_pred)

   plt.figure(figsize=(10, 8))
   sns.heatmap(
       cm, annot=True, fmt='d', cmap='Blues',
       xticklabels=classes, yticklabels=classes
   )
   plt.title('Confusion Matrix')
   plt.ylabel('True Label')
   plt.xlabel('Predicted Label')
   plt.tight_layout()
   plt.savefig('confusion_matrix.png')
   plt.show()

# Plot feature importance
def plot_feature_importance(model, feature_names, top_n=20):
   importance_df = pd.DataFrame({
       'feature': feature_names,
       'importance': model.feature_importances_
   }).sort_values('importance', ascending=False).head(top_n)

   plt.figure(figsize=(12, 6))
   plt.barh(importance_df['feature'], importance_df['importance'])
   plt.xlabel('Importance')
   plt.title(f'Top {top_n} Feature Importances')
   plt.tight_layout()
   plt.savefig('feature_importance.png')
   plt.show()

# Plot learning curves
def plot_learning_curves(train_sizes, train_scores, val_scores):
   plt.figure(figsize=(10, 6))
   plt.plot(train_sizes, train_scores.mean(axis=1), label='Training score')
   plt.plot(train_sizes, val_scores.mean(axis=1), label='Validation score')
   plt.fill_between(train_sizes,
                    train_scores.mean(axis=1) - train_scores.std(axis=1),
                    train_scores.mean(axis=1) + train_scores.std(axis=1),
                    alpha=0.1)
   plt.fill_between(train_sizes,
                    val_scores.mean(axis=1) - val_scores.std(axis=1),
                    val_scores.mean(axis=1) + val_scores.std(axis=1),
                    alpha=0.1)
   plt.xlabel('Training Examples')
   plt.ylabel('Score')
   plt.title('Learning Curves')
   plt.legend()
   plt.grid(True)
   plt.savefig('learning_curves.png')
   plt.show()
```

## Next Steps for Phase III

- **Collect multiple sessions** - More data improves model robustness
- **Experiment with features** - Try different feature engineering approaches
- **Compare algorithms** - Test Random Forest, SVM, Neural Networks
- **Optimize inference time** - Ensure real-time performance (<50ms)
- **User testing** - Validate model with different users
- **Iterative improvement** - Collect more data for problematic gestures

This preview demonstrates the complete ML pipeline from raw sensor data to deployed gesture recognition. Phase III will implement and refine these techniques for production use.
