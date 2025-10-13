# Quick Reference Card

## 🚀 Quick Commands

### Python Controller

```bash
# Run the main controller
python src/udp_listener.py

# Run calibration
python src/calibrate.py

# Run data collection (Phase II)
python src/data_collector.py

# Or use installer scripts
cd installer
./run_controller.sh         # Unix/Mac
./run_data_collector.sh     # Unix/Mac
run_controller.bat          # Windows
run_data_collector.bat      # Windows
```

### Android Development

```bash
cd Android

# Build
./gradlew assembleDebug

# Install to watch
./gradlew installDebug

# View logs
adb logcat | grep MainActivity
```

## 📦 Project Info

**Package Name**: `com.cvk.silksongcontroller`
**Python Entry**: `src/udp_listener.py`
**Default Port**: `12345`
**Config File**: `config.json`

## 📁 Important Paths

| Component | Location |
|-----------|----------|
| Android Main Activity | `Android/app/src/main/java/com/cvk/silksongcontroller/MainActivity.kt` |
| Python Controller | `src/udp_listener.py` |
| Calibration Tool | `src/calibrate.py` |
| Data Collector | `src/data_collector.py` |
| Configuration | `config.json` |
| Documentation | `docs/` |
| Installation Scripts | `installer/` |

## 🔧 Quick Fixes

### Can't receive data?

1. Check watch and PC on same WiFi
2. Update IP in watch app
3. Check firewall allows UDP port 12345

### Gestures not working?

1. Run calibration: `python src/calibrate.py`
2. Edit thresholds in `config.json`
3. Check sensor permissions granted

### Build errors?

```bash
cd Android
./gradlew clean
./gradlew build
```

## 📚 Documentation

- **User Guide**: `README.md`
- **Developer Guide**: `docs/DEVELOPER_GUIDE.md`
- **Project Structure**: `docs/PROJECT_STRUCTURE.md`
- **Data Collection Guide**: `docs/DATA_COLLECTION_GUIDE.md`
- **Changes**: `CHANGELOG.md`
- **Migration Info**: `MIGRATION_SUMMARY.md`

## 🎮 Default Controls

- **Walk**: Step detection
- **Jump**: Upward acceleration (Z-axis)
- **Attack**: Punch motion (XY acceleration)
- **Turn**: Rotation threshold

Customize in `config.json` → `keyboard_mappings`

## 🔗 Quick Links

- [v2 Repository](https://github.com/CarlKho-Minerva/v2_SilksongController_25TPE)
- [Android Sensor Docs](https://developer.android.com/guide/topics/sensors/sensors_overview)
- [Wear OS Guide](https://developer.android.com/training/wearables)

---

**Version**: 3.0.0 | **Last Updated**: October 13, 2025
