# notebooks/SVM_Local_Training.py
import pandas as pd
import numpy as np
from pathlib import Path
import joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np
from scipy.fft import rfft
from scipy.stats import skew, kurtosis
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os


def extract_features_from_dataframe(df):
    """
    Extract features from a DataFrame containing sensor readings.

    Args:
        df: DataFrame with columns: accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z

    Returns:
        Dictionary of extracted features
    """
    features = {}
    for axis in ["accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z"]:
        signal = df[axis].dropna()
        if len(signal) > 0:
            features[f"{axis}_mean"] = signal.mean()
            features[f"{axis}_std"] = signal.std()
            features[f"{axis}_min"] = signal.min()
            features[f"{axis}_max"] = signal.max()
            features[f"{axis}_skew"] = skew(signal)
            features[f"{axis}_kurtosis"] = kurtosis(signal)
            if len(signal) > 2:
                fft_vals = np.abs(rfft(signal.to_numpy()))[: len(signal) // 2]
                if len(fft_vals) > 0:
                    features[f"{axis}_fft_max"] = fft_vals.max()
                    features[f"{axis}_fft_mean"] = fft_vals.mean()
    return features


def load_data(data_dir, classes):
    X, y = [], []
    data_path = Path(data_dir)
    feature_names = None

    for i, class_name in enumerate(classes):
        class_path = data_path / class_name
        if not class_path.exists():
            continue

        for file_path in class_path.glob("*.csv"):
            df = pd.read_csv(file_path)
            if len(df) < 10:
                continue

            # Use the imported function
            features = extract_features_from_dataframe(df)
            if feature_names is None:
                feature_names = sorted(list(features.keys()))

            X.append([features.get(name, 0) for name in feature_names])
            y.append(i)

    return np.array(X), np.array(y), feature_names


def train_and_evaluate(X, y, classes, model_name, models_dir, feature_names):
    print(f"\n{'='*20} Training {model_name} Classifier {'='*20}")

    if len(np.unique(y)) < 2:
        print(f"Skipping training for {model_name}: only one class present.")
        return

    # Check if we have enough samples per class for stratified split
    unique, counts = np.unique(y, return_counts=True)
    min_samples = counts.min()

    print(f"Dataset: {len(X)} samples, {len(unique)} classes")
    for cls_idx, count in zip(unique, counts):
        print(f"  - {classes[cls_idx]}: {count} samples")

    # Try multiple random states until all classes appear in test set
    max_attempts = 10
    for attempt in range(max_attempts):
        random_state = 42 + attempt

        if min_samples < 10:
            print(f"⚠️  Warning: Class with only {min_samples} samples.")
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=random_state, stratify=None
            )
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=random_state, stratify=y
            )

        # Check if all classes are in the test set
        classes_in_test = set(y_test)
        if len(classes_in_test) == len(unique):
            print(f"✓ All classes present in test set (attempt {attempt + 1})")
            break
        elif attempt == max_attempts - 1:
            print(f"⚠️  Warning: Only {len(classes_in_test)}/{len(unique)} classes in test set after {max_attempts} attempts")

    scaler = StandardScaler().fit(X_train)
    X_train_scaled, X_test_scaled = scaler.transform(X_train), scaler.transform(X_test)

    svm = SVC(kernel="rbf", C=10, gamma="auto", probability=True, random_state=42).fit(
        X_train_scaled, y_train
    )

    print("📈 Evaluating on test set...")
    y_pred = svm.predict(X_test_scaled)

    # Check which classes are actually in the test set
    classes_in_test = np.unique(y_test)
    classes_in_pred = np.unique(y_pred)
    all_classes_in_eval = np.unique(np.concatenate([y_test, y_pred]))

    print(f"Classes in test set: {[classes[i] for i in classes_in_test]}")
    print(f"Classes predicted: {[classes[i] for i in classes_in_pred]}")

    print("\nClassification Report:")
    # Get the actual classes present in evaluation
    target_names_present = [classes[i] for i in sorted(all_classes_in_eval)]
    print(classification_report(
        y_test, y_pred,
        labels=sorted(all_classes_in_eval),
        target_names=target_names_present,
        zero_division=0
    ))

    print("💾 Saving models...")
    models_path = Path(models_dir)
    models_path.mkdir(exist_ok=True)
    joblib.dump(svm, models_path / f"gesture_classifier_{model_name}.pkl")
    joblib.dump(scaler, models_path / f"feature_scaler_{model_name}.pkl")
    joblib.dump(feature_names, models_path / f"feature_names_{model_name}.pkl")

    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues", xticklabels=classes, yticklabels=classes
    )
    plt.title(f"Confusion Matrix - {model_name.capitalize()} Classifier")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.savefig(models_path / f"{model_name}_confusion_matrix.png")
    print(
        f"  Confusion matrix saved to {models_path / f'{model_name}_confusion_matrix.png'}"
    )


def main():
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    ORGANIZED_DATA_DIR = PROJECT_ROOT / "data" / "organized_training"
    MODELS_DIR = PROJECT_ROOT / "models"

    # Binary: simple walk vs idle detection
    binary_classes = ["walk", "idle"]
    X_binary, y_binary, binary_feature_names = load_data(
        ORGANIZED_DATA_DIR / "binary_classification", binary_classes
    )
    if X_binary.size > 0:
        train_and_evaluate(
            X_binary,
            y_binary,
            binary_classes,
            "binary",
            MODELS_DIR,
            binary_feature_names,
        )

    # Multiclass: all actions including noise filtering
    multi_classes = ["jump", "punch", "turn_left", "turn_right", "idle", "noise"]
    X_multi, y_multi, multi_feature_names = load_data(
        ORGANIZED_DATA_DIR / "multiclass_classification", multi_classes
    )
    if X_multi.size > 0:
        train_and_evaluate(
            X_multi,
            y_multi,
            multi_classes,
            "multiclass",
            MODELS_DIR,
            multi_feature_names,
        )


if __name__ == "__main__":
    main()
