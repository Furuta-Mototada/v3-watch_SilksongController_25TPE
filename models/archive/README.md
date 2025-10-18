# Models Archive

This directory contains historical model artifacts and metadata.

## Contents

### `model_metadata.json`
Metadata from Phase III SVM training:
- Model performance metrics
- Training parameters
- Feature importance
- Timestamp and versioning info

**Status**: Corresponds to archived Phase III notebook

## Current Models

**Location**: `models/` (parent directory)

**Expected Files** (generated during training):
- `gesture_classifier.pkl` - Trained classifier (SVM or CNN-LSTM)
- `feature_scaler.pkl` - StandardScaler for feature normalization
- `feature_names.pkl` - List of feature names for consistency
- `model_metadata.json` - Current model performance and parameters

**Note**: Trained models are not committed to git (too large). They are generated during training and loaded at runtime.

## Training Instructions

**Phase III (SVM - Archived)**:
```bash
jupyter notebook notebooks/archive/CS156_Silksong_Watch.ipynb
# Follow notebook cells to train and save to models/
```

**Phase V (CNN-LSTM - Current)**:
```bash
# Upload data to Google Drive
# Open notebooks/watson_Colab_CNN_LSTM_Training.ipynb in Colab
# Train with GPU
# Download trained models to models/
```

See respective phase documentation for details:
- Phase III: `docs/Phase_III/README.md`
- Phase V: `docs/Phase_V/README.md`

---

**Last Updated**: October 18, 2025  
**Note**: Models are gitignored due to size. Train locally or download from cloud storage.
