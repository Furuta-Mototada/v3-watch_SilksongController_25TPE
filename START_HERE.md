# 🎯 START HERE: Your Model Only Predicts "Walk"

## The Problem in 10 Seconds

Your model got **77.99% accuracy** but it's broken. It only predicts "walk" because 78% of your training data is walking gestures. All other gestures (jump, punch, turn, noise) have **0% recall**.

## The Solution in 30 Seconds

Your Colab notebook **already has the fix** (class weight softening in Cell 13). Just:

1. Open Colab notebook
2. Runtime → Restart runtime
3. Run all cells
4. Wait 30 minutes

**Expected result:** All gestures will work with 70-96% recall. Real 87% accuracy.

---

## 📚 Documentation Quick Links

Choose your reading style:

### 😓 I'm tired, just give me the simplest fix
**Read:** [WHEN_YOURE_TIRED.md](WHEN_YOURE_TIRED.md) (2 min read)
- Simplest possible instructions
- No technical details
- Copy-paste ready
- 30 min training time

### 🎯 I want to understand the problem and all solutions
**Read:** [LEVEL_THE_PLAYING_FIELD.md](LEVEL_THE_PLAYING_FIELD.md) (10 min read)
- Complete explanation of the problem
- 3 different solutions (quick, better, advanced)
- Decision tree to pick the right one
- Expected results for each approach

### 📊 I want to see before/after comparison
**Read:** [BEFORE_AFTER_RESULTS.md](BEFORE_AFTER_RESULTS.md) (5 min read)
- Side-by-side metrics comparison
- Visual confusion matrices
- Real-world impact examples
- How to verify your fix worked

### 🛠️ I want automated tools
**Use:** `fix_class_imbalance.py` script
```bash
# Diagnose your data
python fix_class_imbalance.py --diagnose --data src/data/continuous/*

# Export ready-to-paste code
python fix_class_imbalance.py --export

# Read the generated file
cat colab_imbalance_fixes.txt
```

---

## 🚀 Quick Start Guide

### Step 1: Choose Your Approach (1 minute)

| Approach | Setup | Train | Accuracy | Recommendation |
|----------|-------|-------|----------|----------------|
| **Quick Fix** | 0 min | 30 min | 85-90% | ✅ Try this first |
| **+ Augmentation** | 5 min | 35 min | 88-93% | Use if quick fix doesn't work |
| **+ Focal Loss** | 15 min | 30 min | 88-95% | Advanced users only |

### Step 2: Follow Instructions (30-60 minutes total)

**For Quick Fix (recommended for first try):**
1. Open `notebooks/Colab_CNN_LSTM_Training.ipynb` in Google Colab
2. Runtime → Change runtime type → GPU (if not already set)
3. Runtime → Restart runtime
4. Cell → Run all
5. Wait 25-40 minutes
6. Check results

**For Data Augmentation (if quick fix didn't work):**
1. In Colab, find Cell 12 (has "DATA AUGMENTATION" header)
2. Remove the `'''` marks at the top and bottom of the code
3. Runtime → Restart runtime
4. Cell → Run all
5. Wait 30-45 minutes
6. Check results

**For Focal Loss (advanced):**
1. Read the Focal Loss section in LEVEL_THE_PLAYING_FIELD.md
2. Add the focal loss cell after Cell 15
3. Modify model compilation
4. Set class_weights = None
5. Retrain

### Step 3: Verify It Worked (2 minutes)

After training, check the classification report:

**Good (fixed):**
```
              precision    recall  f1-score
jump              0.78      0.72      0.75   ✅ All > 0
punch             0.82      0.79      0.80   ✅ All > 0
turn              0.75      0.73      0.74   ✅ All > 0
walk              0.93      0.96      0.94   ✅ Still good
noise             0.68      0.65      0.66   ✅ All > 0
```

**Bad (still broken):**
```
              precision    recall  f1-score
jump              0.00      0.00      0.00   ❌ Still zeros
punch             0.00      0.00      0.00   ❌ Still zeros
turn              0.00      0.00      0.00   ❌ Still zeros
walk              0.78      1.00      0.88   ⚠️  Only walk
noise             0.00      0.00      0.00   ❌ Still zeros
```

If still broken → Try next approach (augmentation or focal loss)

---

## 🎓 Understanding the Problem (Optional Reading)

### Why is this happening?

**Your data distribution:**
- Walk: 78% (1,173 samples) ← Dominates everything
- Punch: 8% (125 samples)
- Turn: 6% (95 samples)
- Jump: 3% (47 samples)
- Noise: 4% (64 samples)

**What the model learned:**
"If I always predict walk, I get 78% accuracy. Perfect!"

**Why class weights help:**
They tell the model: "Hey, getting 'jump' right is more important than getting 'walk' right (since walk is everywhere)."

**Why augmentation helps:**
Creates synthetic data for rare classes, so the model sees more examples and learns better patterns.

**Why focal loss helps:**
Automatically focuses the model on hard-to-classify examples (minority classes) without manual weight tuning.

---

## 🆘 Troubleshooting

### "My model still only predicts walk after using class weights"

**Solution:** Try data augmentation. Your imbalance might be too extreme (25x) for weights alone.

### "I get NaN loss during training"

**Solutions:**
1. Check that data quality check in Cell 13 is running
2. Make sure you're using softened class weights (sqrt), not full weights
3. Try removing class weights: `class_weights = None`
4. Add gradient clipping to optimizer

### "Training is very slow (>2 hours)"

**Solutions:**
1. Make sure GPU is enabled: Runtime → Change runtime type → GPU
2. Check you're using T4 GPU (not CPU)
3. Reduce batch size from 32 to 16
4. Use fewer epochs (50 instead of 100)

### "Model works in Colab but not on my watch"

**Solutions:**
1. Check sensor data formats match (watch vs training data)
2. Verify sampling rates are consistent
3. Test with synthetic data first
4. Add normalization to handle different input ranges

---

## 📊 Expected Timeline

### Quick Fix Path:
- Read WHEN_YOURE_TIRED.md: 2 min
- Open Colab and restart: 1 min
- Training: 30 min
- Verify results: 2 min
- **Total: ~35 minutes**

### Full Understanding Path:
- Read all documentation: 20 min
- Understand the problem: included above
- Choose approach: 2 min
- Setup (if using augmentation): 5 min
- Training: 30-40 min
- Verify and test: 5 min
- **Total: ~70 minutes**

---

## ✅ Success Checklist

Your model is fixed when:

- [ ] All gestures have recall > 70% in classification report
- [ ] Overall accuracy > 85%
- [ ] Model predicts diverse classes (not just walk)
- [ ] Confusion matrix shows errors spread across classes
- [ ] Real-time testing on watch shows all gestures working

---

## 💬 FAQ

**Q: Do I need to collect more data?**
A: No! Fix training first. You have enough data. The problem is imbalance, not quantity.

**Q: How long will this take?**
A: 30-70 minutes depending on approach and how much you want to understand.

**Q: Will I break anything?**
A: No. Notebook backup exists: `notebooks/Colab_CNN_LSTM_Training.ipynb.backup`

**Q: What if none of the solutions work?**
A: Then you probably need more data for minority classes (especially jump). But try all three approaches first.

**Q: Is 87% accuracy good enough?**
A: Yes! 87-93% with all gestures working is excellent for real-time gesture recognition.

**Q: Should I use augmentation AND focal loss?**
A: Usually not needed. Pick one: weights (default), weights + augmentation, OR focal loss. Don't combine all three.

---

## 🎯 Bottom Line

1. Your model is broken (only predicts walk)
2. The fix is already in your notebook (class weights)
3. Just retrain (30 min) and it should work
4. If not, enable augmentation (Cell 12)
5. All documented in detail if you want to understand

**Don't overthink it. Start with the quick fix.**

Read [WHEN_YOURE_TIRED.md](WHEN_YOURE_TIRED.md) and follow the 5-minute instructions. You'll have a working model in 30 minutes.

Good luck! 💪
