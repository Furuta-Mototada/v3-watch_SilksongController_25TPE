# Development Guide - v3 Silksong Controller

## Project Overview

This is version 3 of the Silksong Motion Controller, optimized for the **Google Pixel Watch (Gen 1)**. The project enables using a Pixel Watch as a wireless motion controller for 2D platformer games through gesture recognition and sensor data.

## Project Structure

```
v3-watch_SilksongController_25TPE/
├── android/                          # Wear OS application
│   ├── app/
│   │   ├── src/
│   │   │   ├── main/
│   │   │   │   ├── java/com/cvk/silksongcontroller/
│   │   │   │   │   └── MainActivity.kt
│   │   │   │   ├── res/              # Android resources
│   │   │   │   └── AndroidManifest.xml
│   │   │   ├── androidTest/          # Instrumented tests
│   │   │   └── test/                 # Unit tests
│   │   └── build.gradle.kts          # App-level Gradle configuration
│   ├── gradle/                       # Gradle wrapper and dependencies
│   ├── build.gradle.kts              # Project-level Gradle configuration
│   └── settings.gradle.kts           # Gradle settings
├── docs/                             # Documentation and notes
├── installer/                        # Installation scripts
├── calibrate.py                      # Sensor calibration script
├── udp_listener.py                   # Main listener for game control
├── network_utils.py                  # Network utilities
├── config.json                       # Configuration file
├── requirements.txt                  # Python dependencies
└── README.md                         # Project documentation
```

## Android Application

### Package Structure

The Android app uses the package name: **`com.cvk.silksongcontroller`**

This was changed from the v2 package (`com.example.silksongmotioncontroller`) to:
- Establish unique project identity
- Follow Android best practices (not using `com.example`)
- Reflect the developer namespace (`com.cvk`)

### Key Components

- **MainActivity.kt**: Main activity handling sensor data collection and UDP transmission
- **build.gradle.kts**: Application configuration with `applicationId` and `namespace` set to `com.cvk.silksongcontroller`

### Building the Android App

```bash
cd android
./gradlew assembleDebug
```

The APK will be generated at: `android/app/build/outputs/apk/debug/app-debug.apk`

### Installing on Pixel Watch

```bash
# Connect your Pixel Watch via ADB
adb devices

# Install the app
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

## Python Components

### Prerequisites

```bash
pip install -r requirements.txt
```

### Calibration

Before first use, run the calibration script to tune the controller to your movements:

```bash
python calibrate.py
```

### Running the Listener

Start the UDP listener to receive sensor data from the watch and translate it to game controls:

```bash
python udp_listener.py
```

## Configuration

Edit `config.json` to customize:
- Network settings (IP address, port)
- Sensor thresholds
- Key mappings
- Gesture parameters

## Development Workflow

1. **Android Development**
   - Open the `android/` directory in Android Studio
   - Make changes to the Wear OS app
   - Test on Pixel Watch emulator or physical device

2. **Python Development**
   - Modify calibration or listener scripts
   - Test with simulated sensor data
   - Validate game control mappings

3. **Integration Testing**
   - Deploy Android app to Pixel Watch
   - Run Python listener on computer
   - Test with actual game

## Version History

- **v1**: Initial prototype with Google Pixel 6 Pro
- **v2**: Enhanced with more sensors and better gesture recognition
- **v3**: Optimized for Pixel Watch (Gen 1) with improved UI and battery efficiency

## Contributing

When making changes:
1. Follow existing code structure and style
2. Update tests when modifying functionality
3. Document significant changes
4. Test on actual hardware when possible

## Notes

- The Android app is designed specifically for Wear OS
- Battery life considerations: Sensor polling is optimized for the watch's smaller battery
- UI is adapted for the circular Pixel Watch display
- Network connectivity requires both devices on the same Wi-Fi network

## License

This project is for educational and personal use.

---

**Author**: Carl Kho (@CarlKho-Minerva)
**Repository**: https://github.com/CarlKho-Minerva/v3-watch_SilksongController_25TPE
