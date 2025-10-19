# Section 1: Data Explanation

## Dataset Overview

This project uses **inertial measurement unit (IMU) sensor data** collected from a Google Pixel Watch during button-triggered gesture recording sessions. The data captures motion signals that correspond to specific game control gestures for Hollow Knight: Silksong.

### Data Components

**Sensor Streams:**
- **Linear acceleration** (3-axis): $\vec{a} = [a_x, a_y, a_z]$ measured in m/s²
- **Gyroscope rotation** (3-axis): $\vec{\omega} = [\omega_x, \omega_y, \omega_z]$ measured in rad/s
- **Sampling rate**: ~50 Hz UDP transmission from Android Wear OS app
- **File format**: CSV files with columns: `accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z`

**Gesture Classes:**

The system recognizes two sets of gestures:

1. **Binary classification** (locomotion):
   - `walk` - continuous walking motion
   - `idle` - stationary/rest state

2. **Multiclass classification** (discrete actions):
   - `jump` - upward wrist flick
   - `punch` - forward thrust
   - `turn_left` - counterclockwise rotation
   - `turn_right` - clockwise rotation
   - `idle` - rest state

### Data Collection Methodology

**Recording Process:**

Data was collected using a button-press system where:
1. User initiates recording by pressing a button
2. Performs the gesture naturally
3. Recording stops after gesture completion
4. CSV file is saved with timestamp naming: `{gesture}_{start_timestamp}_to_{end_timestamp}.csv`

**Hardware:**
- Google Pixel Watch 2 with Bosch BMI260 IMU
- Android Wear OS custom app streaming via UDP
- Network Service Discovery (NSD) for automatic connection

**Dataset Structure:**
```
main/data/button_collected/
├── jump_*.csv          # Jump gesture samples
├── punch_*.csv         # Punch gesture samples
├── turn_left_*.csv     # Left turn samples
├── turn_right_*.csv    # Right turn samples
├── walk_*.csv          # Walking samples
└── idle_*.csv          # Idle/rest samples
```

Each CSV file contains approximately 15-50 rows (0.3-1.0 seconds of sensor data at 50Hz).

### Data Characteristics

**Sample Count:** 
- Multiple samples per gesture class collected over several recording sessions
- Each gesture class has 10-30 training samples

**Quality Considerations:**
- Raw sensor data includes measurement noise from ADC quantization
- Gravity component present in accelerometer readings
- Sensor orientation varies with wrist position
- Natural variation exists between repeated gestures

### Why This Data Works for Classification

The sensor data captures the distinctive kinematic patterns of each gesture:

- **Jump**: Sharp vertical acceleration spike followed by deceleration
- **Punch**: Forward acceleration in dominant axis with high peak magnitude
- **Turn left/right**: Rotation detected primarily in gyroscope readings with opposite signs
- **Walk**: Periodic oscillation pattern at stride frequency (~2 Hz)
- **Idle**: Low-magnitude signals near gravitational baseline

These physical differences enable machine learning models to discriminate between gesture classes based on extracted statistical features.

### Data Processing Pipeline

Raw CSV files undergo the following preprocessing:

1. **Loading**: Read CSV files into pandas DataFrames
2. **Validation**: Check for minimum sample count (10+ rows)
3. **Feature extraction**: Compute statistical features from sensor windows
4. **Normalization**: Apply StandardScaler to zero-mean, unit-variance
5. **Train/test split**: 70/30 stratified split for model evaluation

The feature extraction process converts raw time-series sensor readings into fixed-length feature vectors suitable for SVM classification (detailed in Section 3).

---

## References

- Android Sensor API: https://developer.android.com/guide/topics/sensors/sensors_motion
- SciPy Statistics: https://docs.scipy.org/doc/scipy/reference/stats.html
- pandas DataFrame documentation: https://pandas.pydata.org/docs/
