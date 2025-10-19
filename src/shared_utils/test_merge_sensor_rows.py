#!/usr/bin/env python3
"""
Unit tests for merge_sensor_rows.py

Tests the sensor row merging logic to ensure proper data fusion.
"""

import pandas as pd
import numpy as np
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add parent directory to path to import merge_sensor_rows
sys.path.insert(0, os.path.dirname(__file__))
from merge_sensor_rows import merge_sensors_by_timestamp


def test_basic_merge():
    """Test basic merging of three sensor types at same timestamp."""
    data = {
        'accel_x': [1.0, 0.0, 0.0],
        'accel_y': [2.0, 0.0, 0.0],
        'accel_z': [3.0, 0.0, 0.0],
        'gyro_x': [0.0, 4.0, 0.0],
        'gyro_y': [0.0, 5.0, 0.0],
        'gyro_z': [0.0, 6.0, 0.0],
        'rot_w': [1.0, 1.0, 0.7],
        'rot_x': [0.0, 0.0, 0.1],
        'rot_y': [0.0, 0.0, 0.2],
        'rot_z': [0.0, 0.0, 0.3],
        'sensor': ['linear_acceleration', 'gyroscope', 'rotation_vector'],
        'timestamp': [100, 100, 100]
    }
    df = pd.DataFrame(data)
    
    merged = merge_sensors_by_timestamp(df)
    
    # Should have exactly 1 row
    assert len(merged) == 1, f"Expected 1 row, got {len(merged)}"
    
    # Check values are merged correctly
    row = merged.iloc[0]
    assert row['accel_x'] == 1.0, f"Expected accel_x=1.0, got {row['accel_x']}"
    assert row['accel_y'] == 2.0
    assert row['accel_z'] == 3.0
    assert row['gyro_x'] == 4.0
    assert row['gyro_y'] == 5.0
    assert row['gyro_z'] == 6.0
    assert row['rot_w'] == 0.7
    assert row['rot_x'] == 0.1
    assert row['rot_y'] == 0.2
    assert row['rot_z'] == 0.3
    assert row['timestamp'] == 100
    
    # Should not have 'sensor' column
    assert 'sensor' not in merged.columns
    
    print("✓ Basic merge test passed")


def test_multiple_timestamps():
    """Test merging with multiple different timestamps."""
    data = {
        'accel_x': [1.0, 0.0, 2.0, 0.0],
        'accel_y': [0.0, 0.0, 0.0, 0.0],
        'accel_z': [0.0, 0.0, 0.0, 0.0],
        'gyro_x': [0.0, 3.0, 0.0, 4.0],
        'gyro_y': [0.0, 0.0, 0.0, 0.0],
        'gyro_z': [0.0, 0.0, 0.0, 0.0],
        'rot_w': [1.0, 1.0, 1.0, 1.0],
        'rot_x': [0.0, 0.0, 0.0, 0.0],
        'rot_y': [0.0, 0.0, 0.0, 0.0],
        'rot_z': [0.0, 0.0, 0.0, 0.0],
        'sensor': ['linear_acceleration', 'gyroscope', 'linear_acceleration', 'gyroscope'],
        'timestamp': [100, 100, 200, 200]
    }
    df = pd.DataFrame(data)
    
    merged = merge_sensors_by_timestamp(df)
    
    # Should have 2 rows (one per unique timestamp)
    assert len(merged) == 2, f"Expected 2 rows, got {len(merged)}"
    
    # Check first timestamp
    row1 = merged[merged['timestamp'] == 100].iloc[0]
    assert row1['accel_x'] == 1.0
    assert row1['gyro_x'] == 3.0
    
    # Check second timestamp
    row2 = merged[merged['timestamp'] == 200].iloc[0]
    assert row2['accel_x'] == 2.0
    assert row2['gyro_x'] == 4.0
    
    print("✓ Multiple timestamps test passed")


def test_missing_sensors():
    """Test merging when some sensors are missing at a timestamp."""
    data = {
        'accel_x': [1.0, 0.0],
        'accel_y': [2.0, 0.0],
        'accel_z': [3.0, 0.0],
        'gyro_x': [0.0, 0.0],
        'gyro_y': [0.0, 0.0],
        'gyro_z': [0.0, 0.0],
        'rot_w': [1.0, 0.8],
        'rot_x': [0.0, 0.1],
        'rot_y': [0.0, 0.2],
        'rot_z': [0.0, 0.3],
        'sensor': ['linear_acceleration', 'rotation_vector'],
        'timestamp': [100, 100]
    }
    df = pd.DataFrame(data)
    
    merged = merge_sensors_by_timestamp(df)
    
    # Should have 1 row
    assert len(merged) == 1
    
    row = merged.iloc[0]
    # Accel values should be present
    assert row['accel_x'] == 1.0
    assert row['accel_y'] == 2.0
    assert row['accel_z'] == 3.0
    
    # Gyro values should be defaults (0.0)
    assert row['gyro_x'] == 0.0
    assert row['gyro_y'] == 0.0
    assert row['gyro_z'] == 0.0
    
    # Rotation values should be present
    assert row['rot_w'] == 0.8
    assert row['rot_x'] == 0.1
    
    print("✓ Missing sensors test passed")


def test_empty_dataframe():
    """Test handling of empty DataFrame."""
    df = pd.DataFrame()
    merged = merge_sensors_by_timestamp(df)
    
    assert merged.empty, "Empty DataFrame should return empty DataFrame"
    print("✓ Empty DataFrame test passed")


def test_column_order():
    """Test that output columns are in correct order."""
    data = {
        'accel_x': [1.0], 'accel_y': [2.0], 'accel_z': [3.0],
        'gyro_x': [4.0], 'gyro_y': [5.0], 'gyro_z': [6.0],
        'rot_w': [0.7], 'rot_x': [0.1], 'rot_y': [0.2], 'rot_z': [0.3],
        'sensor': ['linear_acceleration'],
        'timestamp': [100]
    }
    df = pd.DataFrame(data)
    
    merged = merge_sensors_by_timestamp(df)
    
    expected_columns = [
        'accel_x', 'accel_y', 'accel_z',
        'gyro_x', 'gyro_y', 'gyro_z',
        'rot_w', 'rot_x', 'rot_y', 'rot_z',
        'timestamp'
    ]
    
    assert list(merged.columns) == expected_columns, \
        f"Column order mismatch. Expected {expected_columns}, got {list(merged.columns)}"
    
    print("✓ Column order test passed")


def test_real_data_reduction():
    """Test with real data pattern - verify row reduction."""
    # Simulate real data with 3 sensors per timestamp
    timestamps = [100, 100, 100, 200, 200, 200, 300, 300, 300]
    sensors = ['linear_acceleration', 'gyroscope', 'rotation_vector'] * 3
    
    data = {
        'accel_x': [1.0, 0.0, 0.0, 2.0, 0.0, 0.0, 3.0, 0.0, 0.0],
        'accel_y': [0.0] * 9,
        'accel_z': [0.0] * 9,
        'gyro_x': [0.0, 4.0, 0.0, 0.0, 5.0, 0.0, 0.0, 6.0, 0.0],
        'gyro_y': [0.0] * 9,
        'gyro_z': [0.0] * 9,
        'rot_w': [1.0, 1.0, 0.7, 1.0, 1.0, 0.8, 1.0, 1.0, 0.9],
        'rot_x': [0.0] * 9,
        'rot_y': [0.0] * 9,
        'rot_z': [0.0] * 9,
        'sensor': sensors,
        'timestamp': timestamps
    }
    df = pd.DataFrame(data)
    
    merged = merge_sensors_by_timestamp(df)
    
    # Should reduce from 9 rows to 3 rows (67% compression)
    assert len(merged) == 3, f"Expected 3 rows, got {len(merged)}"
    
    reduction = (1 - len(merged) / len(df)) * 100
    assert abs(reduction - 66.67) < 0.1, f"Expected ~66.67% reduction, got {reduction:.2f}%"
    
    print("✓ Real data reduction test passed")


def run_all_tests():
    """Run all tests."""
    print("Running merge_sensor_rows tests...\n")
    
    try:
        test_basic_merge()
        test_multiple_timestamps()
        test_missing_sensors()
        test_empty_dataframe()
        test_column_order()
        test_real_data_reduction()
        
        print("\n✅ All tests passed!")
        return True
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
