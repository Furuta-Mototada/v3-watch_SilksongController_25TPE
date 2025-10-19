# python3.11 src/organize_training_data.py --input data/merged_training --output data/organized_training --target-samples 100

import os
import shutil
from pathlib import Path
import argparse
import pandas as pd
import random
import json


def get_gesture_name(filename):
    """Correctly identifies gesture names, including compound ones like 'turn_left'."""
    if filename.startswith("turn_left"):
        return "turn_left"
    if filename.startswith("turn_right"):
        return "turn_right"
    # Handle noise with specific classifiers (noise_locomotion, noise_action)
    if filename.startswith("noise_locomotion"):
        return "noise"
    if filename.startswith("noise_action"):
        return "noise"
    if filename.startswith("noise"):
        return "noise"
    return filename.split("_")[0]


def truncate_and_copy(src_path, dst_path, duration_sec=1.5, sample_rate=50):
    """Reads a CSV, truncates it to a central window, and saves it."""
    try:
        df = pd.read_csv(src_path)
        target_samples = int(duration_sec * sample_rate)

        if len(df) > target_samples:
            center_index = len(df) // 2
            start_index = max(0, center_index - (target_samples // 2))
            end_index = start_index + target_samples

            truncated_df = df.iloc[start_index:end_index]
            truncated_df.to_csv(dst_path, index=False)
        else:
            shutil.copy(src_path, dst_path)
    except Exception as e:
        print(f"  - Error truncating {src_path.name}: {e}")


def organize_files(input_dir, output_dir, target_samples):
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if output_path.exists():
        shutil.rmtree(output_path)
    print(f"Creating clean output directory: {output_path}")

    binary_path = output_path / "binary_classification"
    multi_path = output_path / "multiclass_classification"

    # Binary: simple walk vs idle (no noise - multiclass handles that)
    locomotion_classes = ["walk", "idle"]
    # Multiclass: all actions including noise filtering
    action_classes = ["jump", "punch", "turn_left", "turn_right", "idle", "noise"]

    for gesture in locomotion_classes:
        (binary_path / gesture).mkdir(parents=True, exist_ok=True)
    for gesture in action_classes:
        (multi_path / gesture).mkdir(parents=True, exist_ok=True)

    files = list(input_path.glob("*.csv"))
    gesture_files = {}
    for f in files:
        gesture = get_gesture_name(f.name)
        if gesture not in gesture_files:
            gesture_files[gesture] = []
        gesture_files[gesture].append(f.name)  # Store just the filename string

    print("\n📊 Initial Data Distribution:")
    for gesture, file_list in sorted(gesture_files.items()):
        print(f"  {gesture}: {len(file_list)} samples")

    print("\n⚖️ Balancing and organizing files...")

    all_classes = set(locomotion_classes + action_classes)
    balanced_files = {}
    for gesture in all_classes:
        if gesture in gesture_files:
            file_list = gesture_files[gesture]
            if len(file_list) > target_samples:
                print(
                    f"  - Undersampling '{gesture}': {len(file_list)} -> {target_samples}"
                )
                balanced_files[gesture] = random.sample(file_list, target_samples)
            else:
                balanced_files[gesture] = file_list

    # Copy files, applying special logic for idle and noise
    for gesture, file_list in balanced_files.items():
        for f_name in file_list:
            # --- THIS IS THE CRITICAL FIX ---
            # Construct the source path correctly from the base input_path
            src = input_path / f_name

            if not src.exists():
                print(f"  - ❌ ERROR: Source file not found: {src}")
                continue

            # Noise files only go to multiclass (for action filtering)
            # Binary classifier doesn't need noise class
            if gesture == "noise":
                shutil.copy(src, multi_path / gesture / f_name)
                continue

            # Copy to binary (locomotion) folder
            if gesture in locomotion_classes:
                shutil.copy(src, binary_path / gesture / f_name)

            # Copy to multi-class (action) folder
            if gesture in action_classes:
                dst = multi_path / gesture / f_name
                if gesture == "idle":
                    print(
                        f"  - Truncating '{f_name}' for action classifier (5s -> 1.5s)"
                    )
                    truncate_and_copy(src, dst, duration_sec=1.5)
                else:
                    shutil.copy(src, dst)

    final_counts = {gest: len(files) for gest, files in balanced_files.items()}

    print("\n✅ Data organization complete!")
    print("\n📊 Final Organized Distribution:")
    print("  Binary Classification (Locomotion):")
    for gesture in locomotion_classes:
        print(f"    - {gesture}: {final_counts.get(gesture, 0)} samples")
    print("  Multi-class Classification (Actions):")
    for gesture in action_classes:
        print(f"    - {gesture}: {final_counts.get(gesture, 0)} samples")

    with open(output_path / "metadata.json", "w") as f:
        json.dump(final_counts, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Organize merged data for parallel training."
    )
    parser.add_argument(
        "--input", default="data/merged_training", help="Input directory."
    )
    parser.add_argument(
        "--output", default="data/organized_training", help="Output directory."
    )
    parser.add_argument(
        "--target-samples", type=int, default=30, help="Target samples per class."
    )
    args = parser.parse_args()
    organize_files(args.input, args.output, args.target_samples)
