# Data Collection Guide - Phase II

## Overview

This guide explains the guided data collection procedure for creating a high-fidelity IMU gesture dataset from the Pixel Watch. The goal is to collect clean, comprehensive, and perfectly labeled sensor data for gesture recognition research and development.

## Purpose

The data collection tool (`data_collector.py`) is designed to:

1. **Collect High-Quality Data**: Capture raw sensor readings during controlled gesture execution
2. **Ensure Consistency**: Use standardized stances and procedures across all samples
3. **Create Labeled Datasets**: Automatically organize and label data by stance and gesture type
4. **Support Research**: Provide data for gesture recognition algorithm development

## Prerequisites

### Hardware
- **Pixel Watch** with the Silksong Controller app installed
- **Computer** (Windows, Mac, or Linux) with Python 3.7+
- Both devices on the **same WiFi network**

### Software
- Python dependencies installed (`pip install -r requirements.txt`)
- Pixel Watch app configured and ready to stream data

### Physical Space
- Clear area for natural movement (approximately 6ft × 6ft)
- Stable, non-slippery flooring
- Comfortable temperature and lighting

## The Three User Stances

The data collection protocol uses **three distinct stances** to ensure data quality and consistency:

### 1. Combat Stance ⚔️

**Purpose**: For attack gestures (punch, slash, stab)

**Body Position**:
- Stand with feet shoulder-width apart
- Hold watch arm as if wielding a weapon
- Elbow bent at approximately 90 degrees
- Body weight balanced, ready to strike

**Watch Orientation**:
- Watch face perpendicular to ground
- Screen facing sideways (typically left for right-handed users)
- Ready to move forward/backward along arm's axis

**Key Points**:
- Maintain stable lower body
- Keep watch arm ready but relaxed
- Minimize wrist rotation during gestures

### 2. Neutral Stance 🧍

**Purpose**: For vertical movements (jump, hop, crouch)

**Body Position**:
- Natural standing position
- Feet together or slightly apart
- Arms relaxed at sides or in natural position
- Weight balanced on both feet

**Watch Orientation**:
- Watch face parallel to ground
- Screen facing UP toward sky
- Arm position allows natural vertical movement

**Key Points**:
- Maintain upright posture
- Allow natural arm swing during jumps
- Keep watch face consistently upward

### 3. Travel Stance 🚶

**Purpose**: For locomotion gestures (walk, turn, stop)

**Body Position**:
- Natural walking posture
- Arms swing naturally with stride
- Body faces direction of intended travel
- Normal gait and rhythm

**Watch Orientation**:
- Watch face parallel to ground
- Screen facing UP or slightly inward
- Arm swings naturally during walking

**Key Points**:
- Walk at a comfortable, natural pace
- Allow arms to swing freely
- Maintain consistent rhythm

## Data Collection Procedure

### Session Preparation

1. **Launch the Application**
   ```bash
   # On Unix/Mac
   cd installer
   ./run_data_collector.sh
   
   # On Windows
   cd installer
   run_data_collector.bat
   ```

2. **Verify Connection**
   - Script will auto-detect your IP address
   - Ensure Pixel Watch app is configured with this IP
   - Start streaming on the watch app

3. **Configure Session**
   - Choose number of samples per gesture (default: 5)
   - Set duration per sample (default: 3.0 seconds)
   - Review stance explanations

### Data Collection Sequence

The tool follows this sequence:

#### Combat Stance Gestures
1. **Punch**: Sharp, forward punch motion
2. **Slash**: Horizontal slashing motion across body
3. **Stab**: Quick, forward stabbing motion

#### Neutral Stance Gestures
4. **Jump**: Vertical jump motion (actual or simulated)
5. **Hop**: Small, quick hop upward
6. **Crouch**: Quick lower into crouch position

#### Travel Stance Gestures
7. **Walk**: Walk in place at natural pace
8. **Turn Left**: 180° body turn to left while walking
9. **Turn Right**: 180° body turn to right while walking
10. **Stop**: Complete stop from walking

### Per-Gesture Workflow

For each gesture, you will:

1. **Read Instructions**: Review the specific gesture requirements
2. **Adopt Stance**: Position yourself in the correct stance
3. **Ready**: Press Enter when prepared
4. **Countdown**: Wait for 3-2-1 countdown
5. **Execute**: Perform gesture when "GO!" appears
6. **Record**: Data is collected for specified duration
7. **Review**: Check if sample was successful
8. **Repeat**: Complete all samples for the gesture

### Execution Guidelines

#### General Principles
- **Natural Movement**: Don't exaggerate or over-perform
- **Crisp Execution**: Be deliberate but not theatrical
- **Consistent Stance**: Maintain stance throughout recording
- **Wait for Signal**: Always wait for "GO!" before moving
- **Take Breaks**: Rest between gestures if needed

#### Gesture-Specific Tips

**Punch**:
- Start from combat stance
- Sharp, linear motion forward
- Return to ready position
- Keep wrist stable

**Slash**:
- Horizontal motion across body
- Follow through naturally
- Maintain consistent height
- Similar to sword swing

**Stab**:
- Quick, direct forward thrust
- Shorter motion than punch
- Immediate retraction
- Focus on acceleration

**Jump**:
- Vertical motion only
- Natural jumping form
- Land softly and controlled
- Actual jump or simulated arm motion

**Hop**:
- Smaller than jump
- Quick, bouncy motion
- Minimal height needed
- Focus on rhythm

**Crouch**:
- Quick bend at knees
- Natural squat motion
- Controlled descent
- Can hold briefly at bottom

**Walk**:
- Natural walking pace
- March in place
- Consistent rhythm
- Natural arm swing

**Turn Left/Right**:
- Begin walking in place
- Perform full 180° body rotation
- Maintain walking rhythm during turn
- End facing opposite direction

**Stop**:
- Begin walking
- Come to natural complete stop
- Decelerate naturally
- Settle into still position

## Data Output Structure

### Directory Layout

```
data_collection/
└── YYYYMMDD_HHMMSS/           # Timestamp of session
    ├── combat/
    │   ├── punch/
    │   │   ├── punch_sample_001.json
    │   │   ├── punch_sample_002.json
    │   │   └── ...
    │   ├── slash/
    │   └── stab/
    ├── neutral/
    │   ├── jump/
    │   ├── hop/
    │   └── crouch/
    ├── travel/
    │   ├── walk/
    │   ├── turn_left/
    │   ├── turn_right/
    │   └── stop/
    └── metadata/
        └── session_info.json
```

### Data File Format

Each gesture sample is saved as a JSON file containing:

```json
{
  "metadata": {
    "stance": "combat",
    "gesture": "punch",
    "sample_number": 1,
    "duration_seconds": 3.0,
    "timestamp": "2025-10-13T16:45:30.123456",
    "packet_count": 450
  },
  "sensor_data": [
    {
      "sensor": "rotation_vector",
      "timestamp_ns": 1234567890123456,
      "values": {"x": 0.1, "y": 0.2, "z": 0.3, "w": 0.9},
      "collection_timestamp": 1697213130.456
    },
    {
      "sensor": "linear_acceleration",
      "timestamp_ns": 1234567890234567,
      "values": {"x": 2.3, "y": -1.1, "z": 0.5},
      "collection_timestamp": 1697213130.467
    },
    {
      "sensor": "gravity",
      "timestamp_ns": 1234567890345678,
      "values": {"x": 0.1, "y": 9.7, "z": 0.3},
      "collection_timestamp": 1697213130.478
    }
  ]
}
```

### Sensor Types Collected

1. **rotation_vector**: Device orientation as quaternion (x, y, z, w)
2. **linear_acceleration**: Acceleration minus gravity (x, y, z in m/s²)
3. **gravity**: Gravity vector (x, y, z in m/s²)

### Session Metadata

The `session_info.json` file contains:

```json
{
  "session_timestamp": "20251013_164530",
  "session_start": "2025-10-13T16:45:30.123456",
  "session_end": "2025-10-13T17:15:45.789012",
  "listen_ip": "192.168.1.113",
  "listen_port": 12345,
  "samples_per_gesture": 5,
  "duration_per_sample": 3.0,
  "sensors_expected": [
    "rotation_vector",
    "linear_acceleration",
    "gravity"
  ],
  "status": "completed"
}
```

## Troubleshooting

### No Data Received

**Problem**: "No data received!" warning appears

**Solutions**:
1. Verify Pixel Watch app is streaming (toggle switch on watch)
2. Confirm both devices are on same WiFi network
3. Check IP address matches in watch app and config.json
4. Ensure firewall allows UDP port 12345
5. Restart watch app and try again

### Port Already in Use

**Problem**: "Could not bind to UDP port" error

**Solutions**:
1. Stop `udp_listener.py` if running
2. Close `calibrate.py` if running
3. Check for other processes using port 12345
4. Wait a few seconds and try again

### Inconsistent Sensor Data

**Problem**: Sensor distribution shows missing sensors

**Solutions**:
1. Check watch app is configured for all three sensors:
   - `Sensor.TYPE_ROTATION_VECTOR`
   - `Sensor.TYPE_LINEAR_ACCELERATION`
   - `Sensor.TYPE_GRAVITY`
2. Verify sensor permissions granted on watch
3. Restart watch app to reinitialize sensors

### Low Packet Count

**Problem**: Few packets collected per sample

**Solutions**:
1. Check WiFi signal strength
2. Move closer to WiFi router
3. Reduce interference (other devices, walls)
4. Increase sample duration

## Best Practices

### Before Starting
- [ ] Read this entire guide
- [ ] Practice each stance without recording
- [ ] Ensure comfortable clothing and footwear
- [ ] Clear physical space of obstacles
- [ ] Charge Pixel Watch to at least 50%
- [ ] Close unnecessary apps on both devices

### During Collection
- [ ] Maintain consistent energy level
- [ ] Take breaks between stances (2-3 minutes)
- [ ] Stay hydrated
- [ ] Focus on quality over speed
- [ ] Redo samples if they feel incorrect
- [ ] Note any issues or anomalies

### After Collection
- [ ] Review data files for completeness
- [ ] Check packet counts are reasonable
- [ ] Verify all gestures were collected
- [ ] Back up data to external storage
- [ ] Document any deviations from protocol

## Data Quality Checklist

Use this checklist to verify data quality:

### Per Sample
- [ ] Sample contains expected number of packets (typically 300-500 for 3s)
- [ ] All three sensor types present
- [ ] No large gaps in timestamps
- [ ] Gesture executed during recording window
- [ ] Stance maintained throughout

### Per Gesture
- [ ] All samples completed
- [ ] Consistent execution across samples
- [ ] Clear gesture signatures visible
- [ ] No obvious outliers or errors

### Per Session
- [ ] All gestures collected
- [ ] All stances represented
- [ ] Session metadata complete
- [ ] Directory structure correct
- [ ] Consistent sample quality

## Next Steps

After collecting data:

1. **Data Analysis**
   - Load data using Python/pandas
   - Visualize sensor signals
   - Identify gesture patterns

2. **Feature Engineering**
   - Extract statistical features
   - Calculate derived metrics
   - Normalize and scale data

3. **Model Training**
   - Split train/validation/test sets
   - Train gesture recognition models
   - Evaluate performance

4. **Integration**
   - Incorporate trained models into application
   - Test real-time gesture recognition
   - Fine-tune thresholds and parameters

## References

- [Android Sensor Overview](https://developer.android.com/guide/topics/sensors/sensors_overview)
- [Sensor Types Documentation](https://developer.android.com/reference/android/hardware/Sensor)
- [Wear OS Sensor Best Practices](https://developer.android.com/training/wearables/sensors)

## Support

For issues or questions:
1. Review troubleshooting section above
2. Check existing issues on GitHub repository
3. Review `docs/reflections.md` for technical insights
4. Consult `QUICK_REFERENCE.md` for quick commands

---

**Version**: 1.0.0  
**Last Updated**: October 13, 2025  
**Part of**: Silksong Controller v3 - Phase II
