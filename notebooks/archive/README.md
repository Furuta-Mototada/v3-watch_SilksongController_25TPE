# Notebooks Archive

This directory contains historical Jupyter notebooks from earlier phases of the project.

## Contents

### `CS156_Silksong_Watch.ipynb`
**Phase III: SVM Training Pipeline (Local)**

Complete ML pipeline using traditional machine learning:
- Data loading from Phase II manual collection
- Feature engineering (~60 features from time/frequency domains)
- SVM classifier with RBF kernel
- Random Forest as comparison model
- GridSearchCV for hyperparameter tuning
- Model evaluation and serialization

**Performance**: ~70-75% test accuracy  
**Status**: Superseded by Phase V CNN-LSTM approach  
**Training Time**: ~10-15 minutes on local machine

### Why Archived?

This notebook represents the Phase III approach using hand-engineered features and classical ML. While functional, it was superseded by:
1. **Phase V CNN-LSTM**: Deep learning approach with automatic feature extraction
2. **Better Data**: Voice-labeled continuous collection vs. manual guided collection
3. **Cloud Training**: Google Colab with GPU vs. local CPU

## Current Training Notebooks

- **CNN-LSTM (Current)**: `notebooks/watson_Colab_CNN_LSTM_Training.ipynb`
  - Deep learning architecture
  - Trained on Google Colab with GPU
  - Processes Phase V voice-labeled data
  - See `docs/Phase_V/README.md` for details

## How to Use This Archive

**If you want to:**
- Understand the Phase III approach → Run this notebook with Phase II data
- Compare SVM vs. CNN-LSTM → Train both and compare results
- Learn feature engineering → Review feature extraction code
- Use classical ML → This notebook is still functional

**Data Requirements:**
- Phase II manual collection data (see `docs/Phase_II/`)
- Or: Adapt for Phase V data format

---

**Last Updated**: October 18, 2025  
**Original Creation**: Phase III development
