#!/usr/bin/env python3
"""
Data Augmentation for IMU Sensor Data

Techniques to augment minority classes and improve model generalization:
1. Gaussian noise injection
2. Time warping
3. Magnitude scaling
4. Time shifting

Usage:
    from data_augmentation import augment_gesture_data
    
    augmented_data = augment_gesture_data(
        original_df, 
        n_augmentations=2,
        methods=['noise', 'scale', 'warp']
    )
"""

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from pathlib import Path


def add_gaussian_noise(df, noise_level=0.05):
    """
    Add Gaussian noise to sensor readings.
    
    Args:
        df: DataFrame with sensor data
        noise_level: Standard deviation of noise (default: 5% of signal)
    
    Returns:
        DataFrame with noise added
    """
    augmented_df = df.copy()
    
    sensor_cols = ['accel_x', 'accel_y', 'accel_z', 
                   'gyro_x', 'gyro_y', 'gyro_z',
                   'rot_w', 'rot_x', 'rot_y', 'rot_z']
    
    for col in sensor_cols:
        if col in augmented_df.columns:
            signal = augmented_df[col].values
            noise = np.random.normal(0, noise_level * np.std(signal), len(signal))
            augmented_df[col] = signal + noise
    
    return augmented_df


def time_warp(df, warp_factor=0.1):
    """
    Apply time warping to stretch/compress gesture in time.
    
    Args:
        df: DataFrame with sensor data
        warp_factor: Amount of warping (0.1 = ±10% time change)
    
    Returns:
        DataFrame with time-warped data
    """
    augmented_df = df.copy()
    
    # Generate warping function
    n_samples = len(df)
    warp = 1.0 + np.random.uniform(-warp_factor, warp_factor)
    
    # New time indices
    old_indices = np.arange(n_samples)
    new_length = int(n_samples * warp)
    new_indices = np.linspace(0, n_samples - 1, new_length)
    
    sensor_cols = ['accel_x', 'accel_y', 'accel_z', 
                   'gyro_x', 'gyro_y', 'gyro_z',
                   'rot_w', 'rot_x', 'rot_y', 'rot_z']
    
    # Interpolate each sensor channel
    for col in sensor_cols:
        if col in augmented_df.columns:
            interpolator = interp1d(old_indices, augmented_df[col].values, 
                                   kind='cubic', fill_value='extrapolate')
            augmented_df[col] = interpolator(new_indices)
    
    # Adjust timestamps
    if 'timestamp' in augmented_df.columns:
        time_interpolator = interp1d(old_indices, augmented_df['timestamp'].values,
                                     kind='linear', fill_value='extrapolate')
        augmented_df['timestamp'] = time_interpolator(new_indices).astype(int)
    
    return augmented_df


def magnitude_scale(df, scale_range=(0.8, 1.2)):
    """
    Scale magnitude of sensor readings.
    
    Args:
        df: DataFrame with sensor data
        scale_range: Min and max scaling factors
    
    Returns:
        DataFrame with scaled magnitudes
    """
    augmented_df = df.copy()
    
    scale = np.random.uniform(*scale_range)
    
    sensor_cols = ['accel_x', 'accel_y', 'accel_z', 
                   'gyro_x', 'gyro_y', 'gyro_z']
    
    for col in sensor_cols:
        if col in augmented_df.columns:
            augmented_df[col] = augmented_df[col] * scale
    
    return augmented_df


def time_shift(df, shift_range=0.1):
    """
    Shift gesture in time (circular shift).
    
    Args:
        df: DataFrame with sensor data
        shift_range: Fraction of data to shift (0.1 = ±10%)
    
    Returns:
        DataFrame with time-shifted data
    """
    augmented_df = df.copy()
    
    n_samples = len(df)
    shift = int(np.random.uniform(-shift_range, shift_range) * n_samples)
    
    sensor_cols = ['accel_x', 'accel_y', 'accel_z', 
                   'gyro_x', 'gyro_y', 'gyro_z',
                   'rot_w', 'rot_x', 'rot_y', 'rot_z']
    
    for col in sensor_cols:
        if col in augmented_df.columns:
            augmented_df[col] = np.roll(augmented_df[col].values, shift)
    
    return augmented_df


def augment_gesture_data(df, n_augmentations=1, methods=None):
    """
    Generate augmented versions of a gesture sample.
    
    Args:
        df: Original DataFrame with sensor data
        n_augmentations: Number of augmented samples to generate
        methods: List of augmentation methods to use
                ['noise', 'warp', 'scale', 'shift']
                If None, uses all methods
    
    Returns:
        List of augmented DataFrames
    """
    if methods is None:
        methods = ['noise', 'scale', 'warp', 'shift']
    
    augmentation_funcs = {
        'noise': lambda df: add_gaussian_noise(df, noise_level=0.05),
        'warp': lambda df: time_warp(df, warp_factor=0.1),
        'scale': lambda df: magnitude_scale(df, scale_range=(0.85, 1.15)),
        'shift': lambda df: time_shift(df, shift_range=0.1)
    }
    
    augmented_samples = []
    
    for i in range(n_augmentations):
        # Randomly select augmentation method
        method = np.random.choice(methods)
        augmented_df = augmentation_funcs[method](df)
        augmented_samples.append(augmented_df)
    
    return augmented_samples


def augment_minority_classes(data_dir, target_samples=35, output_dir=None):
    """
    Augment minority classes to reach target sample count.
    
    Args:
        data_dir: Directory with organized gesture folders
        target_samples: Target number of samples per class
        output_dir: Output directory (default: data_dir + '_augmented')
    
    Returns:
        Dict with augmentation statistics
    """
    data_path = Path(data_dir)
    
    if output_dir is None:
        output_dir = Path(str(data_dir) + '_augmented')
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    stats = {}
    
    # Process each gesture folder
    for gesture_folder in data_path.iterdir():
        if not gesture_folder.is_dir():
            continue
        
        gesture = gesture_folder.name
        csv_files = list(gesture_folder.glob("*.csv"))
        n_original = len(csv_files)
        
        print(f"\n📁 Processing {gesture}:")
        print(f"   Original samples: {n_original}")
        
        # Create output folder
        output_gesture_dir = output_dir / gesture
        output_gesture_dir.mkdir(exist_ok=True)
        
        # Copy original files
        for csv_file in csv_files:
            df = pd.read_csv(csv_file)
            output_file = output_gesture_dir / csv_file.name
            df.to_csv(output_file, index=False)
        
        # Augment if needed
        if n_original < target_samples:
            n_needed = target_samples - n_original
            n_per_original = int(np.ceil(n_needed / n_original))
            
            print(f"   Augmenting: {n_needed} samples needed ({n_per_original} per original)")
            
            augmented_count = 0
            for csv_file in csv_files:
                df = pd.read_csv(csv_file)
                
                # Generate augmented samples
                augmented_samples = augment_gesture_data(
                    df, 
                    n_augmentations=n_per_original,
                    methods=['noise', 'scale', 'warp']
                )
                
                # Save augmented samples
                for i, aug_df in enumerate(augmented_samples):
                    if augmented_count >= n_needed:
                        break
                    
                    # Generate filename
                    base_name = csv_file.stem
                    aug_filename = f"{base_name}_aug{i+1}.csv"
                    aug_path = output_gesture_dir / aug_filename
                    aug_df.to_csv(aug_path, index=False)
                    augmented_count += 1
                
                if augmented_count >= n_needed:
                    break
            
            print(f"   ✅ Created {augmented_count} augmented samples")
            stats[gesture] = {
                'original': n_original,
                'augmented': augmented_count,
                'total': n_original + augmented_count
            }
        else:
            print(f"   ✅ Already has enough samples")
            stats[gesture] = {
                'original': n_original,
                'augmented': 0,
                'total': n_original
            }
    
    print(f"\n💾 Augmented data saved to: {output_dir}")
    return stats


def main():
    """Command-line interface for data augmentation."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Augment minority classes in gesture data'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Input directory with gesture folders (e.g., data/organized_training/multiclass_classification)'
    )
    parser.add_argument(
        '--output',
        help='Output directory for augmented data'
    )
    parser.add_argument(
        '--target-samples',
        type=int,
        default=35,
        help='Target number of samples per class (default: 35)'
    )
    
    args = parser.parse_args()
    
    print("🔄 Data Augmentation Tool")
    print("=" * 60)
    
    stats = augment_minority_classes(
        args.input,
        target_samples=args.target_samples,
        output_dir=args.output
    )
    
    print("\n📊 Augmentation Summary:")
    print("=" * 60)
    for gesture, counts in stats.items():
        print(f"{gesture}:")
        print(f"  Original: {counts['original']}")
        print(f"  Augmented: {counts['augmented']}")
        print(f"  Total: {counts['total']}")
    
    print("\n✨ Done!")


if __name__ == '__main__':
    main()
