# v3-watch_SilksongController_25TPE

**ML-powered Pixel Watch (Gen 1) as a controller for Silksong**

This is version 3 of the Silksong Motion Controller project, specifically designed for the **Google Pixel Watch (Gen 1)** with enhanced machine learning capabilities.

## 🎯 Project Overview

Transform your Pixel Watch into a wireless motion controller for Hollow Knight, Silksong, or any 2D platformer game! Use natural wrist movements and gestures to control your character.

### Key Features

- 🎮 **Pixel Watch Optimized** → Specifically designed for Pixel Watch (Gen 1) form factor
- 🤖 **ML-Enhanced** → Machine learning models for gesture recognition
- 🚶‍♂️ **Natural Movements** → Walk, jump, and punch using wrist gestures
- 📱 **Wireless** → No cables needed, just Wi-Fi
- ⚙️ **Personalized** → Calibrates to your unique movements

## 📂 Project Structure

```
v3-watch_SilksongController_25TPE/
├── android/              # Wear OS application for Pixel Watch
│   ├── app/
│   │   ├── src/
│   │   │   └── main/
│   │   │       └── java/com/cvk/silksongcontroller/
│   │   └── build.gradle.kts
│   └── build.gradle.kts
├── docs/                 # Documentation and design notes
├── installer/            # Installation scripts
├── calibrate.py          # Calibration script
├── udp_listener.py       # Main listener application
├── network_utils.py      # Network utilities
├── config.json           # Configuration file
└── requirements.txt      # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- Google Pixel Watch (Gen 1) with Wear OS
- Computer (Windows, Mac, or Linux) with Python 3.7+
- Both devices on the same Wi-Fi network
- A game to play (Hollow Knight, Celeste, etc.)

### Installation

1. **Clone this repository**
   ```bash
   git clone https://github.com/CarlKho-Minerva/v3-watch_SilksongController_25TPE.git
   cd v3-watch_SilksongController_25TPE
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Build and install the Wear OS app**
   ```bash
   cd android
   ./gradlew assembleDebug
   # Install the APK to your Pixel Watch via ADB
   adb install -r app/build/outputs/apk/debug/app-debug.apk
   ```

4. **Configure and run**
   - Edit `config.json` with your network settings
   - Run calibration: `python calibrate.py`
   - Start the listener: `python udp_listener.py`
   - Launch the app on your Pixel Watch
   - Start playing!

## 📝 Notes

This is version 3 of the Silksong Motion Controller project. It builds upon v2 but is specifically optimized for the smaller form factor and unique capabilities of the Pixel Watch.

### Changes from v2

- Adapted UI for Pixel Watch's smaller screen
- Optimized sensor polling for better battery life
- Updated package name: `com.cvk.silksongcontroller`
- Enhanced gesture recognition algorithms

## 📄 License

This project is for educational and personal use.

## 👤 Author

Carl Kho (@CarlKho-Minerva)
