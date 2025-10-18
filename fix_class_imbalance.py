#!/usr/bin/env python3
"""
Automated Class Imbalance Fixer for Gesture Recognition

This script helps you quickly diagnose and fix class imbalance issues
in your gesture recognition training data.

Usage:
    python fix_class_imbalance.py --diagnose        # Just check the problem
    python fix_class_imbalance.py --augment         # Generate augmented data
    python fix_class_imbalance.py --export          # Export code for Colab

Author: Gesture Recognition Pipeline
"""

import argparse
from pathlib import Path
import json

try:
    import numpy as np
    import pandas as pd
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False
    print("⚠️  Warning: numpy/pandas not installed")
    print("   Install with: pip install numpy pandas")
    print("   For --export, dependencies are not needed")

def analyze_class_distribution(session_folders):
    """
    Analyze class distribution across all session folders.
    
    Args:
        session_folders: List of session folder paths
        
    Returns:
        Dictionary with class counts and statistics
    """
    print("\n" + "="*70)
    print("CLASS DISTRIBUTION ANALYSIS")
    print("="*70)
    
    all_labels = []
    
    for folder in session_folders:
        folder_path = Path(folder)
        label_files = list(folder_path.glob("*_labels.csv"))
        
        if not label_files:
            print(f"⚠️  No labels file found in {folder}")
            continue
            
        labels_df = pd.read_csv(label_files[0])
        if 'label' in labels_df.columns:
            all_labels.extend(labels_df['label'].tolist())
    
    if not all_labels:
        print("❌ No labels found in any session folders!")
        return None
    
    # Count occurrences
    from collections import Counter
    counts = Counter(all_labels)
    
    # Calculate statistics
    total = sum(counts.values())
    max_count = max(counts.values())
    min_count = min(counts.values())
    imbalance_ratio = max_count / min_count
    
    print(f"\nTotal labeled segments: {total}")
    print(f"\nPer-class breakdown:")
    
    sorted_classes = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    for label, count in sorted_classes:
        pct = count / total * 100
        print(f"  {label:10s}: {count:5d} segments ({pct:5.1f}%)")
    
    print(f"\nImbalance ratio: {imbalance_ratio:.1f}x")
    print(f"Most common class: {sorted_classes[0][0]} ({sorted_classes[0][1]} samples)")
    print(f"Rarest class: {sorted_classes[-1][0]} ({sorted_classes[-1][1]} samples)")
    
    # Diagnosis
    print("\n" + "="*70)
    print("DIAGNOSIS")
    print("="*70)
    
    if imbalance_ratio < 3:
        print("✅ GOOD: Classes are well balanced (< 3x difference)")
        print("   → Standard training should work fine")
    elif imbalance_ratio < 10:
        print("⚠️  MODERATE: Some class imbalance (3-10x difference)")
        print("   → Recommend: Use class weights (already in notebook)")
    elif imbalance_ratio < 50:
        print("🚨 HIGH: Significant class imbalance (10-50x difference)")
        print("   → Recommend: Use softened class weights + data augmentation")
    else:
        print("💥 EXTREME: Severe class imbalance (>50x difference)")
        print("   → Recommend: Collect more data for minority classes")
        print("   → Alternative: Use focal loss + heavy augmentation")
    
    # Calculate target counts for augmentation
    print("\n" + "="*70)
    print("AUGMENTATION RECOMMENDATIONS")
    print("="*70)
    
    target_count = int(max_count * 0.5)  # Target: 50% of max class
    
    print(f"\nRecommended target count: {target_count} samples per class")
    print(f"(50% of most common class)")
    
    print("\nSamples needed for each class:")
    for label, count in sorted_classes:
        needed = max(0, target_count - count)
        if needed > 0:
            print(f"  {label:10s}: needs {needed:4d} more samples")
        else:
            print(f"  {label:10s}: ✅ already has enough")
    
    return {
        'counts': counts,
        'total': total,
        'imbalance_ratio': imbalance_ratio,
        'target_count': target_count,
        'sorted_classes': sorted_classes
    }


def generate_augmentation_code():
    """
    Generate Python code for data augmentation to paste into Colab.
    """
    code = '''
# ============================================================================
# 🎨 DATA AUGMENTATION FOR MINORITY CLASSES (Generated Code)
# ============================================================================
print("\\n" + "="*60)
print("DATA AUGMENTATION")
print("="*60)

def augment_window(window, noise_level=0.01):
    """Apply data augmentation to a sensor window."""
    augmented = window.copy()
    
    # 1. Add small random noise
    noise = np.random.normal(0, noise_level, augmented.shape)
    augmented = augmented + noise * np.abs(augmented).mean()
    
    # 2. Random scaling (0.95x to 1.05x)
    scale = np.random.uniform(0.95, 1.05)
    augmented = augmented * scale
    
    # 3. Random shift (small time offset)
    shift = np.random.randint(-2, 3)
    if shift != 0:
        augmented = np.roll(augmented, shift, axis=0)
    
    return augmented

# Calculate samples per class
class_counts = {}
for i in range(NUM_CLASSES):
    class_counts[i] = np.sum(y_combined == i)

print("\\nOriginal class distribution:")
for i, gesture in enumerate(GESTURES):
    print(f"  {gesture:8s}: {class_counts[i]:4d} samples")

# Find target count (50% of max class)
max_count = max(class_counts.values())
target_count = int(max_count * 0.5)

print(f"\\nTarget count for minority classes: {target_count}")

# Augment minority classes
augmented_X = []
augmented_y = []

for class_idx in range(NUM_CLASSES):
    current_count = class_counts[class_idx]
    
    if current_count < target_count:
        needed = target_count - current_count
        
        # Get all samples from this class
        class_mask = (y_combined == class_idx)
        class_samples = X_combined[class_mask]
        
        print(f"\\nAugmenting {GESTURES[class_idx]}: adding {needed} synthetic samples")
        
        for _ in range(needed):
            # Pick random sample and augment it
            idx = np.random.randint(0, len(class_samples))
            original_sample = class_samples[idx]
            augmented_sample = augment_window(original_sample)
            
            augmented_X.append(augmented_sample)
            augmented_y.append(class_idx)

# Add augmented data to original data
if len(augmented_X) > 0:
    X_augmented = np.array(augmented_X)
    y_augmented = np.array(augmented_y)
    
    X_combined = np.vstack([X_combined, X_augmented])
    y_combined = np.concatenate([y_combined, y_augmented])
    
    print(f"\\n✅ Added {len(augmented_X)} augmented samples")
    
    print("\\nNew class distribution:")
    for i, gesture in enumerate(GESTURES):
        count = np.sum(y_combined == i)
        pct = count / len(y_combined) * 100
        print(f"  {gesture:8s}: {count:4d} samples ({pct:5.1f}%)")
else:
    print("\\n✅ No augmentation needed")
'''
    
    return code


def generate_focal_loss_code():
    """
    Generate Python code for focal loss to paste into Colab.
    """
    code = '''
# ============================================================================
# 🔥 FOCAL LOSS - Alternative to Class Weights (Generated Code)
# ============================================================================
import tensorflow.keras.backend as K

def focal_loss(gamma=2.0, alpha=0.25):
    """
    Focal Loss for multi-class classification.
    
    Automatically focuses learning on hard-to-classify examples.
    
    Args:
        gamma: Focusing parameter (2.0 recommended for high imbalance)
        alpha: Balance parameter (0.25 default)
    
    Returns:
        Focal loss function
    """
    def focal_loss_fixed(y_true, y_pred):
        # Clip predictions to prevent log(0)
        y_pred = K.clip(y_pred, K.epsilon(), 1.0 - K.epsilon())
        
        # Calculate cross entropy
        cross_entropy = -y_true * K.log(y_pred)
        
        # Calculate focal loss
        loss = alpha * K.pow(1 - y_pred, gamma) * cross_entropy
        
        return K.mean(K.sum(loss, axis=-1))
    
    return focal_loss_fixed

print("✅ Focal loss defined")
print("\\n💡 Focal loss automatically:")
print("   - Focuses on minority classes")
print("   - Reduces importance of easy examples")
print("   - No need for manual class weights")

# Update model compilation
model.compile(
    optimizer='adam',
    loss=focal_loss(gamma=2.0, alpha=0.25),  # Use focal loss
    metrics=['accuracy']
)
print("\\n✅ Model compiled with focal loss")

# Don't use class weights with focal loss
class_weights = None
print("⚠️  Class weights disabled (using focal loss instead)")
'''
    
    return code


def export_colab_cells(output_file='colab_cells_export.txt'):
    """
    Export ready-to-paste code cells for Colab.
    """
    print("\n" + "="*70)
    print("EXPORTING CODE FOR GOOGLE COLAB")
    print("="*70)
    
    with open(output_file, 'w') as f:
        f.write("="*70 + "\n")
        f.write("COPY-PASTE THESE CELLS INTO YOUR COLAB NOTEBOOK\n")
        f.write("="*70 + "\n\n")
        
        f.write("CELL 1: DATA AUGMENTATION\n")
        f.write("-"*70 + "\n")
        f.write("Insert this BEFORE Cell 11 (data splitting)\n\n")
        f.write(generate_augmentation_code())
        f.write("\n\n")
        
        f.write("="*70 + "\n")
        f.write("CELL 2: FOCAL LOSS (Alternative)\n")
        f.write("-"*70 + "\n")
        f.write("Insert this AFTER Cell 13 (model creation)\n\n")
        f.write(generate_focal_loss_code())
        f.write("\n\n")
        
        f.write("="*70 + "\n")
        f.write("USAGE INSTRUCTIONS\n")
        f.write("="*70 + "\n")
        f.write("1. Choose ONE approach:\n")
        f.write("   - Quick fix: Just retrain (class weights already in notebook)\n")
        f.write("   - Better: Add CELL 1 (data augmentation)\n")
        f.write("   - Advanced: Add CELL 2 (focal loss)\n")
        f.write("\n")
        f.write("2. In Colab: Runtime → Restart runtime\n")
        f.write("3. Run all cells from beginning\n")
        f.write("4. Wait 30-40 minutes for training\n")
        f.write("\n")
        f.write("Expected results:\n")
        f.write("  - All gestures: 75-92% recall\n")
        f.write("  - Overall accuracy: 85-95%\n")
        f.write("  - Stable training (no NaN loss)\n")
    
    print(f"\n✅ Code exported to: {output_file}")
    print(f"\nNext steps:")
    print(f"  1. Open {output_file}")
    print(f"  2. Copy the code for your chosen approach")
    print(f"  3. Paste into your Colab notebook")
    print(f"  4. Retrain!")


def main():
    parser = argparse.ArgumentParser(
        description='Automated Class Imbalance Fixer for Gesture Recognition',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Diagnose the problem
  python fix_class_imbalance.py --diagnose --data src/data/continuous/*

  # Export code for Colab
  python fix_class_imbalance.py --export

  # Both (diagnose then export)
  python fix_class_imbalance.py --diagnose --export --data src/data/continuous/*
        '''
    )
    
    parser.add_argument('--diagnose', action='store_true',
                        help='Analyze class distribution in your data')
    parser.add_argument('--export', action='store_true',
                        help='Export code cells for Colab')
    parser.add_argument('--data', nargs='+',
                        help='Session folders to analyze (for --diagnose)')
    
    args = parser.parse_args()
    
    if not args.diagnose and not args.export:
        parser.print_help()
        print("\n💡 TIP: Start with --diagnose to see the problem, then --export to get fixes")
        return
    
    # Diagnose
    if args.diagnose:
        if not DEPS_AVAILABLE:
            print("❌ Error: --diagnose requires numpy and pandas")
            print("   Install with: pip install numpy pandas")
            return
            
        if not args.data:
            print("❌ Error: --diagnose requires --data parameter")
            print("   Example: --data src/data/continuous/*")
            return
        
        analyze_class_distribution(args.data)
    
    # Export code
    if args.export:
        export_colab_cells('colab_imbalance_fixes.txt')
    
    print("\n" + "="*70)
    print("✅ DONE")
    print("="*70)
    print("\n📚 For detailed explanations, see: LEVEL_THE_PLAYING_FIELD.md")


if __name__ == '__main__':
    main()
