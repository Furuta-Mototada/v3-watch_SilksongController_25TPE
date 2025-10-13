# Training Data Format Specification

This document describes the expected format and structure of training data for the ML pipeline.

## Directory Structure

```
training_data/
└── session_20251013_141530/           # Session directory (timestamp-based)
    ├── punch_forward_sample01.csv     # Gesture sample 1
    ├── punch_forward_sample02.csv     # Gesture sample 2
    ├── punch_forward_sample03.csv     # Gesture sample 3
    ├── punch_forward_sample04.csv     # Gesture sample 4
    ├── punch_forward_sample05.csv     # Gesture sample 5
    ├── punch_upward_sample01.csv
    ├── punch_upward_sample02.csv
    ├── ...
    ├── rest_sample05.csv
    └── session_metadata.json          # Session metadata
```

### Session Directory Naming

Format: `session_YYYYMMDD_HHMMSS`

Example: `session_20251013_141530`
- Date: October 13, 2025
- Time: 14:15:30 (2:15:30 PM)

### CSV File Naming

Format: `{gesture_name}_sample{number}.csv`

Examples:
- `punch_forward_sample01.csv`
- `jump_quick_sample03.csv`
- `turn_left_sample05.csv`

## CSV File Format

Each CSV file contains time-series sensor data for a single gesture recording (typically 3 seconds).

### Column Schema

```csv
timestamp,sensor,gesture,stance,sample,rot_x,rot_y,rot_z,rot_w,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z
```

### Column Descriptions

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `timestamp` | float | Time since recording start (seconds) | 0.001, 0.012, 0.023 |
| `sensor` | string | Sensor type | `rotation_vector`, `linear_acceleration`, `gyroscope` |
| `gesture` | string | Gesture label | `punch_forward`, `jump_quick` |
| `stance` | string | Physical stance | `combat`, `neutral`, `travel` |
| `sample` | int | Sample number (1-5) | 1, 2, 3, 4, 5 |
| `rot_x` | float | Rotation quaternion X | 0.123 |
| `rot_y` | float | Rotation quaternion Y | -0.456 |
| `rot_z` | float | Rotation quaternion Z | 0.789 |
| `rot_w` | float | Rotation quaternion W | 0.987 |
| `accel_x` | float | Linear acceleration X (m/s²) | 12.5 |
| `accel_y` | float | Linear acceleration Y (m/s²) | 3.2 |
| `accel_z` | float | Linear acceleration Z (m/s²) | -1.1 |
| `gyro_x` | float | Angular velocity X (rad/s) | 0.5 |
| `gyro_y` | float | Angular velocity Y (rad/s) | 2.1 |
| `gyro_z` | float | Angular velocity Z (rad/s) | 0.3 |

### Sensor-Specific Columns

Each row contains data from ONE sensor type. Unused columns are empty:

**rotation_vector rows:**
- Have values in: `rot_x`, `rot_y`, `rot_z`, `rot_w`
- Empty: `accel_x/y/z`, `gyro_x/y/z`

**linear_acceleration rows:**
- Have values in: `accel_x`, `accel_y`, `accel_z`
- Empty: `rot_x/y/z/w`, `gyro_x/y/z`

**gyroscope rows:**
- Have values in: `gyro_x`, `gyro_y`, `gyro_z`
- Empty: `rot_x/y/z/w`, `accel_x/y/z`

## Example CSV Content

```csv
timestamp,sensor,gesture,stance,sample,rot_x,rot_y,rot_z,rot_w,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z
0.001,rotation_vector,punch_forward,combat,1,0.123,-0.456,0.789,0.987,,,,,
0.012,linear_acceleration,punch_forward,combat,1,,,,,12.5,3.2,-1.1,,
0.015,gyroscope,punch_forward,combat,1,,,,,,,0.5,2.1,0.3
0.023,rotation_vector,punch_forward,combat,1,0.124,-0.457,0.788,0.986,,,,,
0.034,linear_acceleration,punch_forward,combat,1,,,,,12.7,3.3,-1.0,,
0.037,gyroscope,punch_forward,combat,1,,,,,,,0.6,2.2,0.4
...
2.987,rotation_vector,punch_forward,combat,1,0.089,-0.423,0.801,0.991,,,,,
2.998,linear_acceleration,punch_forward,combat,1,,,,,1.2,0.5,-0.2,,
```

## Gesture Labels

Standard gestures recognized by the system:

### Combat Stance
- `punch_forward` - Forward punch motion
- `punch_upward` - Upward punch motion

### Neutral Stance
- `jump_quick` - Quick upward jerk
- `jump_sustained` - Sustained upward motion

### Travel Stance
- `turn_left` - Rotate to face left
- `turn_right` - Rotate to face right
- `walk_forward` - Walking motion

### Special
- `rest` - No motion (baseline)

## Session Metadata

The `session_metadata.json` file contains session information:

```json
{
  "session_id": "20251013_141530",
  "start_time": "2025-10-13T14:15:30.123456",
  "end_time": "2025-10-13T14:45:12.654321",
  "device": "Samsung Galaxy Watch 4",
  "gestures_recorded": [
    "punch_forward",
    "punch_upward",
    "jump_quick",
    "jump_sustained",
    "turn_left",
    "turn_right",
    "walk_forward",
    "rest"
  ],
  "samples_per_gesture": 5,
  "recording_duration_sec": 3.0,
  "sensor_frequency_hz": 50,
  "notes": "User notes or comments"
}
```

## Data Quality Requirements

### Minimum Requirements

For successful model training:

1. **At least 5 samples per gesture**
   - Recommended: 10+ samples for better generalization

2. **Consistent duration**
   - Each sample should be ~3 seconds
   - Minimum 100 sensor readings per sample

3. **All three sensor types**
   - rotation_vector
   - linear_acceleration
   - gyroscope

4. **Clean recordings**
   - Follow stance instructions
   - Execute gestures consistently
   - Avoid interruptions

### Sampling Rate

- **Target**: 50 Hz (50 readings per second)
- **Minimum**: 30 Hz
- **Each 3-second recording**: ~150-200 total sensor readings (across all sensors)

## Data Validation Checklist

Before using data for training:

- [ ] All required gesture types present
- [ ] 5+ samples per gesture
- [ ] CSV files have correct column names
- [ ] No empty CSV files
- [ ] Timestamp ranges from ~0.0 to ~3.0 seconds
- [ ] All three sensor types present in each file
- [ ] No excessive missing values
- [ ] session_metadata.json exists and is valid JSON

## Loading Training Data

The notebook automatically loads data using:

```python
# Load all sessions
all_data = load_all_training_data(base_dir="training_data")

# Data is combined from all sessions
# Each row represents one sensor reading
# Grouped by gesture + sample for feature extraction
```

## Troubleshooting

### Missing sensor data

**Problem**: Some CSV files missing sensor types

**Solution**: 
- Re-run data collection for affected gestures
- Ensure smartwatch sensors are enabled
- Check Android permissions

### Inconsistent sample counts

**Problem**: Different gestures have different numbers of samples

**Solution**:
- The model handles class imbalance
- Recommendation: Balance sample counts across gestures
- Use stratified sampling in train/test split

### Large file sizes

**Problem**: CSV files are unexpectedly large

**Cause**: High sampling rate or long recordings

**Solution**:
- Normal: 10-50 KB per file
- Large: >100 KB per file
- Check recording duration is ~3 seconds
- Verify sensor sampling rate

## References

- **Data Collection Guide**: `docs/Phase_II/DATA_COLLECTION_GUIDE.md`
- **Data Collector Script**: `src/data_collector.py`
- **ML Pipeline Notebook**: `CS156_Silksong_Watch.ipynb`

---

**Data collection creates the foundation for model success!**
