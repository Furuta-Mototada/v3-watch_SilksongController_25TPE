# Android 2x3 Button Grid Data Collector

**Status**: Development Scaffold Ready  
**Purpose**: Button-based gesture labeling for ML training data collection  
**Architecture**: Phone app that bridges Pixel Watch sensor stream with Python ML pipeline

---

## Overview

This Android app provides a **2x3 button grid interface** for precise, real-time labeling of motion gestures during data collection. It addresses data quality issues from voice-based labeling by giving users direct control over label boundaries with press-and-hold interactions.

### Key Features

- 📱 **2x3 Button Grid**: Walk, Idle, Punch, Jump, Turn Left, Turn Right
- 🔢 **Real-time Count Display**: Track data balance across all gestures
- ⏱️ **Precise Timestamps**: Exact start/end times for each recording
- 🔄 **Three-Stage Pipeline**: Watch → Phone → MacBook via UDP
- 👆 **Press-and-Hold**: Natural interaction - hold to record, release to save
- 🎨 **Visual Feedback**: Color-coded states and count tracking

## Architecture

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ Pixel Watch  │─UDP──│Android Phone │─UDP──│   MacBook    │
│ (Left Wrist) │      │(Right Hand)  │      │  (Python)    │
└──────────────┘      └──────────────┘      └──────────────┘
  Sensor Data           Button Events         Data Storage
  50Hz IMU              Label + Timestamp     CSV + Labels
```

**Watch App** (unchanged): `../Android/` - Streams sensor data continuously via UDP with NSD

**This App**: 
- Displays 2x3 button grid 
- User presses button → sends "label_start" event
- User releases button → sends "label_end" event  
- Updates count display for data balance tracking

**Python Backend**: `../src/button_data_collector.py` (to be created)
- Receives sensor data from watch
- Receives label events from this app
- Saves labeled CSV files with proper naming

## Button Layout

```
┌──────────────┬──────────────┐
│    WALK      │    IDLE      │  Row 1: Locomotion
│   Count: 0   │   Count: 0   │  (Hold 5-10 sec)
├──────────────┼──────────────┤
│    PUNCH     │    JUMP      │  Row 2: Actions
│   Count: 0   │   Count: 0   │  (Tap 1-2 sec)
├──────────────┼──────────────┤
│  TURN_LEFT   │  TURN_RIGHT  │  Row 3: Turns
│   Count: 0   │   Count: 0   │  (Tap <1 sec)
└──────────────┴──────────────┘
```

**Target Data Balance**: 30-50 samples per gesture

## Implementation Status

**✅ COMPLETE**: Full implementation with all core features

See [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for detailed information including:
- Complete feature list
- Build and installation instructions
- Usage guide and testing checklist
- UDP protocol specification
- Troubleshooting guide

**Files Implemented**:
1. `MainActivity.kt` - Complete UI with 2x3 button grid
2. `DataCollectorViewModel.kt` - State management and UDP client
3. `AndroidManifest.xml` - Required permissions
4. Updated `build.gradle.kts` and `libs.versions.toml`

**Ready to Build**: Open in Android Studio and run. See implementation status doc for build instructions.

## UDP Label Event Protocol

**Message Format** (JSON):
```json
{
  "type": "label_event",
  "action": "punch",
  "event": "start" | "end",
  "timestamp_ms": 1697654789123,
  "count": 15
}
```

**Target Host**: Auto-discovered via NSD or manual IP entry  
**Port**: Same as watch app (default: 5005)

## Usage Flow

1. **Setup**: Launch watch app (`../Android/`) first - starts sensor streaming
2. **Launch**: Open this app on phone (held in right hand)
3. **Connect**: Auto-discover MacBook via NSD or enter IP manually
4. **Collect**: Press and hold button → perform gesture → release button
5. **Monitor**: Watch count displays to maintain data balance
6. **Complete**: Collect 30-50 samples per gesture (15-20 minutes total)

## Data Output (Python Side)

**File Format**: `{action}_{start_timestamp}_to_{end_timestamp}.csv`

**Example**:
```
walk_1697654789123_to_1697654795000.csv
punch_1697654796000_to_1697654796891.csv
turn_left_1697654797000_to_1697654797456.csv
```

## Development Setup

**Requirements**:
- Android Studio Hedgehog or later
- Kotlin 1.9+
- Jetpack Compose 1.5+
- Minimum SDK: 30 (Android 11)
- Target SDK: 34 (Android 14)

**Build**:
```bash
cd Android_2_Grid
./gradlew build
```

**Run**:
- Connect Android phone via USB or WiFi debugging
- Click Run (▶️) in Android Studio
- Select phone device (not watch)

## Key Implementation Files

**Current**:
- `app/src/main/java/com/example/grid_watch_udp_datacollector/MainActivity.kt` - Skeleton template

**To Create**:
- `ButtonGridScreen.kt` - Main 2x3 grid Composable
- `DataCollectorViewModel.kt` - State management for counts and recording
- `UDPClient.kt` - Label event transmission
- `NSDHelper.kt` - Service discovery (can reuse from `../Android/`)

## Design Specifications

**Button Size**: 120x120 dp (thumb-optimized)

**Colors**:
- Unpressed: Gray (#757575)
- Recording: Green (#4CAF50)
- Post-Record Flash: Blue (#2196F3)

**Count Colors**:
- 0-9: Red (need more data)
- 10-29: Yellow (building)
- 30+: Green (sufficient)

**Typography**:
- Action label: 18sp, bold
- Count: 14sp, regular

## Testing Checklist

- [ ] Button press triggers haptic feedback
- [ ] Button state changes color when pressed
- [ ] UDP label_start event sent on press
- [ ] UDP label_end event sent on release
- [ ] Count increments after release
- [ ] Counts persist across app restarts
- [ ] Can connect to Python backend
- [ ] Data files created with correct naming
- [ ] No timestamp mismatches
- [ ] All 6 buttons work independently

## Related Documentation

📄 **Complete Protocol Specification**: `../docs/BUTTON_DATA_COLLECTION_PROTOCOL.md`
- Detailed interaction model
- Dual classifier rationale
- Data integrity considerations
- Implementation phases
- Testing and validation protocols

📄 **Design Exploration**: `../docs/ALTERNATIVE_DATA_COLLECTION_BRAINSTORM.md`
- Expert panel analysis
- Trade-off discussion
- Voice vs. button comparison

📄 **Watch App**: `../Android/README.md` (if exists)
- Sensor streaming implementation
- NSD discovery setup

## Notes

**Why "2_Grid" instead of "Grid"?**
- Distinguishes from original `Android/` folder (watch app)
- This is the second Android component in the project
- Reserves `Android/` for Pixel Watch app (v1)
- This folder is for phone app (v2 interface)

**Why Not Integrate Into Watch App?**
- Pixel Watch has limited screen space
- Phone provides better UI for button grid
- Separation of concerns (sensing vs. labeling)
- Allows independent development and testing

**Future Enhancements**:
- Session management UI
- Data export to Google Drive
- Live sensor visualization
- Multi-user mode
- External Bluetooth button support
