# Silksong Motion Controller v3 - Pixel Watch Edition

Control Hollow Knight: Silksong using motion gestures from a Pixel Watch! This project uses real-time sensor data (accelerometer, gyroscope, rotation vector, step detector) streamed over UDP from an Android Wear OS app to a Python controller that simulates keyboard inputs.

Building on top of [V2](https://github.com/CarlKho-Minerva/v2_SilksongController_25TPE)

## 🎮 Features

- **Motion-based game control**: Walk, jump, attack, and turn using natural body movements
- **Pixel Watch integration**: Wear OS app captures sensor data from your smartwatch
- **Automatic device discovery**: "Magic link" feature - no manual IP configuration needed! 🎯
- **Real-time UDP streaming**: Low-latency sensor data transmission
- **Configurable thresholds**: Calibrate sensitivity for different play styles
- **Cross-platform Python backend**: Works on Windows, macOS, and Linux
- **Data collection tool**: Guided procedure for collecting high-quality IMU gesture datasets

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
│   └── data_collector.py    # Data collection tool (Phase II)
├── installer/                # Installation scripts and templates
│   ├── INSTALLATION_GUIDE.md
│   ├── run_controller.sh/bat
│   ├── run_calibration.sh/bat
│   └── run_data_collector.sh/bat
├── docs/                     # Documentation and development notes
├── config.json              # Runtime configuration
└── requirements.txt         # Python dependencies
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

## 📊 Data Collection (Phase II)

For researchers and developers who want to collect IMU gesture data:

```bash
# Run the guided data collection tool
python src/data_collector.py

# Or use the installer script
cd installer
./run_data_collector.sh  # Unix/Mac
run_data_collector.bat   # Windows
```

This tool provides a comprehensive, guided procedure for collecting high-quality IMU gesture datasets. See `docs/DATA_COLLECTION_GUIDE.md` for detailed instructions on:

- Three user stances (Combat, Neutral, Travel)
- 10 different gesture types across all stances
- Automated data organization and labeling
- Best practices for data quality

Perfect for training gesture recognition models or analyzing motion patterns!

## ⚙️ Configuration

Edit `config.json` to adjust:

- **Network settings**: IP address and port
- **Thresholds**: Sensitivity for gestures (punch, jump, turn, walk)
- **Keyboard mappings**: Custom key bindings

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
