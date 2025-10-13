# Changelog

All notable changes to the Silksong Motion Controller project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2025-10-13

### Added

- Pixel Watch compatibility and optimization
- Comprehensive project documentation in `docs/PROJECT_STRUCTURE.md`
- Organized directory structure with `src/` and `docs/` directories
- Enhanced README with detailed setup instructions and feature descriptions

### Changed

- **BREAKING**: Android package renamed from `com.example.silksongmotioncontroller` to `com.cvk.silksongcontroller`
- **BREAKING**: Python source files moved to `src/` directory
- Project name updated to "Silksong Controller v3"
- Android project name updated in `settings.gradle.kts`
- Installer scripts updated to reference new `src/` directory structure
- Documentation consolidated in `docs/` directory (previously `docs_nontechnical/`)

### Removed

- Old package directory `com/example/silksongmotioncontroller`
- Redundant `docs_nontechnical/` directory (merged into `docs/`)

### Migration Guide

If you're upgrading from v2:

1. **Android App**: Uninstall the old app and reinstall the new one with updated package name
2. **Python Scripts**: Update any custom scripts to reference `src/udp_listener.py` instead of `udp_listener.py`
3. **Configuration**: Your `config.json` remains compatible with no changes needed

## [2.x.x] - Previous Version

See [v2_SilksongController_25TPE](https://github.com/CarlKho-Minerva/v2_SilksongController_25TPE) repository for v2 history.

## Future Roadmap

- [ ] Machine learning gesture recognition
- [ ] iOS/Apple Watch support
- [ ] Web-based configuration interface
- [ ] Additional game profiles
- [ ] Gesture recording and playback
