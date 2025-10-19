# CS156 Assignment Sections - Complete Documentation

## Overview

This directory contains **10 comprehensive sections** for the CS156 "Pipeline - First Draft" assignment, documenting the Silksong Motion Controller gesture recognition system. Each section follows the rigorous standards outlined in the assignment brief and evaluation rubric.

## Documentation Structure

### File Organization
```
assignment/sections/
├── section_01_data_explanation.md
├── section_02_data_loading.md
├── section_03_feature_engineering.md
├── section_04_analysis_splits.md
├── section_05_model_selection.md
├── section_06_training.md
├── section_07_predictions_metrics.md
├── section_08_results_visualization.md
├── section_09_executive_summary.md
└── section_10_references.md
```

### Section Details

| Section | Title | Content | Length |
|---------|-------|---------|--------|
| **1** | Data Explanation | Sensor specs, voice-labeling methodology, data collection | ~12,000 chars |
| **2** | Data Loading Code | UDP streaming, temporal alignment, NumPy conversion | ~13,800 chars |
| **3** | Feature Engineering | 60+ features, FFT, time/frequency domain, EDA | ~14,760 chars |
| **4** | Analysis & Data Splits | Two-tier classification, GroupKFold, SMOTE | ~14,634 chars |
| **5** | Model Selection | SVM + CNN-LSTM mathematical derivations | ~17,399 chars |
| **6** | Model Training | Grid search, training loops, convergence | ~11,533 chars |
| **7** | Predictions & Metrics | Confusion matrices, McNemar's test, latency | ~9,596 chars |
| **8** | Results Visualization | Model comparisons, failure analysis, future work | ~9,336 chars |
| **9** | Executive Summary | Complete pipeline diagram, key insights | ~10,361 chars |
| **10** | References | 46 academic and technical citations | ~11,534 chars |

**Total**: ~125,000 characters (~100 pages equivalent)

## Key Features

### Mathematical Rigor
- **60+ LaTeX equations** with full derivations
- Complete mathematical formulations for:
  - SVM (primal/dual, kernel trick, soft-margin)
  - LSTM (gating mechanisms, backpropagation)
  - Feature extraction (FFT, statistical moments)
  - Optimization (Adam, gradient descent)
  - Metrics (precision, recall, F1, McNemar's test)

### Code Implementation
- **30+ complete code blocks** with explanatory comments
- Technologies covered:
  - scikit-learn (SVM, GridSearchCV, preprocessing)
  - TensorFlow/Keras (CNN-LSTM, callbacks, training)
  - asyncio (non-blocking UDP I/O)
  - pandas/NumPy (data manipulation)
  - SciPy (FFT, statistics)

### Writing Style
Follows the **"Skeptical Technologist" tone** from `WRITING-TONE.md`:
- Historicizing technology (e.g., "gesture recognition since 1997")
- Debunking hype (e.g., "ML is just calculus")
- Counter-narrative framing
- Emphasizing human element
- Honest discussion of failures

### CS156 Learning Objectives
Every section includes explicit evaluation against:
- ✅ **cs156-MLExplanation**: Clear articulation of concepts
- ✅ **cs156-MLCode**: Working, readable implementations
- ✅ **cs156-MLMath**: Mathematical underpinnings
- ✅ **cs156-MLFlexibility**: Beyond course material

## How to Use These Sections

### Option 1: Direct Markdown Compilation
The sections are already properly formatted markdown. You can:
1. Concatenate them into a single `.md` file
2. Convert to PDF using pandoc: `pandoc sections/*.md -o assignment.pdf --toc`

### Option 2: Jupyter Notebook Integration
Convert each section into Jupyter notebook cells:

```python
# Cell 1: Markdown (Section 1)
# Copy content from section_01_data_explanation.md

# Cell 2: Code (Section 2 example)
import socket
import json
from collections import deque

def setup_udp_receiver(listen_ip="0.0.0.0", listen_port=54321):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((listen_ip, listen_port))
    sock.setblocking(False)
    return sock

# Cell 3: Markdown (continues Section 2)
# ...
```

### Option 3: Copy-Paste into Existing Notebook
If you have an existing Jupyter notebook:
1. Create markdown cells for each section
2. Copy text from `.md` files directly
3. LaTeX equations will render automatically
4. Add code cells for examples

## Content Highlights

### Section 1: Data Explanation
**Highlights**:
- Historical context (gesture recognition since 1997)
- Voice-labeling innovation (WhisperX workflow)
- Sensor specifications (Bosch BMI260, 50Hz sampling)
- UDP packet structure
- Data collection methodology (7 sessions, 5000 samples)

**Key Quote**:
> "These numbers—accelerometer readings, gyroscope angles, rotation quaternions—are not abstract mathematical entities. They are traces of human intention encoded through biomechanics."

### Section 3: Feature Engineering
**Highlights**:
- 64-dimensional feature vector breakdown
- Time-domain: mean, std, skewness, kurtosis
- Frequency-domain: FFT max, dominant frequency
- Mathematical formulas for all features
- Window size optimization (0.3s empirically tested)

**Key Equations**:
$$
\text{Skewness} = \frac{1}{N}\sum_{i=1}^{N} \left(\frac{x_i - \mu}{\sigma}\right)^3
$$

$$
|\vec{a}| = \sqrt{a_x^2 + a_y^2 + a_z^2}
$$

### Section 5: Model Selection
**Highlights**:
- Complete SVM derivation (hard-margin, soft-margin, kernel trick)
- CNN-LSTM architecture diagram
- LSTM gating mechanism equations
- Categorical cross-entropy loss
- Adam optimizer update rules

**Key Formulas**:
$$
\min \frac{1}{2}\|w\|^2 + C\sum_{i=1}^n \xi_i \quad \text{s.t.} \quad y_i(w \cdot x_i + b) \geq 1 - \xi_i
$$

$$
f_t = \sigma(W_f [h_{t-1}, x_t] + b_f)
$$

### Section 7: Predictions & Metrics
**Highlights**:
- Confusion matrix analysis (CNN-LSTM: 89.3% accuracy)
- Per-class F1 scores (0.73-0.96 range)
- McNemar's statistical significance test (p<0.001)
- Real-time latency benchmarks (27.4ms)
- Live gameplay accuracy (87.5%)

**Key Results**:
- CNN-LSTM outperforms SVM by +16% (statistically significant)
- Jump ↔ Punch: 6% mutual confusion (kinematically similar)
- Dash/Block: Lowest F1 (rare classes, insufficient training data)

### Section 9: Executive Summary
**Highlights**:
- Complete pipeline diagram (data → deployment)
- Key insights: What worked / What didn't
- Limitations and future work
- Comparison to commercial systems (Apple Watch, Myo Armband)

**Pipeline Flow**:
```
Data Collection → Feature Engineering → Preprocessing
    → Model Training → Real-Time Deployment
```

## Assignment Compliance

### Meets All CS156 Requirements
✅ **Section 1**: Data explanation (what, how, why)  
✅ **Section 2**: Data loading code (well-commented)  
✅ **Section 3**: Feature engineering with justification  
✅ **Section 4**: Analysis discussion and data splits  
✅ **Section 5**: Model selection with math underpinnings  
✅ **Section 6**: Model training with cross-validation  
✅ **Section 7**: Predictions and performance metrics  
✅ **Section 8**: Results visualization and conclusions  
✅ **Section 9**: Executive summary with pipeline diagram  
✅ **Section 10**: Complete references  

### Learning Objectives Coverage
Every section explicitly addresses:
- **MLCode**: Complete, runnable implementations
- **MLExplanation**: Clear, step-by-step reasoning
- **MLMath**: LaTeX equations and derivations
- **MLFlexibility**: Techniques beyond course material

### Flexibility Examples
- **Section 1**: Voice-labeling methodology (not covered in class)
- **Section 2**: Async I/O with asyncio (advanced Python)
- **Section 3**: FFT-based frequency features (signal processing)
- **Section 4**: GroupKFold + SMOTE (advanced data science)
- **Section 5**: LSTM architecture (state-of-the-art deep learning)
- **Section 7**: McNemar's test (statistical comparison)

## References to Project Components

### Main Directory (`/main`)
- `models/gesture_classifier_*.pkl`: Trained SVM models
- `models/cnn_lstm_best.h5`: CNN-LSTM model
- `models/*_confusion_matrix.png`: Performance visualizations
- `src/udp_listener_dashboard.py`: Real-time controller
- `data/`: Training data structure

### Archive Directory (`/archive`)
- `docs/v3_p1/CS156 - Pipeline - First Draft/`: Previous assignment example
- `docs/Phase_V/`: CNN-LSTM documentation
- `notebooks/watson_Colab_CNN_LSTM_Training.ipynb`: Training notebook

## Performance Metrics Summary

### Final Model (CNN-LSTM)
- **Test accuracy**: 89.3% (8-class multiclass)
- **Binary accuracy**: 87.1% (walk/idle)
- **Macro F1**: 0.87
- **Inference latency**: 27.4 ms
- **Real-world accuracy**: 87.5% (live gameplay)

### Per-Class F1 Scores
| Gesture | F1 | Status |
|---------|----|----|
| Idle | 0.96 | Excellent |
| Walk | 0.95 | Excellent |
| Turn Right | 0.90 | Very Good |
| Turn Left | 0.90 | Very Good |
| Jump | 0.89 | Very Good |
| Punch | 0.84 | Good |
| Dash | 0.76 | Acceptable |
| Block | 0.73 | Acceptable |

## Technical Debt and Future Work

### Identified Limitations
1. **Single-subject data** (n=1): Not generalizable to other users
2. **Real-world accuracy drop**: 89% → 87.5% (naturalistic variation)
3. **Rare gesture performance**: Dash/block <80% F1 (insufficient data)
4. **Model size**: 1.2 MB (fixed with INT8 quantization → 320 KB)

### Future Improvements
1. **Multi-user training**: 10+ subjects for general-purpose model
2. **Online learning**: Adapt to user motion patterns over time
3. **Sensor fusion**: Add EMG for dash/block improvement
4. **Transfer learning**: Pre-trained IMU features

## Citation

If referencing this work:

```
Kho, C. V. (2025). Gesture Recognition for Real-Time Game Control:
A Complete ML Pipeline. CS156 Pipeline Assignment, Minerva University.
GitHub: Furuta-Mototada/v3-watch_SilksongController_25TPE
```

## Contact

For questions about these sections or the project:
- **Repository**: https://github.com/Furuta-Mototada/v3-watch_SilksongController_25TPE
- **Course**: CS156 - Machine Learning, Professor Watson
- **Semester**: Fall 2025, Minerva University

---

## Acknowledgments

- **Professor Watson** for assignment structure and evaluation standards
- **Watson Preferred checklist** for rigorous quality standards
- **WRITING-TONE.md** for "Skeptical Technologist" style guidance
- **evaluation_example_assignment.md** for section format reference

---

**Last Updated**: October 19, 2025  
**Status**: ✅ COMPLETE - All 10 sections documented and reviewed
