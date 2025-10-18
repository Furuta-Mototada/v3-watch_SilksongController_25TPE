# Silksong Motion Controller v3 - Pixel Watch Edition

Control Hollow Knight: Silksong using motion gestures from a Pixel Watch! This project uses real-time sensor data (accelerometer, gyroscope, rotation vector, step detector) streamed over UDP from an Android Wear OS app to a Python controller that simulates keyboard inputs.

Building on top of [V2](https://github.com/CarlKho-Minerva/v2_SilksongController_25TPE)

<div>
    <a href="https://www.loom.com/share/175721940a354cb98fe0ec2a13e2bddf">
      <p>1 - Watch Data Transmitted! - Watch Video</p>
    </a>
    <a href="https://www.loom.com/share/175721940a354cb98fe0ec2a13e2bddf">
      <img style="max-width:100vw;" src="https://cdn.loom.com/sessions/thumbnails/175721940a354cb98fe0ec2a13e2bddf-3d20da5d3c764dc4-full-play.gif">
    </a>
  </div>

![data collection complete oct 14 2025](telegram-cloud-photo-size-5-6300675731876416733-y-1.jpg)

<div>
    <a href="https://www.loom.com/share/dfb0398e038c409084696484e159a588">
      <p>SVM Live Demo (Bad Performance)- Watch Video</p>
    </a>
    <a href="https://www.loom.com/share/dfb0398e038c409084696484e159a588">
      <img style="max-width:300px;" src="https://cdn.loom.com/sessions/thumbnails/dfb0398e038c409084696484e159a588-cd70ba8caabdfa18-full-play.gif">
    </a>
  </div>

<div>
    <a href="https://www.loom.com/share/db304cbfea1d4fa4914256f097d4a166">
      <p>v3 cnn - how im collecting data - Watch Video</p>
    </a>
    <a href="https://www.loom.com/share/db304cbfea1d4fa4914256f097d4a166">
      <img style="max-width:300px;" src="https://cdn.loom.com/sessions/thumbnails/db304cbfea1d4fa4914256f097d4a166-b2ff6573e4a9ecc7-full-play.gif">
    </a>
  </div>

## 🚨 Model Only Predicts "Walk"? READ THIS FIRST!

If your trained model has **77-78% accuracy but 0% recall for jump/punch/turn/noise**, you have a class imbalance issue. This is common and easily fixable!

**Quick Fix (30 minutes):**
- Your Colab notebook already has the solution (class weight softening)
- Just retrain: Runtime → Restart runtime → Run all cells
- Expected result: All gestures working with 85-90% accuracy

**Documentation:**
- 😓 **Tired? Quick fix:** [WHEN_YOURE_TIRED.md](WHEN_YOURE_TIRED.md)
- 🎯 **Want details:** [START_HERE.md](START_HERE.md)
- 📊 **Full guide:** [LEVEL_THE_PLAYING_FIELD.md](LEVEL_THE_PLAYING_FIELD.md)
- 📈 **Before/after:** [BEFORE_AFTER_RESULTS.md](BEFORE_AFTER_RESULTS.md)

**Automated tools:**
```bash
python fix_class_imbalance.py --export  # Get ready-to-paste code
```

---

## 🎮 Features

![Hornet from Hollowknight: Silksong Colors](distribution.png)

- **Motion-based game control**: Walk, jump, attack, and turn using natural body movements
- **Pixel Watch integration**: Wear OS app captures sensor data from your smartwatch
- **Automatic device discovery**: "Magic link" feature - no manual IP configuration needed! 🎯
- **Real-time UDP streaming**: Low-latency sensor data transmission
- **Configurable thresholds**: Calibrate sensitivity for different play styles
- **Cross-platform Python backend**: Works on Windows, macOS, and Linux

## 📁 Project Structure

```text
v3-watch_SilksongController_25TPE/
├── Android/                    # Wear OS Android app
│   └── app/
│       ├── build.gradle.kts   # Android build configuration
│       └── src/main/
│           ├── AndroidManifest.xml
│           └── java/com/cvk/silksongcontroller/
│               └── MainActivity.kt
├── src/                       # Python source code
│   ├── udp_listener.py       # Main controller logic
│   ├── network_utils.py      # UDP network handling
│   ├── calibrate.py          # Calibration tool
│   ├── data_collector.py     # Phase II: ML training data collection
│   └── feature_extractor.py  # Phase III: Feature engineering module
├── models/                    # Trained ML models (Phase III output)
│   ├── gesture_classifier.pkl
│   ├── feature_scaler.pkl
│   └── README.md
├── docs/                      # Documentation
│   ├── Phase_II/             # Data collection guides
│   └── Phase_III/            # ML pipeline documentation
├── installer/                # Installation scripts and templates
│   ├── INSTALLATION_GUIDE.md
│   ├── run_controller.sh/bat
│   └── run_calibration.sh/bat
├── CS156_Silksong_Watch.ipynb # Phase III: ML Pipeline Notebook
├── config.json              # Runtime configuration
└── requirements.txt         # Python dependencies (includes ML libs)
```

## 🚀 Quick Start

### Prerequisites

- **Hardware**: Pixel Watch or compatible Wear OS device
- **Software**:
  - Android Studio (for building the watch app)
  - Python 3.8+ (for the controller)
  - Hollow Knight: Silksong (game)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/CarlKho-Minerva/v3-watch_SilksongController_25TPE.git
   cd v3-watch_SilksongController_25TPE
   ```

2. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Build and install the Android app**
   - Open `Android/` folder in Android Studio
   - Build and deploy to your Pixel Watch
   - ✨ The app will automatically discover your computer on the network!

4. **Run calibration**

   ```bash
   python src/calibrate.py
   ```

5. **Start the controller**

   ```bash
   python src/udp_listener.py
   ```

See `installer/INSTALLATION_GUIDE.md` for detailed setup instructions.

## 🌟 Automatic Connection

The controller features **automatic device discovery** using Network Service Discovery (NSD):

1. **Start the Python controller** - it automatically advertises itself on your local network
2. **Launch the watch app** - watch the connection status at the top:
   - 🟠 "Searching..." - discovering services
   - 🟢 "Connected!" - server found and ready
3. **Start playing!** - no manual IP configuration needed

The watch app will automatically find your computer if both devices are on the same WiFi network. Manual IP entry is still available as a fallback option.

## ⚙️ Configuration

Edit `config.json` to adjust:

- **Network settings**: IP address and port
- **Thresholds**: Sensitivity for gestures (punch, jump, turn, walk)
- **Keyboard mappings**: Custom key bindings

## 📊 Phase II: Machine Learning Data Collection

In addition to real-time gesture control, this project includes a guided data collection system for training ML models:

```bash
python src/data_collector.py
```

This tool:

- Guides you through structured gesture recording sessions
- Defines clear physical stances (Combat, Neutral, Travel)
- Records labeled IMU sensor data for 8 different gestures
- Exports training data in ML-ready CSV format
- Takes ~20-30 minutes for a complete session

**Use Cases**:

- Train personalized gesture recognition models
- Build more robust classifiers than threshold-based detection
- Research and experimentation with IMU gesture recognition
- Create custom gesture sets

See `docs/Phase_II/DATA_COLLECTION_GUIDE.md` for full documentation.

## 🤖 Phase III: Machine Learning Pipeline

Transform collected sensor data into a trained gesture recognition model using a comprehensive Jupyter Notebook:

```bash
# Install ML dependencies
pip install -r requirements.txt

# Run the ML pipeline notebook
jupyter notebook CS156_Silksong_Watch.ipynb
```

**The notebook includes:**

- ✅ Data loading and exploration
- ✅ Feature engineering (~60+ features from time-series data)
- ✅ Model training (SVM with RBF kernel + Random Forest)
- ✅ Hyperparameter tuning via GridSearchCV
- ✅ Model evaluation and validation
- ✅ Model serialization for deployment

**Output Models:**

- `models/gesture_classifier.pkl` - Trained SVM classifier
- `models/feature_scaler.pkl` - Feature normalization scaler
- `models/feature_names.pkl` - Feature reference list
- `models/model_metadata.json` - Performance metrics

**Performance Targets:**

- Test accuracy: >85%
- Real-time latency: <100ms
- Confidence threshold: 0.7 (70%)

See `docs/Phase_III/README.md` for complete ML pipeline documentation.

## 🚀 Phase IV: Multi-Threaded ML Controller ✅ **COMPLETE**

**Fully ML-powered** gesture recognition system with decoupled architecture for low-latency real-time performance:

### Architecture

**Collector Thread** → **Predictor Thread** → **Actor Thread**

1. **Collector**: Reads UDP sensor data at network speed, no processing delay
2. **Predictor**: Runs ML inference continuously on 0.3s micro-windows
3. **Actor**: Executes keyboard actions with confidence gating (5 consecutive predictions)

### Key Features

- **Micro-Windows**: 0.3s windows instead of 2.5s for <500ms latency
- **Continuous Prediction**: No fixed intervals, predicts as fast as CPU allows
- **Confidence Gating**: Requires 5 consecutive matching predictions for stable state changes
- **Thread-Safe Queues**: Producer-consumer pattern eliminates bottlenecks
- **All ML**: Jump, punch, turn, and walk all handled by ML model

### Performance

- **Latency**: <500ms (down from 1+ second)
- **Responsiveness**: Near real-time gesture detection
- **CPU**: ~30-40% single-core usage

See `docs/Phase_IV/README.md` for complete documentation.

## 🎙️ Phase V: Voice-Controlled Data Collection + WhisperX Post-Processing

**Continuous motion data collection** using voice commands with retrospective WhisperX processing:

### Features

- **Audio Recording**: Records audio alongside sensor data during gameplay
- **WhisperX Post-Processing**: Research-grade word segmentation with forced alignment
- **Automated Workflow**: One-command processing with `process_transcripts.sh`
- **Natural Gameplay**: No performance impact during recording
- **Word-Level Timestamps**: Precise alignment of voice commands to sensor data
- **Hands-Free**: Maintain natural motion while playing Hollow Knight: Silksong

### Quick Start

```bash
# Install dependencies
pip install whisperx sounddevice numpy librosa soundfile

# 1. Record session (5-10 minutes)
cd src
python continuous_data_collector.py --duration 600 --session gameplay_01

# 2. Automated post-processing (WhisperX + alignment)
cd ..
./process_transcripts.sh YYYYMMDD_HHMMSS_gameplay_01

# That's it! Your labeled training data is ready.
```

### Manual Post-Processing (Alternative)

```bash
# Step 1: WhisperX transcription with forced alignment
python src/whisperx_transcribe.py \
  --audio src/data/continuous/SESSION/audio_16k.wav \
  --model large-v3

# Step 2: Align voice commands to sensor data
python src/align_voice_labels.py \
  --session SESSION \
  --whisper src/data/continuous/SESSION/SESSION_whisperx.json
```

### Why Post-Processing?

**Problem**: Real-time Whisper processing requires significant CPU resources

**Solution**: Retrospective processing allows:

- No performance impact during gameplay
- Use powerful WhisperX models with forced alignment
- Research-grade word-level timestamp granularity
- Re-process with different parameters
- Natural, reactive gameplay

### Documentation

- **Quick Start**: `docs/Phase_V/QUICK_REFERENCE.md` - Commands and workflow
- **Full Guide**: `docs/Phase_V/POST_PROCESSING.md` - Complete documentation
- **Data Collection**: `docs/Phase_V/DATA_COLLECTION_GUIDE.md` - Recording best practices
- **WhisperX**: `docs/Phase_V/WhisperX/WHISPERX_GUIDE.md` - WhisperX details

## 🔧 Development

### Android Package

The Android app uses package name: `com.cvk.silksongcontroller`

To modify the Android app:

1. Open `Android/` in Android Studio
2. Main code is in `Android/app/src/main/java/com/cvk/silksongcontroller/MainActivity.kt`
3. Edit layouts in `Android/app/src/main/res/layout/`

### Python Controller

Main entry point: `src/udp_listener.py`

- Receives UDP packets from watch
- Processes sensor data to detect gestures
- Simulates keyboard inputs

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

Based on the original v2 SilksongController project with enhancements for Pixel Watch compatibility and improved gesture recognition.
