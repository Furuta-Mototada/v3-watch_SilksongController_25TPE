#!/usr/bin/env python3
"""
Data Organization Script for Silksong Gesture Training

This script organizes collected gesture data into a structured format for training:
1. Multi-class classification: Idle, Jump, Punch, Turn_Left, Turn_Right, Walk (6 gestures)
2. Noise/Baseline detection (optional)

Usage:
    python organize_training_data.py --input ../data/button_collected --output ../data/organized_training
"""

import os
import shutil
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
from collections import Counter
import json


def analyze_data_distribution(input_dir):
    """
    Analyze the distribution of gesture classes.

    Returns:
        dict: Gesture counts
    """
    gesture_counts = {}

    for filename in os.listdir(input_dir):
        if not filename.endswith('.csv'):
            continue

        # Extract gesture from filename (format: gesture_timestamp.csv)
        gesture = filename.split('_')[0]
        gesture_counts[gesture] = gesture_counts.get(gesture, 0) + 1

    return gesture_counts


def segment_baseline_noise(input_dir, output_dir, samples_per_sec=50, segment_duration=5.0):
    """
    Segment the baseline noise CSV into multiple samples for training.

    Args:
        input_dir: Directory containing baseline_noise CSV
        output_dir: Directory to save segmented baseline samples
        samples_per_sec: Sensor data rate (default 50Hz)
        segment_duration: Duration of each segment in seconds (default 5.0s)

    Returns:
        list: Filenames of segmented baseline samples
    """
    baseline_files = [f for f in os.listdir(input_dir) if f.startswith('baseline_noise') and f.endswith('.csv')]

    if not baseline_files:
        print("⚠️  No baseline_noise file found")
        return []

    baseline_file = Path(input_dir) / baseline_files[0]
    print(f"\n📊 Segmenting baseline noise: {baseline_file.name}")

    # Read the baseline CSV
    df = pd.read_csv(baseline_file)
    total_samples = len(df)
    segment_size = int(segment_duration * samples_per_sec)

    print(f"   Total samples: {total_samples}")
    print(f"   Segment size: {segment_size} samples ({segment_duration}s at {samples_per_sec}Hz)")

    # Create segments
    segmented_files = []
    segment_count = 0

    for i in range(0, total_samples - segment_size + 1, segment_size):
        segment = df.iloc[i:i + segment_size]

        if len(segment) == segment_size:
            segment_count += 1
            filename = f"baseline_segment_{segment_count:03d}.csv"
            filepath = Path(output_dir) / filename
            segment.to_csv(filepath, index=False)
            segmented_files.append(filename)

    print(f"   ✅ Created {segment_count} baseline segments")

    return segmented_files


def copy_and_balance_data(input_dir, output_dir, target_samples_per_class=None):
    """
    Copy data files to organized structure WITHOUT undersampling.
    
    User requirement: Keep all data since it's already balanced (~37 ± 5 samples per class).

    Args:
        input_dir: Source directory with all CSV files
        output_dir: Target directory for organized data
        target_samples_per_class: DEPRECATED - kept for backward compatibility but ignored
    """
    # Create output directory structure
    multiclass_dir = Path(output_dir) / "multiclass"
    noise_dir = Path(output_dir) / "noise"

    for directory in [multiclass_dir, noise_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    # Multi-class: 6 gestures - idle, jump, punch, turn_left, turn_right, walk
    for gesture in ['idle', 'jump', 'punch', 'turn_left', 'turn_right', 'walk']:
        (multiclass_dir / gesture).mkdir(exist_ok=True)

    # Noise detection: baseline only (user's clean golden quality data)
    (noise_dir / "baseline").mkdir(exist_ok=True)

    # Collect files by gesture - NO undersampling, use all data
    gesture_files = {
        'idle': [],
        'jump': [],
        'punch': [],
        'turn_left': [],
        'turn_right': [],
        'walk': [],
        'noise': []
    }

    for filename in os.listdir(input_dir):
        if not filename.endswith('.csv'):
            continue

        # Extract gesture from filename
        # Format can be: gesture_timestamp.csv OR gesture_type_timestamp.csv
        parts = filename.split('_')

        # Handle compound names like "turn_left" and "turn_right"
        if parts[0] == 'turn' and len(parts) > 1 and parts[1] in ['left', 'right']:
            gesture = f"{parts[0]}_{parts[1]}"
        elif parts[0] == 'noise' or parts[0] == 'baseline':
            gesture = 'noise'  # Baseline noise files
        else:
            gesture = parts[0]

        if gesture in gesture_files:
            gesture_files[gesture].append(filename)

    # Print distribution - NO undersampling
    print("\n📊 Data Distribution (using ALL data):")
    for gesture, files in gesture_files.items():
        print(f"  {gesture}: {len(files)} samples")

    # Copy files to organized structure (NO undersampling - use ALL data)
    print("\n📁 Organizing files...")

    # Multi-class classification - ALL 6 gestures
    for gesture in ['idle', 'jump', 'punch', 'turn_left', 'turn_right', 'walk']:
        for filename in gesture_files[gesture]:
            src = Path(input_dir) / filename
            dst = multiclass_dir / gesture / filename
            shutil.copy2(src, dst)

    # Noise detection - baseline/noise files only
    for filename in gesture_files.get('noise', []):
        src = Path(input_dir) / filename
        dst = noise_dir / "baseline" / filename
        shutil.copy2(src, dst)

    # Create metadata file
    all_gestures = ['idle', 'jump', 'punch', 'turn_left', 'turn_right', 'walk']

    metadata = {
        "source_directory": str(input_dir),
        "note": "All data used - NO undersampling (data is already balanced)",
        "original_distribution": {k: len(v) for k, v in gesture_files.items()},
        "total_files_organized": sum(len(v) for v in gesture_files.values()),
        "multiclass_classification": {
            gesture: len(gesture_files[gesture]) for gesture in all_gestures
        },
        "noise_detection": {
            "baseline": len(gesture_files.get('noise', []))
        }
    }

    with open(Path(output_dir) / "metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)

    print("\n✅ Data organization complete!")
    print(f"\n📊 Final Distribution:")
    print(f"  Multi-class Classification (6 gestures):")
    for gesture in all_gestures:
        print(f"    - {gesture}: {metadata['multiclass_classification'][gesture]}")
    print(f"  Noise Detection:")
    print(f"    - baseline: {metadata['noise_detection']['baseline']}")

    return metadata


def verify_csv_format(input_dir):
    """
    Verify that CSV files have the correct format.

    Expected columns: accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z,
                     rot_w, rot_x, rot_y, rot_z, sensor, timestamp
    """
    print("\n🔍 Verifying CSV format...")

    expected_columns = {'accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z',
                       'rot_w', 'rot_x', 'rot_y', 'rot_z', 'sensor', 'timestamp'}

    issues = []
    sample_count = 0

    for filename in os.listdir(input_dir):
        if not filename.endswith('.csv'):
            continue

        try:
            df = pd.read_csv(Path(input_dir) / filename)
            columns = set(df.columns)

            if not expected_columns.issubset(columns):
                missing = expected_columns - columns
                issues.append(f"  ❌ {filename}: Missing columns {missing}")

            sample_count += 1
            if sample_count >= 5:  # Check first 5 files
                break

        except Exception as e:
            issues.append(f"  ❌ {filename}: Error reading file - {e}")

    if issues:
        print("⚠️  Found issues in some files:")
        for issue in issues:
            print(issue)
    else:
        print("✅ CSV format verified - all files have correct columns")


def main():
    parser = argparse.ArgumentParser(
        description='Organize gesture data for simplified multi-class training (NO undersampling)'
    )
    parser.add_argument(
        '--input',
        default='../data/button_collected',
        help='Input directory with CSV files'
    )
    parser.add_argument(
        '--output',
        default='../data/organized_training',
        help='Output directory for organized data'
    )
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only verify CSV format without organizing'
    )

    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)

    if not input_dir.exists():
        print(f"❌ Error: Input directory not found: {input_dir}")
        return 1

    # Verify CSV format
    verify_csv_format(input_dir)

    if args.verify_only:
        return 0

    # Analyze distribution
    print(f"\n📂 Input directory: {input_dir}")
    print(f"📂 Output directory: {output_dir}")

    # Organize data - NO undersampling
    metadata = copy_and_balance_data(input_dir, output_dir)

    print(f"\n📄 Metadata saved to: {output_dir / 'metadata.json'}")
    print(f"\n✨ Ready for training!")
    print(f"\n📚 Training Structure:")
    print(f"  1. Multi-class Classifier (6 gestures: idle, jump, punch, turn_left, turn_right, walk):")
    print(f"     - Train on: {output_dir / 'multiclass'}/")
    print(f"  2. Noise Detector (optional - baseline only):")
    print(f"     - Train on: {output_dir / 'noise'}/")

    return 0


if __name__ == '__main__':
    exit(main())
