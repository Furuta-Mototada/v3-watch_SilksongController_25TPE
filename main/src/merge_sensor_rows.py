# python src/merge_sensor_rows.py --input data/button_collected --output data/merged_training --single-folder
import pandas as pd
import numpy as np
from pathlib import Path
import argparse
import time


def merge_rows(df):
    """Merges sensor data rows by timestamp."""
    if "sensor" not in df.columns:
        print("    - Already merged. Skipping.")
        return df

    # Group by the closest timestamps. Tolerance of 20ms (for a 50Hz rate).
    df["timestamp_group"] = (df["timestamp"] // 20000000) * 20000000

    merged_data = []

    for _, group in df.groupby("timestamp_group"):
        merged_row = {
            "timestamp": group["timestamp_group"].iloc[0],
            "accel_x": 0.0,
            "accel_y": 0.0,
            "accel_z": 0.0,
            "gyro_x": 0.0,
            "gyro_y": 0.0,
            "gyro_z": 0.0,
            "rot_w": 1.0,
            "rot_x": 0.0,
            "rot_y": 0.0,
            "rot_z": 0.0,
        }

        accel_row = group[group["sensor"] == "linear_acceleration"]
        if not accel_row.empty:
            merged_row["accel_x"] = accel_row["accel_x"].iloc[0]
            merged_row["accel_y"] = accel_row["accel_y"].iloc[0]
            merged_row["accel_z"] = accel_row["accel_z"].iloc[0]

        gyro_row = group[group["sensor"] == "gyroscope"]
        if not gyro_row.empty:
            merged_row["gyro_x"] = gyro_row["gyro_x"].iloc[0]
            merged_row["gyro_y"] = gyro_row["gyro_y"].iloc[0]
            merged_row["gyro_z"] = gyro_row["gyro_z"].iloc[0]

        rot_row = group[group["sensor"] == "rotation_vector"]
        if not rot_row.empty:
            merged_row["rot_w"] = rot_row["rot_w"].iloc[0]
            merged_row["rot_x"] = rot_row["rot_x"].iloc[0]
            merged_row["rot_y"] = rot_row["rot_y"].iloc[0]
            merged_row["rot_z"] = rot_row["rot_z"].iloc[0]

        merged_data.append(merged_row)

    return pd.DataFrame(merged_data)


def main(input_dir, output_dir, single_folder):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"🚀 Starting sensor merge process...")
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")

    if single_folder:
        process_folder(input_path, output_path)
    else:
        for gesture_folder in input_path.iterdir():
            if gesture_folder.is_dir():
                output_gesture_path = output_path / gesture_folder.name
                output_gesture_path.mkdir(exist_ok=True)
                process_folder(gesture_folder, output_gesture_path)

    print("\n✅ Merge process complete!")


def process_folder(input_folder, output_folder):
    files = list(input_folder.glob("*.csv"))
    total_files = len(files)
    print(f"\nProcessing folder: {input_folder.name} ({total_files} files)")

    for i, file_path in enumerate(files):
        try:
            df = pd.read_csv(file_path)
            original_rows = len(df)

            merged_df = merge_rows(df)
            final_rows = len(merged_df)

            output_file = output_folder / file_path.name
            merged_df.to_csv(output_file, index=False)

            compression = (
                (1 - final_rows / original_rows) * 100 if original_rows > 0 else 0
            )
            print(
                f"  ({i+1}/{total_files}) Merged {file_path.name}: {original_rows} -> {final_rows} rows ({compression:.1f}% reduction)"
            )

        except Exception as e:
            print(f"  ❌ Error processing {file_path.name}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge sensor data rows by timestamp.")
    parser.add_argument("--input", required=True, help="Input directory with raw CSVs.")
    parser.add_argument(
        "--output", required=True, help="Output directory for merged CSVs."
    )
    parser.add_argument(
        "--single-folder",
        action="store_true",
        help="Process all files in a single input folder.",
    )
    args = parser.parse_args()
    main(args.input, args.output, args.single_folder)
