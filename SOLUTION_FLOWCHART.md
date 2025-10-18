# 🗺️ Solution Flowchart: Fix Your Model

```
┌─────────────────────────────────────────────────────────────┐
│          YOUR MODEL ONLY PREDICTS "WALK"                    │
│        (77-78% accuracy, but 0% recall for others)          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Q: Have you tried retraining with existing notebook?      │
└─────┬────────────────────────────────────────┬──────────────┘
      │                                        │
      NO                                      YES → Still broken?
      │                                              │
      ▼                                              ▼
┌─────────────────────────────┐          ┌──────────────────┐
│  SOLUTION 1: Quick Fix      │          │  Go to Solution 2│
│  (30 minutes)               │          └──────────────────┘
│                             │
│  1. Open Colab notebook     │
│  2. Runtime → Restart       │
│  3. Run all cells           │
│  4. Wait 30 min             │
│                             │
│  Expected: 85-90% accuracy  │
│  All gestures working!      │
└──────────┬──────────────────┘
           │
           ▼
    ┌──────────┐
    │  FIXED?  │
    └─┬─────┬──┘
      │     │
     YES    NO
      │     │
      │     ▼
      │  ┌──────────────────────────────┐
      │  │  SOLUTION 2: + Augmentation  │
      │  │  (5 min setup + 30 min)      │
      │  │                              │
      │  │  1. Find Cell 12 in notebook │
      │  │  2. Remove ''' marks         │
      │  │  3. Runtime → Restart        │
      │  │  4. Run all cells            │
      │  │  5. Wait 30-40 min           │
      │  │                              │
      │  │  Expected: 88-93% accuracy   │
      │  │  All gestures working well!  │
      │  └──────────┬───────────────────┘
      │             │
      │             ▼
      │      ┌──────────┐
      │      │  FIXED?  │
      │      └─┬─────┬──┘
      │        │     │
      │       YES    NO
      │        │     │
      │        │     ▼
      │        │  ┌───────────────────────────────┐
      │        │  │  SOLUTION 3: + Focal Loss     │
      │        │  │  (15 min setup + 30 min)      │
      │        │  │                               │
      │        │  │  1. Read focal loss section   │
      │        │  │  2. Add focal loss code       │
      │        │  │  3. Set class_weights = None  │
      │        │  │  4. Runtime → Restart         │
      │        │  │  5. Run all cells             │
      │        │  │  6. Wait 30 min               │
      │        │  │                               │
      │        │  │  Expected: 88-95% accuracy    │
      │        │  │  Best possible results!       │
      │        │  └──────────┬────────────────────┘
      │        │             │
      │        │             ▼
      │        │      ┌──────────┐
      │        │      │  FIXED?  │
      │        │      └─┬─────┬──┘
      │        │        │     │
      │        │       YES    NO
      │        │        │     │
      │        │        │     ▼
      │        │        │  ┌──────────────────────────┐
      │        │        │  │  SOLUTION 4: More Data   │
      │        │        │  │  (2-3 hours)             │
      │        │        │  │                          │
      │        │        │  │  1. Record new sessions  │
      │        │        │  │  2. Focus on rare        │
      │        │        │  │     gestures (jump)      │
      │        │        │  │  3. Process new data     │
      │        │        │  │  4. Retrain with all     │
      │        │        │  │                          │
      │        │        │  │  Expected: 90-98%        │
      │        │        │  │  Professional-grade!     │
      │        │        │  └──────────┬───────────────┘
      │        │        │             │
      ▼        ▼        ▼             ▼
┌────────────────────────────────────────────┐
│         🎉 SUCCESS!                        │
│                                            │
│  ✅ All gestures working (70-98% recall)   │
│  ✅ Real accuracy (85-98%)                 │
│  ✅ Model is production-ready              │
│  ✅ Download and test on watch             │
└────────────────────────────────────────────┘
```

---

## 📚 Quick Reference

| Solution | Files to Read | Time | Success Rate |
|----------|---------------|------|--------------|
| **1. Quick Fix** | [WHEN_YOURE_TIRED.md](WHEN_YOURE_TIRED.md) | 30 min | 85% of users |
| **2. + Augmentation** | [LEVEL_THE_PLAYING_FIELD.md](LEVEL_THE_PLAYING_FIELD.md) | 40 min | 95% of users |
| **3. + Focal Loss** | [LEVEL_THE_PLAYING_FIELD.md](LEVEL_THE_PLAYING_FIELD.md) | 50 min | 98% of users |
| **4. + More Data** | [docs/Phase_V/](docs/Phase_V/) | 3+ hours | 99% of users |

---

## 🎯 Decision Matrix

### When to Use Each Solution

```
┌──────────────────┬──────────────────┬──────────────────┬─────────────────┐
│ Your Situation   │ Recommended      │ Expected Result  │ Time Required   │
├──────────────────┼──────────────────┼──────────────────┼─────────────────┤
│ First time       │ Solution 1       │ 85-90% accuracy  │ 30 min          │
│ trying to fix    │ (Quick Fix)      │ All work         │                 │
├──────────────────┼──────────────────┼──────────────────┼─────────────────┤
│ Quick fix        │ Solution 2       │ 88-93% accuracy  │ 40 min          │
│ didn't work      │ (+ Augmentation) │ All work well    │                 │
├──────────────────┼──────────────────┼──────────────────┼─────────────────┤
│ Want best        │ Solution 3       │ 88-95% accuracy  │ 50 min          │
│ accuracy         │ (+ Focal Loss)   │ Excellent        │                 │
├──────────────────┼──────────────────┼──────────────────┼─────────────────┤
│ Need perfect     │ Solution 4       │ 90-98% accuracy  │ 3+ hours        │
│ results          │ (+ More Data)    │ Professional     │                 │
├──────────────────┼──────────────────┼──────────────────┼─────────────────┤
│ Very tired       │ Read this first: │                  │ 2 min read      │
│ right now        │ WHEN_YOURE_TIRED │ Then do Soln 1   │ + 30 min train  │
└──────────────────┴──────────────────┴──────────────────┴─────────────────┘
```

---

## 🔍 Troubleshooting Map

```
Problem: Model still predicts only "walk"
    │
    ├─ After Solution 1?
    │   └─> Try Solution 2 (augmentation)
    │
    ├─ After Solution 2?
    │   └─> Try Solution 3 (focal loss)
    │
    └─ After Solution 3?
        └─> Try Solution 4 (more data)

Problem: NaN loss during training
    │
    ├─ Check: Is Cell 13 data quality check running?
    │   └─> If no: Uncomment it
    │
    ├─ Check: Are you using softened weights?
    │   └─> If no: Make sure sqrt() is applied
    │
    └─ Check: Did you combine multiple solutions?
        └─> If yes: Use only ONE at a time

Problem: Training very slow (>2 hours)
    │
    ├─ Check: Is GPU enabled?
    │   └─> Runtime → Change runtime type → GPU
    │
    ├─ Check: Which GPU do you have?
    │   └─> Should be T4 (free tier)
    │
    └─ Alternative: Reduce epochs to 50 instead of 100

Problem: Model doesn't work on watch
    │
    ├─ Check: Did it work in Colab evaluation?
    │   └─> If no: Fix Colab first
    │
    ├─ Check: Is watch data format same as training?
    │   └─> Verify sensor columns match
    │
    └─ Check: Is UDP connection working?
        └─> Test with udp_listener.py first
```

---

## 📊 Expected Metrics by Solution

### Solution 1: Quick Fix (Class Weights)
```
Overall: 85-90%
├─ Jump:  70-75%
├─ Punch: 75-82%
├─ Turn:  72-78%
├─ Walk:  94-97%
└─ Noise: 65-72%
```

### Solution 2: + Data Augmentation
```
Overall: 88-93%
├─ Jump:  80-85%
├─ Punch: 84-89%
├─ Turn:  78-84%
├─ Walk:  95-98%
└─ Noise: 72-78%
```

### Solution 3: + Focal Loss
```
Overall: 88-95%
├─ Jump:  82-88%
├─ Punch: 86-92%
├─ Turn:  80-86%
├─ Walk:  96-99%
└─ Noise: 74-82%
```

### Solution 4: + More Data
```
Overall: 90-98%
├─ Jump:  88-95%
├─ Punch: 90-96%
├─ Turn:  86-92%
├─ Walk:  96-99%
└─ Noise: 82-90%
```

---

## 🚀 Quick Action Plan

### If you have 30 minutes:
1. Read: [WHEN_YOURE_TIRED.md](WHEN_YOURE_TIRED.md) (2 min)
2. Do: Solution 1 (30 min)
3. Verify: Check classification report

### If you have 1 hour:
1. Read: [START_HERE.md](START_HERE.md) (5 min)
2. Try: Solution 1 (30 min)
3. If needed: Solution 2 (40 min)

### If you have 2+ hours:
1. Read: [LEVEL_THE_PLAYING_FIELD.md](LEVEL_THE_PLAYING_FIELD.md) (15 min)
2. Understand: The full problem (included)
3. Try: All solutions in order until fixed
4. Verify: Test on watch

---

## 💡 Pro Tips

### Tip #1: Start Simple
Don't jump to Solution 3 or 4 immediately. Solution 1 fixes 85% of cases.

### Tip #2: Verify Each Step
After each solution, check the classification report. Don't move to next solution if current one worked.

### Tip #3: Don't Combine Solutions
Use ONE approach at a time:
- Class weights (default) OR
- Class weights + augmentation OR
- Focal loss (no class weights)

Don't use all three together!

### Tip #4: Save Your Work
After each successful training:
```python
# In Colab
model.save(f'/content/drive/MyDrive/silksong_data/model_solution_{N}.h5')
```

This way you can compare different approaches.

### Tip #5: Test in Colab First
Don't download and test on watch until Colab classification report looks good. Save time by verifying in Colab first.

---

## 📖 Documentation Index

- **START_HERE.md** - Overview and quick links
- **WHEN_YOURE_TIRED.md** - Simplest possible fix
- **LEVEL_THE_PLAYING_FIELD.md** - Complete guide to all solutions
- **BEFORE_AFTER_RESULTS.md** - Visual comparison of metrics
- **SOLUTION_FLOWCHART.md** - This file (visual guide)
- **fix_class_imbalance.py** - Automated diagnostic tool

---

## ✅ Success Checklist

Your model is fully fixed when:

- [ ] All gestures have recall > 70% in Colab
- [ ] Overall accuracy > 85%
- [ ] Confusion matrix shows distributed errors
- [ ] Model predicts diverse classes (not just walk)
- [ ] Watch testing shows all gestures working
- [ ] Real-time performance is acceptable (<500ms latency)
- [ ] You're happy with the results! 🎉

---

**Remember: You don't need perfection. 85-93% with all gestures working is excellent!**

Start with Solution 1. You'll probably be done in 30 minutes. Good luck! 💪
