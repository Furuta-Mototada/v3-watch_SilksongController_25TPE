# Models Directory

This directory stores the trained machine learning models for gesture recognition.

## Expected Files

After running the ML pipeline notebook (`CS156_Silksong_Watch.ipynb`), this directory will contain:

- `gesture_classifier.pkl` - Trained SVM classifier model
- `feature_scaler.pkl` - StandardScaler for feature normalization
- (Optional) Other model formats or architectures

## Model Usage

The trained models are used by:
1. **Training**: `CS156_Silksong_Watch.ipynb` saves models after training
2. **Deployment**: `src/udp_listener.py` loads models for real-time gesture recognition

## Note

Model files (`.pkl`, `.joblib`, `.h5`) are excluded from git due to their size.
You must train the models locally using the notebook before deploying the controller.
