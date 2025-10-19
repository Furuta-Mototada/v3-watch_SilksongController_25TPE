#!/usr/bin/env python3
"""
Data Organization Script for Silksong Gesture Training

This script organizes collected gesture data into a structured format for training:
1. Binary classification: Walk vs Idle (locomotion states - 5 second samples)
2. Multi-class classification: Jump, Punch, Turn_Left, Turn_Right (actions - 1-2 second samples)
3. Noise/Baseline detection

These two classifiers run IN PARALLEL for simultaneous detection (e.g., walk + jump).

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


def copy_and_balance_data(input_dir, output_dir, target_samples_per_class=30):
    """
    Copy data files to organized structure with class balancing.

    For majority classes: Randomly select target_samples_per_class
    For minority classes: Copy all available samples

    Args:
        input_dir: Source directory with all CSV files
        output_dir: Target directory for organized data
        target_samples_per_class: Target number of samples per class
    """
    # Create output directory structure
    binary_dir = Path(output_dir) / "binary_classification"
    multiclass_dir = Path(output_dir) / "multiclass_classification"
    noise_dir = Path(output_dir) / "noise_detection"

    for directory in [binary_dir, multiclass_dir, noise_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    # Segment baseline noise first (creates temporary files)
    temp_baseline_dir = Path(output_dir) / "temp_baseline"
    temp_baseline_dir.mkdir(exist_ok=True)
    baseline_segments = segment_baseline_noise(input_dir, temp_baseline_dir)

    # Binary classification: walk vs idle (locomotion states)
    (binary_dir / "walk").mkdir(exist_ok=True)
    (binary_dir / "idle").mkdir(exist_ok=True)

    # Multi-class: jump, punch, turn_left, turn_right (actions only)
    for gesture in ['jump', 'punch', 'turn_left', 'turn_right']:
        (multiclass_dir / gesture).mkdir(exist_ok=True)

    # Noise detection: idle vs active
    (noise_dir / "idle").mkdir(exist_ok=True)
    (noise_dir / "active").mkdir(exist_ok=True)
    (noise_dir / "baseline").mkdir(exist_ok=True)

    # Collect files by gesture
    gesture_files = {
        'jump': [],
        'punch': [],
        'turn_left': [],
        'turn_right': [],
        'walk': [],
        'idle': [],
        'baseline': baseline_segments,  # Use segmented baseline files
        'noise': []
    }

    for filename in os.listdir(input_dir):
        if not filename.endswith('.csv'):
            continue

        # Skip the original baseline_noise file (we're using segments)
        if filename.startswith('baseline_noise'):
            continue

        # Extract gesture from filename
        # Format can be: gesture_timestamp.csv OR gesture_type_timestamp.csv
        parts = filename.split('_')

        # Handle compound names like "turn_left" and "turn_right"
        if parts[0] == 'turn' and len(parts) > 1 and parts[1] in ['left', 'right']:
            gesture = f"{parts[0]}_{parts[1]}"
        elif parts[0] in ['noise', 'locomotion', 'action']:
            gesture = 'noise'  # Group all noise-related files
        else:
            gesture = parts[0]

        if gesture in gesture_files:
            gesture_files[gesture].append(filename)

    # Print initial distribution
    print("\n📊 Initial Data Distribution:")
    for gesture, files in gesture_files.items():
        print(f"  {gesture}: {len(files)} samples")

    # Balance classes by undersampling majority
    balanced_files = {}
    for gesture, files in gesture_files.items():
        if len(files) > target_samples_per_class:
            # Undersample majority class
            import random
            random.seed(42)
            balanced_files[gesture] = random.sample(files, target_samples_per_class)
            print(f"  ⚖️  {gesture}: Undersampled {len(files)} → {target_samples_per_class}")
        else:
            balanced_files[gesture] = files
            if len(files) < target_samples_per_class:
                print(f"  ⚠️  {gesture}: Only {len(files)} samples (need more data or augmentation)")

    # Copy files to organized structure
    print("\n📁 Organizing files...")

    # Binary classification: walk vs idle
    for filename in balanced_files['walk']:
        src = Path(input_dir) / filename
        dst = binary_dir / "walk" / filename
        shutil.copy2(src, dst)

    for filename in balanced_files['idle']:
        src = Path(input_dir) / filename
        dst = binary_dir / "idle" / filename
        shutil.copy2(src, dst)

    # Multi-class classification: actions only (jump, punch, turn_left, turn_right)
    for gesture in ['jump', 'punch', 'turn_left', 'turn_right']:
        for filename in balanced_files[gesture]:
            src = Path(input_dir) / filename
            dst = multiclass_dir / gesture / filename
            shutil.copy2(src, dst)

    # Noise detection
    for filename in balanced_files['idle']:
        src = Path(input_dir) / filename
        dst = noise_dir / "idle" / filename
        shutil.copy2(src, dst)

    # Copy noise/baseline files (from temp directory)
    for filename in balanced_files.get('noise', []):
        src = Path(input_dir) / filename
        dst = noise_dir / "baseline" / filename
        shutil.copy2(src, dst)

    for filename in balanced_files.get('baseline', []):
        src = temp_baseline_dir / filename  # Baseline segments are in temp directory
        dst = noise_dir / "baseline" / filename
        shutil.copy2(src, dst)

    for gesture in ['jump', 'punch', 'turn_left', 'turn_right', 'walk']:
        for filename in balanced_files[gesture]:
            src = Path(input_dir) / filename
            dst = noise_dir / "active" / filename
            shutil.copy2(src, dst)

    # Clean up temp directory
    shutil.rmtree(temp_baseline_dir)

    # Create metadata file
    action_gestures = ['jump', 'punch', 'turn_left', 'turn_right']
    active_gestures = ['jump', 'punch', 'turn_left', 'turn_right', 'walk']

    metadata = {
        "source_directory": str(input_dir),
        "target_samples_per_class": target_samples_per_class,
        "original_distribution": {k: len(v) for k, v in gesture_files.items()},
        "balanced_distribution": {k: len(v) for k, v in balanced_files.items()},
        "total_files_organized": sum(len(v) for v in balanced_files.values()),
        "binary_classification": {
            "description": "Locomotion states (5s samples) - run in parallel with actions",
            "walk": len(balanced_files['walk']),
            "idle": len(balanced_files['idle'])
        },
        "multiclass_classification": {
            "description": "Action gestures (1-2s samples) - run in parallel with locomotion",
            **{gesture: len(balanced_files[gesture]) for gesture in action_gestures}
        },
        "noise_detection": {
            "idle": len(balanced_files['idle']),
            "baseline": len(balanced_files.get('noise', [])) + len(balanced_files.get('baseline', [])),
            "active": sum(len(balanced_files[g]) for g in active_gestures)
        }
    }

    with open(Path(output_dir) / "metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)

    print("\n✅ Data organization complete!")
    print(f"\n📊 Final Distribution:")
    print(f"  Binary Classification (Locomotion - walk vs idle):")
    print(f"    - walk: {metadata['binary_classification']['walk']}")
    print(f"    - idle: {metadata['binary_classification']['idle']}")
    print(f"  Multi-class Classification (Actions - jump/punch/turn):")
    for gesture, count in metadata['multiclass_classification'].items():
        if gesture != "description":
            print(f"    - {gesture}: {count}")
    print(f"  Noise Detection:")
    print(f"    - Idle: {metadata['noise_detection']['idle']}")
    print(f"    - Active: {metadata['noise_detection']['active']}")

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
        description='Organize gesture data for training with class balancing'
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
        '--target-samples',
        type=int,
        default=30,
        help='Target number of samples per class (default: 30)'
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

    # Organize data
    metadata = copy_and_balance_data(input_dir, output_dir, args.target_samples)

    print(f"\n📄 Metadata saved to: {output_dir / 'metadata.json'}")
    print(f"\n✨ Ready for training!")
    print(f"\n📚 Training Structure (TWO PARALLEL CLASSIFIERS):")
    print(f"  1. Binary Classifier (Locomotion: Walk vs Idle - 5s samples):")
    print(f"     - Train on: {output_dir / 'binary_classification'}/")
    print(f"  2. Multi-class Classifier (Actions: Jump/Punch/Turn_Left/Turn_Right - 1-2s samples):")
    print(f"     - Train on: {output_dir / 'multiclass_classification'}/")
    print(f"  3. Noise Detector (optional):")
    print(f"     - Train on: {output_dir / 'noise_detection'}/")
    print(f"\n💡 Note: Binary and multi-class run in parallel for simultaneous detection (e.g., walk + jump)")

    return 0


if __name__ == '__main__':
    exit(main())
