# Phase III: Machine Learning Pipeline

This phase transforms the raw sensor data collected in Phase II into a trained gesture recognition model.

## Overview

The ML pipeline is implemented in a comprehensive Jupyter Notebook: **`CS156_Silksong_Watch.ipynb`**

This notebook documents the complete journey from raw IMU sensor data to a deployable gesture classification model.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `pandas`, `numpy` - Data manipulation
- `scikit-learn` - Machine learning
- `scipy` - Signal processing
- `joblib` - Model serialization
- `jupyter` - Notebook environment
- `matplotlib`, `seaborn` - Visualization

### 2. Ensure Training Data Exists

The notebook expects training data in this structure:

```
training_data/
└── session_YYYYMMDD_HHMMSS/
    ├── punch_forward_sample01.csv
    ├── punch_forward_sample02.csv
    ├── jump_quick_sample01.csv
    └── ... (all gesture samples)
```

If you don't have training data yet:
```bash
python src/data_collector.py
```

### 3. Run the Notebook

```bash
jupyter notebook CS156_Silksong_Watch.ipynb
```

Or use JupyterLab:
```bash
jupyter lab CS156_Silksong_Watch.ipynb
```

## Pipeline Stages

The notebook is organized into the following sections:

### 1. Environment Setup
- Import required libraries
- Configure visualization settings
- Set random seeds for reproducibility

### 2. Data Loading & Exploration
- Load CSV files from all training sessions
- Explore data distribution
- Validate data quality
- Visualize gesture and sensor distributions

### 3. Feature Engineering
- Extract time-domain features (mean, std, min, max, etc.)
- Extract frequency-domain features (FFT, dominant frequencies)
- Compute statistical features (skewness, kurtosis)
- Create cross-sensor features (magnitude, correlations)
- **Result**: ~60+ features per gesture sample

### 4. Model Training
- Train/test split (80/20) with stratification
- Feature scaling using StandardScaler
- **Primary Model**: Support Vector Machine (SVM) with RBF kernel
- **Alternative Model**: Random Forest (for comparison)
- Hyperparameter tuning via GridSearchCV
- 5-fold cross-validation

### 5. Model Evaluation
- Test set performance metrics
- Classification reports
- Confusion matrices
- Model comparison visualizations
- Cross-validation analysis

### 6. Model Serialization
- Save trained model: `models/gesture_classifier.pkl`
- Save feature scaler: `models/feature_scaler.pkl`
- Save feature names: `models/feature_names.pkl`
- Save metadata: `models/model_metadata.json`

### 7. Validation
- Load saved models
- Test prediction pipeline
- Verify deployment readiness

## Model Architecture

### Primary: Support Vector Machine (SVM)

**Why SVM?**
- Excellent for high-dimensional feature spaces
- Non-linear decision boundaries via RBF kernel
- Strong theoretical foundations
- Good generalization with proper tuning
- Efficient for real-time prediction

**Hyperparameters:**
- `C`: Regularization parameter (grid search: [0.1, 1, 10, 100])
- `gamma`: Kernel coefficient (grid search: ['scale', 'auto', 0.001, 0.01, 0.1])
- `kernel`: RBF (Radial Basis Function)

**Optimization:**
- GridSearchCV with 5-fold cross-validation
- Scoring metric: accuracy
- Probability estimates enabled for confidence thresholding

## Feature Engineering Details

### Acceleration Features (30 features)
For each axis (x, y, z):
- Mean, Std, Min, Max, Range, Median
- Skewness, Kurtosis
- Peak count
- FFT max, Dominant frequency, FFT mean

### Gyroscope Features (24 features)
For each axis (x, y, z):
- Mean, Std, Max absolute, Range
- Skewness, Kurtosis
- RMS (root mean square)
- FFT max

### Rotation Features (12 features)
For quaternion components (x, y, z, w):
- Mean, Std, Range

### Cross-Sensor Features (6 features)
- Acceleration magnitude: mean, max, std
- Gyroscope magnitude: mean, max, std

**Total: ~60+ features per gesture**

## Performance Expectations

Based on typical IMU gesture recognition tasks:

- **Target Accuracy**: >85% on test set
- **Target F1-Score**: >0.80 (weighted)
- **Real-time Latency**: <100ms per prediction
- **Confidence Threshold**: 0.7 (70%) for gesture execution

## Output Files

After running the notebook, the following files are created:

```
models/
├── gesture_classifier.pkl          # Trained SVM model
├── feature_scaler.pkl              # StandardScaler for normalization
├── feature_names.pkl               # List of feature names (for reference)
├── random_forest_classifier.pkl    # Alternative RF model
└── model_metadata.json             # Model performance metrics
```

## Next Steps: Phase IV Deployment

Once the model is trained, proceed to Phase IV to integrate it into the real-time controller:

1. **Update `src/udp_listener.py`**:
   - Load trained model and scaler
   - Create sensor data buffer (sliding window)
   - Implement feature extraction
   - Predict gestures with confidence thresholding
   - Execute keyboard actions

2. **Test real-time performance**:
   - Run the controller with live sensor data
   - Validate prediction accuracy
   - Tune confidence thresholds
   - Optimize latency

See `docs/Phase_II/ML_PIPELINE_PREVIEW.md` for code examples.

## Troubleshooting

### No training data found

**Error**: `❌ Training data directory not found: training_data`

**Solution**: Run the data collection script first:
```bash
python src/data_collector.py
```

### Import errors

**Error**: `ModuleNotFoundError: No module named 'sklearn'`

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Low model accuracy

**Possible causes**:
- Insufficient training data (need 5+ samples per gesture)
- Inconsistent gesture execution
- Sensor calibration issues

**Solutions**:
- Collect more training data
- Follow gesture instructions carefully during collection
- Ensure watch is worn consistently (same wrist, same position)

### Notebook kernel crashes

**Possible causes**:
- Insufficient memory
- Large dataset

**Solutions**:
- Increase available memory
- Process data in batches
- Reduce cross-validation folds

## References

- **Data Collection Guide**: `docs/Phase_II/DATA_COLLECTION_GUIDE.md`
- **ML Pipeline Preview**: `docs/Phase_II/ML_PIPELINE_PREVIEW.md`
- **Project README**: `README.md`

## Watson Preferred Checklist

The notebook follows the Watson Preferred methodology:

- [x] Clear problem statement and objectives
- [x] Data loading and exploration with visualizations
- [x] Feature engineering with justification
- [x] Model selection with rationale
- [x] Hyperparameter tuning methodology
- [x] Comprehensive evaluation metrics
- [x] Model serialization for deployment
- [x] Validation and testing procedures
- [x] Documentation and next steps

---

**Happy Training! 🎮🤖**
