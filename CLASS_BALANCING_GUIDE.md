# 🎯 Class Balancing Guide - Fixed!

## The Problem

Your model was stuck predicting only "walk" because:
- **Walk class:** 78% of data (1173 samples)
- **Jump/Punch/Turn:** 0-5% each (47-125 samples)
- **Result:** Model learned to always predict "walk" for 78% accuracy

```
Before Balancing:
  jump:  0% accuracy (predicted 0 times)
  punch: 0% accuracy (predicted 0 times)
  turn:  0% accuracy (predicted 0 times)
  walk:  99% accuracy (predicted everything as walk)
  noise: 5% accuracy
```

## The Solution (Triple Strategy)

### 1️⃣ Undersample Majority Class
```python
# Reduce "walk" to 3x the largest minority class
target_walk_size = max(jump, punch, turn, noise) * 3
walk_downsampled = resample(walk_data, n_samples=target_walk_size)
```

**Why:** Prevents "walk" from dominating the learning signal.

### 2️⃣ Augment Minority Classes
```python
# Create 3x variations of each minority sample
for minority_sample in [jump, punch, turn, noise]:
    - Original sample
    - Add Gaussian noise (σ=0.02)
    - Random scaling (90-110%)
    - Time shift (±3 samples)
```

**Why:** Gives the model more examples to learn rare gesture patterns.

### 3️⃣ Moderate Class Weights
```python
# Calculate balanced weights, then soften with sqrt
class_weights = compute_class_weight('balanced', y_train)
class_weights = np.sqrt(class_weights)  # Softening prevents instability
```

**Why:** Tells the model "minority classes are more important" without destabilizing training.

## Expected Results

After applying all three strategies:

```
After Balancing:
  jump:   70-85% accuracy ✅
  punch:  70-85% accuracy ✅
  turn:   70-85% accuracy ✅
  walk:   85-95% accuracy ✅
  noise:  60-75% accuracy ✅

  Overall: 80-90% balanced accuracy
```

## How to Use

### In the Updated Notebook:

1. **Run cells 1-12** (data loading and splitting)
   - This creates the original imbalanced dataset

2. **Run NEW cells 13-16** (class balancing - Section 4.5)
   - Cell 13: Markdown header
   - Cell 14: Undersample walk class
   - Cell 15: Augment minority classes
   - Cell 16: Calculate moderate class weights

3. **Run cell 21** (training - UPDATED)
   - Now uses `X_train_augmented` and `class_weights_final`
   - Training will take the same time but with balanced learning

4. **Run NEW cell 23** (verification - Section 6.5)
   - Checks if model is predicting all classes
   - Should show diverse predictions, not just "walk"

5. **Run cells 25-27** (evaluation)
   - Classification report should show >70% for all classes!

## Troubleshooting

### Issue: Still getting 0% on minority classes

**Solution:** Data augmentation might not be enough. Try:
```python
# In cell 15, increase augmentation factor
# Change from 3x to 5x
for sample in class_data:
    # Add 4 variations instead of 2
    aug1 = augment_window(sample, 'noise')
    aug2 = augment_window(sample, 'scale')
    aug3 = augment_window(sample, 'time_shift')
    aug4 = augment_window(sample, 'noise')  # Different noise
```

### Issue: Training loss is NaN

**Solution:** Weights might still be too extreme. In cell 16, add more softening:
```python
# Use cube root instead of square root for gentler softening
class_weights_array = np.power(class_weights_array, 1/3)
```

### Issue: Overall accuracy dropped

**Solution:** This is normal initially! The model is learning harder tasks.
- Before: 78% by always predicting "walk" (useless)
- After: 75% but ALL classes work (useful!)

Give it more epochs or adjust augmentation.

## Technical Details

### Why Undersampling?

Reducing the majority class prevents gradient updates from being dominated by "walk" examples. With 78% walk data, 78% of gradient updates were about walking, drowning out other gestures.

### Why Augmentation?

The model needs to see patterns multiple times to learn. With only 47 jump examples, the model doesn't have enough exposure. Augmentation creates realistic variations without collecting more data.

### Why Softened Weights?

Extreme class weights (like 100x) can cause:
- Gradient explosion → NaN loss
- Overfitting to minority classes
- Training instability

Square root softening (e.g., 100x → 10x) maintains balance while keeping training stable.

## References

- Original issue: Model predicting only majority class
- Solution inspired by: sklearn `compute_class_weight`, imbalanced-learn library
- Augmentation techniques: Time series data augmentation best practices

## Next Steps

After successful training with balanced classes:

1. **Collect more minority class data** (ideal solution)
   - Target: 200-300 samples per gesture
   - Use the hybrid collection protocol

2. **Fine-tune augmentation parameters**
   - Experiment with noise levels
   - Try rotation/permutation for gestures

3. **Deploy and monitor**
   - Real-world performance might differ
   - Log misclassifications to improve dataset

---

**Last Updated:** October 18, 2025
**Status:** ✅ Implemented in `watson_Colab_CNN_LSTM_Training.ipynb`
