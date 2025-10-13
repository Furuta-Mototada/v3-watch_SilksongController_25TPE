# Developer Guide

Welcome to the Silksong Motion Controller v3 development guide! This document will help you get started with development and contribution.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Project Architecture](#project-architecture)
3. [Development Workflow](#development-workflow)
4. [Code Standards](#code-standards)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)

## Quick Start

### Prerequisites

- **Hardware**: Pixel Watch or compatible Wear OS device
- **Software**:
  - Android Studio (latest version)
  - Python 3.8+
  - Git

### Initial Setup

1. Clone and navigate to the project:

   ```bash
   git clone https://github.com/CarlKho-Minerva/v3-watch_SilksongController_25TPE.git
   cd v3-watch_SilksongController_25TPE
   ```

2. Set up Python environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Open Android project:
   - Launch Android Studio
   - Open the `Android/` directory
   - Wait for Gradle sync to complete

## Project Architecture

### Component Overview

```text
┌─────────────────┐
│  Pixel Watch    │ (Sensor capture)
│  Android App    │
└────────┬────────┘
         │ UDP (JSON)
         ↓
┌─────────────────┐
│  Python Server  │ (Gesture detection)
│  UDP Listener   │
└────────┬────────┘
         │ Keyboard Events
         ↓
┌─────────────────┐
│  Game           │ (Control target)
│  Silksong       │
└─────────────────┘
```

### Key Technologies

- **Android**: Kotlin, Wear OS SDK, Sensor APIs
- **Python**: pynput (keyboard control), socket (UDP)
- **Network**: UDP for low-latency sensor streaming

## Development Workflow

### Android Development

#### Building the App

```bash
cd Android
./gradlew assembleDebug
```

#### Testing on Watch

1. Enable Developer Options on Pixel Watch:
   - Go to Settings → About → Tap Build number 7 times

2. Enable ADB debugging:
   - Settings → Developer options → ADB debugging

3. Connect via WiFi debugging or USB (with adapter):

   ```bash
   adb connect <watch-ip>:5555
   adb devices  # Verify connection
   ```

4. Install APK:

   ```bash
   ./gradlew installDebug
   ```

#### Key Files to Modify

- **MainActivity.kt**: Main sensor handling and UI logic
- **activity_main.xml**: UI layout
- **build.gradle.kts**: Dependencies and build config

### Python Development

#### Running the Controller

```bash
python src/udp_listener.py
```

#### Key Components

1. **UDP Listener** (`src/udp_listener.py`):
   - Receives sensor packets
   - Parses JSON data
   - Triggers gesture detection
   - Simulates keyboard inputs

2. **Network Utils** (`src/network_utils.py`):
   - UDP socket management
   - Packet handling utilities

3. **Calibration** (`src/calibrate.py`):
   - Interactive threshold tuning
   - Config file generation

#### Configuration

Edit `config.json` to adjust:

```json
{
    "network": {
        "listen_ip": "0.0.0.0",  // Listen on all interfaces
        "listen_port": 12345
    },
    "thresholds": {
        "punch_threshold_xy_accel": 35.0,  // Adjust sensitivity
        "jump_threshold_z_accel": 33.6,
        "turn_threshold_degrees": 123.6
    }
}
```

## Code Standards

### Kotlin (Android)

Follow [Kotlin Coding Conventions](https://kotlinlang.org/docs/coding-conventions.html):

```kotlin
// Good
class MainActivity : AppCompatActivity() {
    private lateinit var sensorManager: SensorManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setupSensors()
    }

    private fun setupSensors() {
        // Implementation
    }
}
```

### Python

Follow [PEP 8](https://peps.python.org/pep-0008/):

```python
# Good
def handle_sensor_data(sensor_type: str, values: dict) -> None:
    """Process incoming sensor data and trigger appropriate actions.

    Args:
        sensor_type: Type of sensor (e.g., 'accelerometer')
        values: Dictionary of sensor values
    """
    if sensor_type == "linear_acceleration":
        detect_punch(values)
```

### Commit Messages

Use conventional commits format:

```text
feat: add gyroscope support
fix: resolve UDP packet loss issue
docs: update installation guide
refactor: reorganize sensor handling code
```

## Testing

### Android Testing

#### Unit Tests

```bash
./gradlew test
```

#### Instrumented Tests

```bash
./gradlew connectedAndroidTest
```

### Python Testing

Create test files in `tests/` directory:

```python
# tests/test_gesture_detection.py
import unittest
from src.udp_listener import detect_punch

class TestGestureDetection(unittest.TestCase):
    def test_punch_detection(self):
        values = {"x": 40.0, "y": 5.0, "z": 3.0}
        self.assertTrue(detect_punch(values, threshold=35.0))
```

Run tests:

```bash
python -m unittest discover tests
```

## Troubleshooting

### Common Issues

#### 1. Sensor Data Not Received

**Problem**: Python server not receiving UDP packets

**Solutions**:

- Check firewall settings
- Verify IP address in Android app matches computer's IP
- Ensure both devices on same WiFi network
- Test with `netcat` or similar tool

```bash
# Listen for UDP packets
nc -u -l 12345
```

#### 2. Android App Crashes

**Problem**: App crashes on sensor registration

**Solutions**:

- Check permissions granted (ACTIVITY_RECOGNITION)
- Verify sensor availability on device
- Check logcat for stack traces

```bash
adb logcat | grep "SilksongController"
```

#### 3. Gesture Detection Too Sensitive/Insensitive

**Problem**: Actions triggered incorrectly

**Solutions**:

- Run calibration tool: `python src/calibrate.py`
- Manually adjust thresholds in `config.json`
- Consider environmental factors (watch fit, movement style)

#### 4. Build Issues

**Problem**: Gradle build fails

**Solutions**:

- Clean and rebuild: `./gradlew clean build`
- Invalidate Android Studio caches
- Update Gradle wrapper: `./gradlew wrapper --gradle-version=X.X.X`

### Debug Tools

#### Android

```bash
# View logs
adb logcat -s MainActivity

# Monitor sensor data
adb shell dumpsys sensorservice
```

#### Python

Add debug logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Received packet: {data}")
```

## Contributing

### Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'feat: add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Comments added for complex logic
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)

## Additional Resources

- [Android Sensor API Documentation](https://developer.android.com/guide/topics/sensors/sensors_overview)
- [Wear OS Development Guide](https://developer.android.com/training/wearables)
- [pynput Documentation](https://pynput.readthedocs.io/)
- [UDP Socket Programming](https://docs.python.org/3/library/socket.html)

## Getting Help

- **Issues**: Open a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Contact**: Reach out to project maintainers

Happy coding! 🚀
