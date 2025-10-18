# ✅ Model Fix Progress Checklist

Use this checklist to track your progress fixing the class imbalance issue.

---

## 📋 Pre-Flight Check

Before starting, verify:

- [ ] I have access to Google Colab
- [ ] I can see my training data in Google Drive (`MyDrive/silksong_data/`)
- [ ] I have at least 45 minutes available
- [ ] I understand the problem (model only predicts "walk")
- [ ] I've read at least one of: WHEN_YOURE_TIRED.md or START_HERE.md

---

## 🚀 Solution 1: Quick Fix (Try This First!)

### Setup (2 minutes)
- [ ] Opened `notebooks/Colab_CNN_LSTM_Training.ipynb` in Colab
- [ ] Checked GPU is enabled (Runtime → Change runtime type → GPU)
- [ ] Confirmed it shows "GPU: T4" or similar

### Training (30 minutes)
- [ ] Clicked Runtime → Restart runtime
- [ ] Clicked Cell → Run all (or Ctrl+F9)
- [ ] Training started without errors
- [ ] Waited for training to complete (25-40 minutes)
- [ ] No NaN loss appeared during training

### Verification (5 minutes)
- [ ] Classification report shows ALL gestures with recall > 0
- [ ] Jump recall > 70%
- [ ] Punch recall > 70%
- [ ] Turn recall > 70%
- [ ] Walk recall > 90%
- [ ] Noise recall > 60%
- [ ] Overall accuracy > 85%

### Result
- [ ] ✅ **FIXED!** → Go to "Download and Test" section
- [ ] ❌ **Still broken** → Go to Solution 2

---

## 🎨 Solution 2: Add Data Augmentation

### Setup (5 minutes)
- [ ] Found Cell 12 in notebook (has "DATA AUGMENTATION" header)
- [ ] Removed the `'''` marks at top and bottom of cell code
- [ ] Verified code is now uncommented (no grey text)

### Training (35 minutes)
- [ ] Clicked Runtime → Restart runtime
- [ ] Clicked Cell → Run all
- [ ] Cell 12 shows "DATA AUGMENTATION ENABLED"
- [ ] Cell 12 shows "Added X augmented samples"
- [ ] Training completed successfully
- [ ] No NaN loss during training

### Verification (5 minutes)
- [ ] Classification report shows improved recall for all gestures
- [ ] Jump recall > 80%
- [ ] Punch recall > 80%
- [ ] Turn recall > 75%
- [ ] Walk recall > 90%
- [ ] Noise recall > 70%
- [ ] Overall accuracy > 88%

### Result
- [ ] ✅ **FIXED!** → Go to "Download and Test" section
- [ ] ❌ **Still broken** → Go to Solution 3

---

## 🔥 Solution 3: Use Focal Loss

### Setup (15 minutes)
- [ ] Read focal loss section in LEVEL_THE_PLAYING_FIELD.md
- [ ] Copied focal loss code from guide
- [ ] Added new cell AFTER Cell 15 (model creation)
- [ ] Pasted focal loss function definition
- [ ] Modified model.compile() to use focal_loss()
- [ ] Added `class_weights = None` in Cell 13

### Training (30 minutes)
- [ ] Clicked Runtime → Restart runtime
- [ ] Clicked Cell → Run all
- [ ] New focal loss cell executed without errors
- [ ] Model compilation shows "focal loss" mention
- [ ] Training completed successfully
- [ ] No NaN loss during training

### Verification (5 minutes)
- [ ] Classification report shows excellent results
- [ ] Jump recall > 82%
- [ ] Punch recall > 85%
- [ ] Turn recall > 80%
- [ ] Walk recall > 92%
- [ ] Noise recall > 75%
- [ ] Overall accuracy > 88%

### Result
- [ ] ✅ **FIXED!** → Go to "Download and Test" section
- [ ] ❌ **Still broken** → Consider collecting more data (Solution 4)

---

## 💾 Download and Test

### Download Model
- [ ] Training completed successfully in Colab
- [ ] Model file exists: Check Files tab in Colab for `best_model.h5`
- [ ] Downloaded model to local machine
- [ ] Or saved to Google Drive: `/content/drive/MyDrive/silksong_data/cnn_lstm_gesture.h5`

### Test in Colab First
- [ ] Ran test set evaluation (Cell with `model.evaluate()`)
- [ ] Checked classification report looks good
- [ ] Tested 10 random predictions (see verification code in guides)
- [ ] All gestures being predicted (not just walk)

### Test Locally
- [ ] Moved model to project: `models/cnn_lstm_gesture.h5`
- [ ] Started UDP listener: `cd src && python udp_listener_v3.py`
- [ ] Started watch app
- [ ] Performed test gestures
- [ ] Jump gesture detected correctly
- [ ] Punch gesture detected correctly
- [ ] Turn gesture detected correctly
- [ ] Walk gesture detected correctly
- [ ] Overall performance is acceptable

---

## 🐛 Troubleshooting Checklist

### If NaN Loss Appears
- [ ] Checked Cell 13 data quality check is running
- [ ] Verified no NaN/Inf values reported in data
- [ ] Confirmed using softened class weights (sqrt applied)
- [ ] Tried removing class weights: `class_weights = None`
- [ ] Added gradient clipping: `clipnorm=1.0` in optimizer

### If Training is Too Slow
- [ ] Verified GPU is enabled (should take 25-40 min, not 2+ hours)
- [ ] Checked GPU type is T4 or better
- [ ] Tried reducing batch size to 16
- [ ] Considered reducing epochs to 50

### If Model Still Only Predicts Walk
- [ ] Verified class weights are being used (check Cell 13 output)
- [ ] Tried enabling data augmentation (Solution 2)
- [ ] Tried focal loss (Solution 3)
- [ ] Read LEVEL_THE_PLAYING_FIELD.md for more strategies

### If Model Works in Colab but Not on Watch
- [ ] Verified sensor data format matches (accel_x, accel_y, etc.)
- [ ] Checked UDP connection is working
- [ ] Tested with synthetic data first
- [ ] Added normalization if needed

---

## 📊 Results Tracking

Record your results here for each attempt:

### Attempt 1: Quick Fix (Solution 1)
Date: ___________  
Overall Accuracy: ______%  
Jump Recall: ______%  
Punch Recall: ______%  
Turn Recall: ______%  
Walk Recall: ______%  
Noise Recall: ______%  
Status: ⬜ Fixed ⬜ Still broken

### Attempt 2: + Augmentation (Solution 2)
Date: ___________  
Overall Accuracy: ______%  
Jump Recall: ______%  
Punch Recall: ______%  
Turn Recall: ______%  
Walk Recall: ______%  
Noise Recall: ______%  
Status: ⬜ Fixed ⬜ Still broken

### Attempt 3: + Focal Loss (Solution 3)
Date: ___________  
Overall Accuracy: ______%  
Jump Recall: ______%  
Punch Recall: ______%  
Turn Recall: ______%  
Walk Recall: ______%  
Noise Recall: ______%  
Status: ⬜ Fixed ⬜ Still broken

---

## 🎉 Success Criteria

Mark all that apply:

- [ ] Overall accuracy > 85%
- [ ] All gestures have recall > 70%
- [ ] No gesture has 100% recall (sign of overfitting)
- [ ] Confusion matrix shows distributed errors
- [ ] Model predicts diverse classes in random tests
- [ ] Watch testing shows acceptable real-time performance
- [ ] I'm satisfied with the results!

---

## 📝 Notes

Use this space to track any issues, observations, or customizations:

```
Date: 
Issue: 
Solution tried: 
Result: 


Date: 
Issue: 
Solution tried: 
Result: 


Date: 
Issue: 
Solution tried: 
Result: 
```

---

## 🆘 Getting Help

If you're still stuck after trying all solutions:

1. **Check documentation:**
   - [ ] Read LEVEL_THE_PLAYING_FIELD.md thoroughly
   - [ ] Reviewed SOLUTION_FLOWCHART.md
   - [ ] Checked BEFORE_AFTER_RESULTS.md for expected metrics

2. **Run diagnostics:**
   ```bash
   python fix_class_imbalance.py --diagnose --data src/data/continuous/*
   python fix_class_imbalance.py --export
   ```

3. **Collect debug info:**
   - [ ] Screenshot of classification report
   - [ ] Copy of training logs (especially last 5 epochs)
   - [ ] Output of class distribution check (Cell 13)
   - [ ] Any error messages

4. **Consider:**
   - [ ] Recording more data for minority classes (especially jump)
   - [ ] Checking data quality (are labels correct?)
   - [ ] Trying a different model architecture

---

## ✨ Final Checklist

Before considering the issue resolved:

- [ ] Model achieves target accuracy (>85%)
- [ ] All gestures work in Colab evaluation
- [ ] Model downloaded and saved
- [ ] Tested on watch with real gestures
- [ ] Performance is acceptable for real-time use
- [ ] Documentation reviewed and understood
- [ ] Future improvements documented (if needed)

---

**Congratulations on fixing your model! 🎉**

Remember to:
- Save your working model
- Document what worked for future reference
- Consider collecting more data for even better results
- Share your success! The approach that worked for you might help others

Good luck with your gesture recognition project! 🚀
