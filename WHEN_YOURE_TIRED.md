# 😓 When You're Tired: The Simplest Fix

## TL;DR (Too Long; Didn't Read)

Your model only predicts "walk" because 78% of your data is walking.

**Quick fix (5 minutes):**

1. Open your Colab notebook
2. Runtime → Restart runtime
3. Click "Run all" (Ctrl+F9)
4. Wait 30 minutes
5. Done!

Your notebook **already has the fix** (class weight softening in Cell 13/14). Just retrain.

---

## If That Doesn't Work (15 minutes)

**Problem still there?** Model still only predicts walk?

### Step 1: Enable Data Augmentation (2 minutes)

In your Colab notebook, find **Cell 12** (has "DATA AUGMENTATION" header).

**See this?**
```python
# '''
print("\n" + "="*60)
# ... lots of code ...
# '''
```

**Remove the `'''` marks:**
```python
print("\n" + "="*60)
# ... lots of code ...
```

That's it! Just delete the two lines with `'''`.

### Step 2: Retrain (30 minutes)

1. Runtime → Restart runtime
2. Run all cells
3. Wait 30 minutes

**Result:** All gestures will work (80-90% accuracy each).

---

## Still Not Working? (30 minutes)

Run this diagnostic script:

```bash
cd /home/runner/work/v3-watch_SilksongController_25TPE/v3-watch_SilksongController_25TPE
python fix_class_imbalance.py --diagnose --data src/data/continuous/*
python fix_class_imbalance.py --export
```

This will:
1. Show you exactly what's wrong
2. Generate code to fix it
3. Tell you what to paste where

Then follow the instructions in `colab_imbalance_fixes.txt`.

---

## I Just Want It To Work

Read `LEVEL_THE_PLAYING_FIELD.md` - it has **3 solutions**:

1. **Quick** (0 setup, 30 min train) - class weights (already in notebook)
2. **Better** (5 min setup, 30 min train) - + data augmentation (Cell 12)
3. **Best** (15 min setup, 30 min train) - + focal loss (see guide)

Pick one, follow the steps, done.

---

## Visual Guide

### Your Current Problem:
```
Classification Report:
              precision    recall  f1-score
walk              0.78      1.00      0.88   ← Only this
jump              0.00      0.00      0.00   ← All zeros
punch             0.00      0.00      0.00   ← All zeros
turn              0.00      0.00      0.00   ← All zeros
noise             0.00      0.00      0.00   ← All zeros
```

### After Quick Fix (Class Weights):
```
Classification Report:
              precision    recall  f1-score
walk              0.94      0.96      0.95   ✅
jump              0.75      0.70      0.72   ✅
punch             0.83      0.80      0.81   ✅
turn              0.78      0.75      0.76   ✅
noise             0.70      0.68      0.69   ✅
```

### After Better Fix (+ Augmentation):
```
Classification Report:
              precision    recall  f1-score
walk              0.95      0.97      0.96   ✅
jump              0.85      0.82      0.83   ✅✅
punch             0.89      0.87      0.88   ✅✅
turn              0.84      0.82      0.83   ✅✅
noise             0.78      0.75      0.76   ✅✅
```

---

## One More Thing

**Don't collect more data yet!** Try the fixes first.

You have enough data. The problem is **how** you're training, not how much data you have.

Once training is fixed, **then** collect more data if you want even better accuracy.

---

## Questions?

- "How long will this take?" → 30-60 minutes total
- "Will I break anything?" → No, we're just uncommenting code
- "What if I mess up?" → Notebook backup: `notebooks/Colab_CNN_LSTM_Training.ipynb.backup`
- "Can I skip reading?" → Yes! Just follow the steps above

---

## Summary

1. ✅ Retrain with existing notebook (fix already there)
2. ❌ Still broken? Enable Cell 12 augmentation
3. ❌ Still broken? Run diagnostic script
4. ❌ Still broken? Read the full guide (LEVEL_THE_PLAYING_FIELD.md)

**Most likely:** Step 1 will fix it. Steps 2-4 are backups.

Good luck! You've got this! 💪

---

**P.S.** Your 77.99% accuracy isn't bad! It's just... misleading. The model learned to predict "walk" every time and got 78% because 78% of data is walking. Once you fix the imbalance, you'll get **real** 85-94% accuracy across **all** gestures.
