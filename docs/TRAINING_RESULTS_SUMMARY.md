# Training Results Summary

## Two-Stage Classification Architecture

This project uses a **two-stage classification approach** for better gesture recognition:

### Stage 1: Binary Classifier (Walking vs Not-Walking)
**Purpose**: Detect continuous walking motion  
**Test Accuracy**: 94.29% ✅  
**Model**: `models/gesture_classifier_binary.pkl`

**Performance**:
```
              precision    recall  f1-score   support
     walking       1.00      0.71      0.83         7
 not_walking       0.93      1.00      0.97        28

    accuracy                           0.94        35
```

**Analysis**:
- ✅ Excellent performance (94% accuracy)
- ✅ High precision for both classes
- ✅ 100% recall for not_walking (no false positives)
- ⚠️ Walking recall at 71% (some walking gestures classified as not_walking)

### Stage 2: Multi-class Classifier (Jump, Punch, Turn, Idle)
**Purpose**: Recognize discrete action gestures  
**Test Accuracy**: 57.14% ⚠️  
**Model**: `models/gesture_classifier_multiclass.pkl`

**Performance**:
```
              precision    recall  f1-score   support
        jump       0.33      0.14      0.20         7
       punch       0.50      0.29      0.36         7
        turn       0.75      0.86      0.80         7
        idle       0.54      1.00      0.70         7

    accuracy                           0.57        28
```

**Analysis**:
- ✅ Turn gesture performs best (80% F1-score)
- ✅ Idle has perfect recall (100%)
- ⚠️ Jump and Punch have low accuracy (needs more data)
- ⚠️ Overall accuracy (57%) needs improvement

## Recommendations for Improvement

### 1. Collect More Data
**Target**: 50-100 samples per gesture (currently 34-35)

**Priority gestures to collect**:
1. **Jump** (14% recall - critical!)
2. **Punch** (29% recall - needs work)
3. **Walk** (71% recall - could improve)

### 2. Apply Data Augmentation
Use the augmentation tool to expand minority classes:

```bash
python src/data_augmentation.py \
  --input data/organized_training/multiclass_classification \
  --output data/organized_training_augmented \
  --target-samples 50
```

This will:
- Add Gaussian noise
- Apply time warping
- Scale magnitudes
- Time shift samples

### 3. Try CNN-LSTM on Colab
Deep learning may capture temporal patterns better:

```bash
# Upload organized data to Google Drive
# Open notebooks/Silksong_Complete_Training_Colab.ipynb
# Set TRAINING_MODE = 'MULTICLASS'
# Enable GPU and run all cells
```

Expected improvement: 57% → 85-92% accuracy

### 4. Verify Gesture Consistency
Review your data collection:
- Are jump gestures consistent across samples?
- Is there overlap between punch and other gestures?
- Check CSV files for quality issues

```bash
python src/shared_utils/inspect_csv_data.py data/button_collected/jump*.csv
```

### 5. Hyperparameter Tuning
Try different SVM parameters:

```python
# In SVM_Local_Training.py, modify:
svm_multi = SVC(
    kernel='rbf',
    C=10.0,        # Increase regularization (was 1.0)
    gamma='auto',  # Or try specific values: 0.001, 0.01
    class_weight='balanced',  # Handle class imbalance
    random_state=RANDOM_SEED,
    probability=True
)
```

## Data Quality Analysis

### Current Distribution
```
Binary Classification:
  Walking: 34 samples
  Not-Walking: 139 samples
  Ratio: 1:4.1 (acceptable imbalance)

Multi-class Classification:
  Jump: 35 samples
  Punch: 34 samples
  Turn: 35 samples
  Idle: 35 samples
  Ratio: Balanced! ✅
```

### Why Multi-class Accuracy is Low

Despite balanced classes, accuracy is low because:

1. **Small Dataset**: 28 test samples (7 per class) is very small
2. **Gesture Similarity**: Jump/punch may have similar motion patterns
3. **Feature Engineering**: Hand-crafted features may not capture subtle differences
4. **Individual Variation**: Personal gesture style may vary between samples

### Expected Accuracy Ranges

Based on IMU gesture recognition literature:

| Dataset Size | Expected SVM Accuracy | Expected CNN-LSTM Accuracy |
|--------------|----------------------|---------------------------|
| 30-50 per class | 60-75% | 75-85% |
| 50-100 per class | 75-85% | 85-92% |
| 100+ per class | 85-92% | 92-98% |

**Current status**: 35 samples per class → 57% (below expected range)

## Next Steps

### Immediate Actions (Today)
1. ✅ Data is organized and models are trained
2. ✅ Test binary classifier (should work well at 94%)
3. ⚠️ Collect 15-20 more samples for jump and punch
4. 🔄 Re-train with augmented data

### Short-term (This Week)
1. Apply data augmentation
2. Re-train SVM with augmented data
3. Try CNN-LSTM on Colab
4. Compare model performance

### Long-term (Next Sprint)
1. Collect 50-100 samples per gesture
2. Implement two-stage prediction in controller
3. Add confidence thresholds
4. Live testing with game

## Model Files

Generated models are in `models/`:

```
models/
├── gesture_classifier_binary.pkl          # Binary SVM (94% accuracy)
├── feature_scaler_binary.pkl
├── feature_names_binary.pkl
├── gesture_classifier_multiclass.pkl      # Multi-class SVM (57% accuracy)
├── feature_scaler_multiclass.pkl
├── feature_names_multiclass.pkl
├── binary_confusion_matrix.png            # Visualization
└── multiclass_confusion_matrix.png        # Visualization
```

## Usage in Controller

Example two-stage prediction:

```python
import joblib
import numpy as np

# Load models
binary_clf = joblib.load('models/gesture_classifier_binary.pkl')
multi_clf = joblib.load('models/gesture_classifier_multiclass.pkl')
binary_scaler = joblib.load('models/feature_scaler_binary.pkl')
multi_scaler = joblib.load('models/feature_scaler_multiclass.pkl')

def predict_gesture(features):
    """Two-stage gesture prediction."""
    
    # Stage 1: Binary classification
    binary_features = binary_scaler.transform([features])
    is_walking = binary_clf.predict(binary_features)[0]
    binary_prob = binary_clf.predict_proba(binary_features)[0]
    
    if is_walking == 0:  # Walking
        return 'WALK', binary_prob[0]
    
    # Stage 2: Multi-class classification
    multi_features = multi_scaler.transform([features])
    action_idx = multi_clf.predict(multi_features)[0]
    action_prob = multi_clf.predict_proba(multi_features)[0]
    
    actions = ['JUMP', 'PUNCH', 'TURN', 'IDLE']
    return actions[action_idx], action_prob[action_idx]

# Use with confidence threshold
gesture, confidence = predict_gesture(extracted_features)
if confidence > 0.7:  # Only act on high-confidence predictions
    execute_action(gesture)
```

## References

- **Data Organization**: `docs/DATA_ORGANIZATION_GUIDE.md`
- **Training Notebook**: `notebooks/SVM_Local_Training.ipynb`
- **Colab Notebook**: `notebooks/Silksong_Complete_Training_Colab.ipynb`
- **Augmentation**: `src/data_augmentation.py`

---

**Last Updated**: 2025-10-19  
**Dataset**: 173 organized samples (34 walk, 139 non-walk)  
**Binary Accuracy**: 94.29% ✅  
**Multi-class Accuracy**: 57.14% ⚠️ (needs improvement)
