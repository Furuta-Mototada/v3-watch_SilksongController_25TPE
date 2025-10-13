# Project Structure Documentation

## Overview

This document provides a comprehensive overview of the Silksong Motion Controller v3 project structure and organization.

## Directory Layout

### `/Android/` - Wear OS Application

Contains the Android Studio project for the Pixel Watch app that captures and streams sensor data.

**Key Files:**
- `app/build.gradle.kts` - Build configuration with package ID `com.cvk.silksongcontroller`
- `app/src/main/java/com/cvk/silksongcontroller/MainActivity.kt` - Main activity with sensor handling
- `app/src/main/AndroidManifest.xml` - App manifest with permissions
- `app/src/main/res/` - UI layouts and resources

**Package Structure:**
```
com.cvk.silksongcontroller
└── MainActivity.kt
```

### `/src/` - Python Source Code

Contains the Python backend that processes sensor data and controls the game.

**Files:**
- `udp_listener.py` - Main controller that receives UDP packets and simulates keyboard inputs
- `network_utils.py` - UDP network handling utilities
- `calibrate.py` - Calibration tool for personalizing gesture thresholds

### `/installer/` - Installation Scripts

Cross-platform installation and launcher scripts.

**Files:**
- `INSTALLATION_GUIDE.md` - Detailed setup instructions
- `run_controller.sh` / `run_controller.bat` - Launch the controller (Unix/Windows)
- `run_calibration.sh` / `run_calibration.bat` - Launch calibration tool (Unix/Windows)
- `config_template.json` - Template configuration file

### `/docs/` - Documentation

Project documentation, development notes, and media.

**Contents:**
- `PROJECT_STRUCTURE.md` - This file
- `LOOM_VIDEO_SCRIPT.md` - Video documentation script
- `reflections.md` - Development reflections and notes
- `aistudio/` - AI-related resources and configurations
- `loom-transcripts/` - Video transcripts from development sessions

### Root Files

- `config.json` - Runtime configuration (network, thresholds, key mappings)
- `requirements.txt` - Python dependencies
- `README.md` - Main project documentation

## Architecture

### Data Flow

1. **Sensor Capture** (Pixel Watch)
   - Accelerometer, gyroscope, rotation vector, step detector
   - Sampled at high frequency (SENSOR_DELAY_GAME)

2. **Network Transport** (UDP)
   - JSON-formatted sensor packets
   - Local network (WiFi) communication
   - Port 12345 (configurable)

3. **Processing** (Python)
   - Packet reception and parsing
   - Gesture detection algorithms
   - Threshold-based action triggering

4. **Game Control** (Keyboard Simulation)
   - `pynput` library for key events
   - Configurable key mappings
   - Real-time input injection

### Configuration System

The `config.json` file controls all runtime behavior:

```json
{
    "network": {
        "listen_ip": "192.168.x.x",
        "listen_port": 12345
    },
    "thresholds": {
        "fuel_added_per_step_sec": 0.4,
        "max_fuel_sec": 1.0,
        "punch_threshold_xy_accel": 35.0,
        "jump_threshold_z_accel": 33.6,
        "turn_threshold_degrees": 123.6
    },
    "keyboard_mappings": {
        "left": "Key.left",
        "right": "Key.right",
        "jump": "z",
        "attack": "x"
    }
}
```

## Development Setup

### Android Development

1. Open `Android/` folder in Android Studio
2. Sync Gradle dependencies
3. Connect Pixel Watch via ADB or WiFi debugging
4. Build and deploy

**Package Name:** `com.cvk.silksongcontroller`
**Namespace:** `com.cvk.silksongcontroller`

### Python Development

1. Create virtual environment (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # Unix
   # or
   venv\Scripts\activate  # Windows
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Run tests/development
   ```bash
   python src/udp_listener.py
   ```

## Version History

- **v1**: Initial proof of concept (previous repo)
- **v2**: Enhanced gesture recognition (previous repo)
- **v3**: Pixel Watch integration, improved architecture, cleaner project structure

## Migration Notes

This project was reorganized from v2 with the following changes:

1. **Package Rename**
   - Old: `com.example.silksongmotioncontroller`
   - New: `com.cvk.silksongcontroller`

2. **File Reorganization**
   - Python files moved to `src/` directory
   - Documentation consolidated in `docs/`
   - Installer scripts maintained in `installer/`

3. **Project Name**
   - Updated from "Silksong Motion Controller" to "Silksong Controller v3"

## Contributing Guidelines

When contributing to this project:

1. **Android Code**
   - Follow Kotlin coding conventions
   - Maintain package structure
   - Update version codes appropriately

2. **Python Code**
   - Follow PEP 8 style guide
   - Add docstrings to functions
   - Update requirements.txt if adding dependencies

3. **Documentation**
   - Keep README.md up to date
   - Document significant changes
   - Add comments for complex logic

## License

MIT License - See root LICENSE file for details.

## Contact

For questions or issues, please open a GitHub issue in the repository.
