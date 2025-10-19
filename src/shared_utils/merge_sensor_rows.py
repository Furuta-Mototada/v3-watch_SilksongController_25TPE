#!/usr/bin/env python3
"""
Merge Sensor Rows by Timestamp

Problem: Raw CSV files have separate rows for each sensor type with zeros in other columns.
Solution: Merge all sensors at the same timestamp into a single row.

Example Input (separate rows):
    0.0,0.0,0.0,0.0,0.0,0.0,0.928,-0.118,-0.093,0.340,rotation_vector,244452317059263
    -6.486,-0.027,-5.809,0.0,0.0,0.0,1.0,0.0,0.0,0.0,linear_acceleration,244452356953341
    0.0,0.0,0.0,-2.596,0.664,-3.595,1.0,0.0,0.0,0.0,gyroscope,244452356953341

Example Output (merged):
    -6.486,-0.027,-5.809,-2.596,0.664,-3.595,0.945,-0.165,-0.106,0.262,244452356953341

Usage:
    python src/shared_utils/merge_sensor_rows.py --input data/organized_training --output data/merged_training
    python src/shared_utils/merge_sensor_rows.py --input data/organized_training/multiclass_classification/punch --output data/merged_punch --single-folder
"""

import pandas as pd
import numpy as np
from pathlib import Path
import argparse
import sys
import json
import shutil

def merge_sensors_by_timestamp(df):
    """
    Merge sensor rows by timestamp into single rows.

    Input DataFrame has columns:
        accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z,
        rot_w, rot_x, rot_y, rot_z, sensor, timestamp

    Output DataFrame has columns:
        accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z,
        rot_w, rot_x, rot_y, rot_z, timestamp

    Strategy:
    1. Group by timestamp
    2. For each timestamp, take non-zero values from each sensor
    3. Combine into single row
    """
    if df.empty:
        return df

    # Group by timestamp
    grouped = df.groupby('timestamp')

    merged_rows = []

    for timestamp, group in grouped:
        # Initialize merged row with zeros
        merged = {
            'accel_x': 0.0, 'accel_y': 0.0, 'accel_z': 0.0,
            'gyro_x': 0.0, 'gyro_y': 0.0, 'gyro_z': 0.0,
            'rot_w': 1.0, 'rot_x': 0.0, 'rot_y': 0.0, 'rot_z': 0.0,  # rot_w defaults to 1.0 (identity quaternion)
            'timestamp': timestamp
        }

        # Extract data from each sensor type
        for _, row in group.iterrows():
            sensor_type = row['sensor']

            if sensor_type == 'linear_acceleration':
                merged['accel_x'] = row['accel_x']
                merged['accel_y'] = row['accel_y']
                merged['accel_z'] = row['accel_z']

            elif sensor_type == 'gyroscope':
                merged['gyro_x'] = row['gyro_x']
                merged['gyro_y'] = row['gyro_y']
                merged['gyro_z'] = row['gyro_z']

            elif sensor_type == 'rotation_vector':
                merged['rot_w'] = row['rot_w']
                merged['rot_x'] = row['rot_x']
                merged['rot_y'] = row['rot_y']
                merged['rot_z'] = row['rot_z']

        merged_rows.append(merged)

    # Create DataFrame with consistent column order
    merged_df = pd.DataFrame(merged_rows, columns=[
        'accel_x', 'accel_y', 'accel_z',
        'gyro_x', 'gyro_y', 'gyro_z',
        'rot_w', 'rot_x', 'rot_y', 'rot_z',
        'timestamp'
    ])

    return merged_df


def process_csv_file(input_path, output_path):
    """Process a single CSV file: merge sensors and save."""
    try:
        # Read CSV
        df = pd.read_csv(input_path)

        if df.empty:
            print(f"⚠️  Skipping empty file: {input_path.name}")
            return False

        # Check required columns
        required_cols = ['accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z',
                        'rot_w', 'rot_x', 'rot_y', 'rot_z', 'sensor', 'timestamp']

        if not all(col in df.columns for col in required_cols):
            print(f"⚠️  Missing columns in {input_path.name}")
            return False

        # Merge sensors by timestamp
        merged_df = merge_sensors_by_timestamp(df)

        if merged_df.empty:
            print(f"⚠️  Merged result empty for {input_path.name}")
            return False

        # Save merged data
        output_path.parent.mkdir(parents=True, exist_ok=True)
        merged_df.to_csv(output_path, index=False)

        original_rows = len(df)
        merged_rows = len(merged_df)
        compression = (1 - merged_rows / original_rows) * 100

        print(f"✅ {input_path.name}: {original_rows} → {merged_rows} rows ({compression:.1f}% compression)")
        return True

    except Exception as e:
        print(f"❌ Error processing {input_path.name}: {e}")
        return False


def process_directory_tree(input_dir, output_dir):
    """
    Process entire directory tree (binary_classification and multiclass_classification).
    Maintains folder structure.
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if not input_path.exists():
        print(f"❌ Input directory not found: {input_path}")
        return

    # Find all CSV files recursively
    csv_files = list(input_path.rglob("*.csv"))

    if not csv_files:
        print(f"❌ No CSV files found in {input_path}")
        return

    print(f"\n📂 Processing {len(csv_files)} CSV files from {input_path}")
    print(f"📂 Output directory: {output_path}\n")

    success_count = 0

    for csv_file in csv_files:
        # Maintain relative path structure
        relative_path = csv_file.relative_to(input_path)
        output_csv = output_path / relative_path

        if process_csv_file(csv_file, output_csv):
            success_count += 1

    print(f"\n✅ Successfully processed {success_count}/{len(csv_files)} files")

    # Copy metadata.json if it exists
    metadata_src = input_path / "metadata.json"
    if metadata_src.exists():
        metadata_dst = output_path / "metadata.json"
        shutil.copy2(metadata_src, metadata_dst)
        print(f"📄 Copied metadata.json")
    else:
        print(f"\n⚠️  No metadata.json found in source directory")


def process_single_folder(input_dir, output_dir):
    """
    Process all CSV files in a single folder (flat structure).
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if not input_path.exists():
        print(f"❌ Input directory not found: {input_path}")
        return

    # Find CSV files in this directory only (not recursive)
    csv_files = list(input_path.glob("*.csv"))

    if not csv_files:
        print(f"❌ No CSV files found in {input_path}")
        return

    print(f"\n📂 Processing {len(csv_files)} CSV files from {input_path}")
    print(f"📂 Output directory: {output_path}\n")

    output_path.mkdir(parents=True, exist_ok=True)
    success_count = 0

    for csv_file in csv_files:
        output_csv = output_path / csv_file.name

        if process_csv_file(csv_file, output_csv):
            success_count += 1

    print(f"\n✅ Successfully processed {success_count}/{len(csv_files)} files")


def main():
    parser = argparse.ArgumentParser(
        description="Merge sensor rows by timestamp to eliminate zero-inflated data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process entire organized training directory
  python src/shared_utils/merge_sensor_rows.py --input data/organized_training --output data/merged_training

  # Process single gesture folder
  python src/shared_utils/merge_sensor_rows.py --input data/organized_training/multiclass_classification/punch --output data/merged_punch --single-folder

  # Process button collected data
  python src/shared_utils/merge_sensor_rows.py --input data/button_collected --output data/button_merged --single-folder
        """
    )

    parser.add_argument('--input', '-i', required=True,
                       help='Input directory containing CSV files')
    parser.add_argument('--output', '-o', required=True,
                       help='Output directory for merged CSV files')
    parser.add_argument('--single-folder', '-s', action='store_true',
                       help='Process single folder (flat) instead of directory tree')

    args = parser.parse_args()

    if args.single_folder:
        process_single_folder(args.input, args.output)
    else:
        process_directory_tree(args.input, args.output)


if __name__ == '__main__':
    main()
