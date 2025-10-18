# Silksong Motion Controller - AI Coding Agent Guide

## Architecture Overview

This project controls Hollow Knight: Silksong using motion gestures from a Pixel Watch. It has evolved through 5 phases:

**Data Flow**: Android Wear OS App → UDP Stream (50Hz) → Python Controller → Keyboard Simulation → Game

**Key Components**:
- `Android/`: Kotlin Wear OS app streams sensor data (accel, gyro, rotation, steps) over UDP with automatic NSD discovery
- `src/udp_listener.py`: Multi-threaded ML controller (Collector→Predictor→Actor pattern)
- `src/feature_extractor.py`: Extracts ~60 features from sensor windows for ML inference
- `src/models/cnn_lstm_model.py`: CNN/LSTM hybrid for deep learning gesture recognition
- `notebooks/watson_Colab_CNN_LSTM_Training.ipynb`: Google Colab training pipeline

## Critical Development Workflows

### Running the Controller
```bash
# Primary ML controller (Phase IV)
cd src && python udp_listener.py

# Requires trained models in models/ directory:
# - gesture_classifier.pkl (SVM)
# - feature_scaler.pkl (StandardScaler) 
# - feature_names.pkl (feature list)
```

### Training New Models

**Phase III (SVM - Fast)**: Run `CS156_Silksong_Watch.ipynb` locally with manual gesture samples

**Phase V (CNN/LSTM - Best)**: 
1. Collect voice-labeled data: `python src/continuous_data_collector.py --duration 600 --session game_01`
2. Post-process: `./docs/Phase_V/process_transcripts.sh SESSION_NAME` (runs WhisperX + alignment)
3. Upload to Google Drive in `silksong_data/SESSION/` folders
4. Train on Colab: `notebooks/watson_Colab_CNN_LSTM_Training.ipynb`

### Data Collection
- **Manual labeled**: `python src/data_collector.py` (guided 8-gesture recording)
- **Voice-controlled**: `python src/continuous_data_collector.py` (natural gameplay with audio)
  - Post-process with WhisperX for word-level timestamps
  - Script: `docs/Phase_V/process_transcripts.sh` automates transcription → label alignment

### Android Development
- Open `Android/` in Android Studio
- Main code: `Android/app/src/main/java/com/cvk/silksongcontroller/MainActivity.kt`
- Build: Standard Wear OS Gradle build
- NSD service type: `_silksong._udp.` (for auto-discovery)

## Project-Specific Conventions

### Multi-Threading Pattern (Phase IV)
`udp_listener.py` uses producer-consumer with thread-safe queues:
- **Collector thread**: Reads UDP at network speed, zero processing
- **Predictor thread**: Runs ML on 0.3s micro-windows continuously (not fixed intervals)
- **Actor thread**: Executes keyboard with confidence gating (requires 5 consecutive matching predictions)

This achieves <500ms latency vs >1s with blocking approaches.

### Feature Engineering
Feature extraction in `feature_extractor.py` and notebooks must match exactly:
- Time-domain: mean, std, min, max, range, median, skew, kurtosis, peak counts
- Frequency-domain: FFT max, dominant frequency
- Cross-sensor: magnitude features from accel/gyro
- **Critical**: Feature order must match training (stored in `feature_names.pkl`)

### Configuration
Edit `config.json` for thresholds and keyboard mappings. The ML controller ignores thresholds (except when models are missing - fallback mode).

### Data Structure
```
src/data/continuous/YYYYMMDD_HHMMSS_session/
├── sensor_data.csv          # Raw IMU data (timestamp, sensor, accel_x/y/z, gyro_x/y/z, rot_x/y/z/w)
├── audio_16k.wav            # Voice commands (16kHz downsampled)
├── metadata.json            # Session info
├── SESSION_whisperx.json    # WhisperX transcription with word timestamps
└── SESSION_labels.csv       # Aligned gesture labels (start_time, end_time, gesture, confidence)
```

## Integration Points

### UDP Protocol
Watch sends JSON packets at ~50Hz:
```json
{
  "sensor": "linear_acceleration|gyroscope|rotation_vector|step_detector",
  "accel_x/y/z": float,
  "gyro_x/y/z": float,
  "rot_x/y/z/w": float,
  "timestamp": int
}
```

### Model Loading
ML models loaded at startup with joblib:
```python
classifier = joblib.load('models/gesture_classifier.pkl')
scaler = joblib.load('models/feature_scaler.pkl')
feature_names = joblib.load('models/feature_names.pkl')
```

### Keyboard Control
Uses `pynput.keyboard.Controller`:
- Walk: Hold left/right arrow
- Jump: Press 'z'
- Attack: Press 'x'
- Turn detection changes direction state

## Common Patterns

### Window Buffering
Use `collections.deque` with maxlen for fixed-size sliding windows:
```python
sensor_buffer = deque(maxlen=int(0.3 * 50))  # 0.3s at 50Hz
```

### Confidence Gating
Require N consecutive predictions to change state (prevents jitter):
```python
prediction_history = deque(maxlen=5)
if len(set(prediction_history)) == 1:  # All 5 match
    execute_action(prediction_history[0])
```

### Voice Command Processing
WhisperX provides word-level timestamps. The `align_voice_labels.py` script:
1. Loads WhisperX JSON with word segments
2. Matches gesture keywords (jump, punch, turn, walk, idle)
3. Aligns to sensor_data.csv timestamps
4. Generates training labels with confidence scores

## Troubleshooting Notes

- **NaN loss during training**: Check class balance (see `CLASS_BALANCING_GUIDE.md`)
- **Controller not receiving data**: Verify both devices on same WiFi; check NSD discovery logs
- **Low ML accuracy**: Retrain with more balanced data; check feature extraction matches training
- **High latency**: Verify micro-windows (0.3s) are used, not full 2.5s windows

## External Dependencies

- Android: `zeroconf` (NSD), standard Wear OS sensors
- Python: `pynput` (keyboard), `zeroconf` (NSD), `scikit-learn` (SVM), `tensorflow` (CNN/LSTM), `whisperx` (transcription)
- Audio: `sounddevice`, `librosa` for recording/processing
