# Changelog

All notable changes to the Silksong Motion Controller project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.2.0] - 2025-10-15

### Added - Phase IV: Multi-Threaded ML Architecture

- **MAJOR FEATURE**: Decoupled multi-threaded architecture for low-latency ML inference
- **Thread 1 (Collector)**: Dedicated UDP listener thread pushing sensor data to queue
- **Thread 2 (Predictor)**: Continuous ML inference thread with 0.3s micro-windows
- **Thread 3 (Actor)**: Keyboard action executor with confidence gating
- **Micro-Windows**: Reduced window size from 2.5s to 0.3s for faster gesture detection
- **Confidence Gating**: Requires 5 consecutive matching predictions for stable state changes
- **Thread-Safe Queues**: Producer-consumer pattern using `queue.Queue` for inter-thread communication

### Changed - Phase IV: Performance Improvements

- **Latency Reduction**: Reduced overall latency from 1+ seconds to <500ms
- **Continuous Inference**: Predictor runs as fast as CPU allows (no fixed intervals)
- **Architecture**: Decoupled components eliminate blocking between network, processing, and actions
- **Window Size**: `WINDOW_SIZE_SEC = 0.3` (was 2.5 seconds)
- **Startup Message**: Now shows "ML-POWERED (Multi-Threaded)" with architecture details
- **All Gestures ML**: Jump, punch, turn, and walk all handled by ML model (no hybrid thresholds)

### Technical Rationale

**Problem Identified**: Synchronous single-threaded architecture caused bottlenecks:
- Network receive blocked by ML processing
- ML processing blocked by keyboard actions
- Fixed prediction intervals (0.5s) added unnecessary latency
- Long sliding windows (2.5s) delayed gesture recognition

**Solution Implemented**: Multi-threaded producer-consumer architecture:
- **Collector** runs at network speed, never blocked
- **Predictor** runs at CPU speed, continuous inference
- **Actor** uses confidence gating to prevent false positives
- **Micro-windows** capture fast gestures quickly
- **Thread-safe queues** enable parallel processing

### Performance Metrics

- **Latency**: <500ms (down from 1+ second)
- **CPU Usage**: ~30-40% single core (acceptable)
- **Responsiveness**: Near real-time gesture detection
- **Accuracy**: Maintained with confidence gating

---

## [3.1.0] - 2025-10-14

### Added - Phase II: Hybrid Data Collection Protocol

- **CRITICAL IMPROVEMENT**: Hybrid data collection protocol distinguishing event-based vs state-based gestures
- `collection_mode` attribute for all gestures in `GESTURES` dictionary
- `record_continuous_gesture()` method for state-based gestures (WALK)
- `_save_continuous_recording()` method for continuous mode data export
- `CONTINUOUS_RECORDING_DURATION_MIN` configuration parameter (2.5 minutes)
- Real-time progress bar for continuous recording with elapsed/remaining time display
- Comprehensive documentation: `docs/Phase_II/HYBRID_COLLECTION_PROTOCOL.md`

### Added - Phase II: Command-Line Interface

- **NEW FEATURE**: Flexible CLI arguments for selective data collection
- `--gestures` flag to collect specific gestures (e.g., `--gestures punch,jump`)
- `--samples N` flag to customize sample count for snippet mode
- `--duration SEC` flag to customize snippet recording duration
- `--continuous-duration MIN` flag to customize continuous recording duration
- `--session-id ID` flag to resume interrupted sessions or add to existing data
- `--list-gestures` flag to display all available gestures and their modes
- `--help` for comprehensive usage information
- Documentation: `docs/Phase_II/CLI_REFERENCE.md`

### Changed - Phase II: Data Collection Architecture

- **BREAKING**: `data_collector.py` now uses TWO collection modes:
  - **Snippet Mode**: PUNCH, JUMP, TURN, NOISE (40 samples × 2.5s each)
  - **Continuous Mode**: WALK (1 session × 2.5 minutes)
- WALK gesture output changed from `walk_sample01.csv...walk_sample40.csv` to single `walk_continuous.csv`
- Updated welcome message to reflect hybrid approach and benefits
- Collection time reduced from ~90 minutes to ~78 minutes (-13%)
- `record_gesture()` method now explicitly documented as "snippet mode"

### Technical Rationale

**Problem Identified**: Original uniform snippet-based approach was suboptimal for continuous/state-based gestures like WALK. Short, isolated snippets failed to capture:
- Temporal dynamics and transitions (starting, maintaining, stopping)
- Cyclical patterns inherent to walking
- Natural variations in pace and intensity

**Solution Implemented**: Hybrid protocol that treats gestures according to their intrinsic nature:

1. **Event-Based Gestures** (PUNCH, JUMP, TURN):
   - Atomic actions with clear start/end
   - Snippet mode remains optimal
   - Each sample is independent

2. **State-Based Gestures** (WALK):
   - Represents a persistent state/mode
   - Continuous recording captures full temporal context
   - Single 2.5-minute recording → ~1,475 training examples via sliding window
   - 37x increase in effective training data

**Impact on ML Pipeline**:
- Training data now matches inference sliding window behavior
- Model will see gesture in all phases (not just "perfect" mid-gesture)
- Significantly improved robustness and accuracy expected

### Documentation

- Added `HYBRID_COLLECTION_PROTOCOL.md` with full technical specification
- Includes theoretical foundation, implementation details, and ML pipeline integration guide
- Documents expected dataset structure and validation procedures

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
