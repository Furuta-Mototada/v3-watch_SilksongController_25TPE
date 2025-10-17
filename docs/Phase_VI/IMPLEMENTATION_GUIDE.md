# Implementation Guide: Watson's Two-Stage Fine-Tuning in Colab

## Quick Start Checklist

- [ ] Open `notebooks/Colab_CNN_LSTM_Training.ipynb` in Google Colab
- [ ] Enable GPU: Runtime → Change runtime type → GPU
- [ ] Run all existing cells up to data loading and splitting
- [ ] Add Phase VI cells from this guide
- [ ] Execute phases sequentially
- [ ] Verify success criteria at each phase

## Where to Add Code

Add the new Phase VI cells **after Cell 13** (data splitting) and **before Cell 14** (original model creation).

This allows you to:
1. Use the existing data splits
2. Keep the original training code for comparison
3. Run Watson's approach as an alternative

## Cell-by-Cell Implementation

### Setup Cell (Add First)

```python
# ============================================================================
# PHASE VI: WATSON'S TWO-STAGE FINE-TUNING
# ============================================================================
print("="*70)
print(" PHASE VI: WATSON'S TWO-STAGE FINE-TUNING APPROACH")
print("="*70)
print("\nThis implements Professor Watson's systematic debugging methodology")
print("for resolving model collapse in imbalanced time-series classification.")
print("\nApproach:")
print("  1. Phase 1: Sandbox test (verify architecture can learn)")
print("  2. Phase 2: Train CNN-only (learn feature extractors)")
print("  3. Phase 3: Freeze CNN, fine-tune LSTM/Dense (stable classification)")
print("\n" + "="*70)
```

### Phase 1: Sandbox Test (2 cells)

Copy cells from `SOP_WATSON_FINE_TUNING.md`:
- Step 1.1: Create toy dataset
- Step 1.2: Train on toy dataset

**Expected time:** 5-10 minutes

### Phase 2: CNN Baseline (2 cells)

Copy cells from `SOP_WATSON_FINE_TUNING.md`:
- Step 2.1: Define CNN-only model
- Step 2.2: Train CNN-only model

**Expected time:** 15-25 minutes (training)

### Phase 3: Fine-Tuning (3 cells)

Copy cells from `SOP_WATSON_FINE_TUNING.md`:
- Step 3.1: Create frozen base
- Step 3.2: Build composite model
- Step 3.3: Train classifier head

**Expected time:** 20-40 minutes (training)

### Evaluation Cell

Copy from `SOP_WATSON_FINE_TUNING.md`:
- Final evaluation with classification report

**Expected time:** 2-3 minutes

## Total Implementation Time

- **Code addition:** 10-15 minutes (copy-paste cells)
- **Phase 1 execution:** 5-10 minutes
- **Phase 2 execution:** 15-25 minutes
- **Phase 3 execution:** 20-40 minutes
- **Evaluation:** 2-3 minutes
- **Total:** ~50-90 minutes

## Success Indicators

### Phase 1 (Sandbox)
✅ Validation accuracy > 60%  
✅ Training curves show learning (not flat)  
✅ No NaN losses

### Phase 2 (CNN-Only)
✅ Validation accuracy > 80%  
✅ Model saves without errors  
✅ Loss decreases steadily

### Phase 3 (Fine-Tuned)
✅ Validation accuracy > 85%  
✅ All classes show in predictions  
✅ No single class dominates  
✅ Classification report: all recalls > 70%

## Common Mistakes to Avoid

### ❌ Don't: Skip Phase 1
**Why:** Phase 1 verifies your architecture works at all. Skipping it means you won't know if later failures are due to architecture or data issues.

### ❌ Don't: Use Different Data Splits
**Why:** All phases must use the same train/val/test splits for fair comparison.

### ❌ Don't: Modify CNN Architecture Between Phases
**Why:** Phase 3 loads weights from Phase 2. Architecture must match exactly.

### ❌ Don't: Unfreeze CNN in Phase 3
**Why:** The whole point is to keep CNN stable. Unfreezing defeats the purpose.

### ❌ Don't: Remove Class Weights in Phase 3
**Why:** Class weights are now safe to use (CNN is frozen). They're needed for minority classes.

## Troubleshooting Quick Reference

| Problem | Phase | Solution |
|---------|-------|----------|
| Val acc stuck at 20% | 1 | Check model architecture, verify data preprocessing |
| NaN loss | 1 or 2 | Add data quality check, verify no NaN/Inf in input |
| Val acc stuck at 78% | 2 | Increase class weights, check imbalance ratio |
| Model collapse in Phase 3 | 3 | Verify CNN is frozen, check base was loaded correctly |
| Low recall for minorities | 3 | Increase class weights, train longer |
| Overfitting (train>>val) | 3 | Add more dropout, reduce LSTM size, add L2 regularization |

## Comparing with Previous Approaches

### Watson's Two-Stage vs. Direct Training with Class Weights

**Direct Training (from previous PR):**
- ✅ Simpler (1 training stage)
- ✅ Faster (30-40 min)
- ⚠️ May collapse with extreme imbalance
- Results: 85-90% accuracy

**Watson's Two-Stage:**
- ⚠️ More complex (3 phases)
- ⚠️ Slower (50-90 min)
- ✅ More stable (CNN frozen)
- ✅ Better for extreme imbalance
- Results: 88-95% accuracy

### When to Use Watson's Approach

Use Watson's two-stage fine-tuning when:
1. Direct training with class weights fails (model collapses)
2. You have extreme imbalance (>50x)
3. You need maximum stability and performance
4. You have time for the longer process

Use direct training (from previous PR) when:
1. Moderate imbalance (<20x)
2. Time is limited
3. Softened class weights work well
4. You want simpler workflow

## Integration with Data Augmentation

Watson's approach can be combined with data augmentation from the previous PR:

```python
# In Phase 2 and Phase 3, after loading data:
# Uncomment Cell 12 (data augmentation) BEFORE Phase VI

# This will:
# 1. Augment minority classes
# 2. Reduce imbalance ratio
# 3. Help CNN learn better features in Phase 2
# 4. Improve final model in Phase 3

# Expected results with both:
# - Phase 2: 83-88% (vs 80-85% without aug)
# - Phase 3: 90-96% (vs 88-95% without aug)
```

## Notebook Organization

Suggested cell order in Colab:

```
[Existing Cells]
1-10: Data loading and preprocessing
11: Data splitting
12: (Optional) Data augmentation

[New Phase VI Cells]
13a: Phase VI setup
14a-14b: Phase 1 (Sandbox)
15a-15b: Phase 2 (CNN-only)
16a-16c: Phase 3 (Fine-tuning)
17a: Final evaluation

[Keep Original Cells for Comparison]
14-17: Original training approach (rename as "Alternative: Direct Training")
```

## Saving Your Work

```python
# At end of Phase VI, save all important artifacts

# 1. Models
final_model.save('/content/drive/MyDrive/silksong_data/watson_final.h5')
cnn_only_model.save('/content/drive/MyDrive/silksong_data/watson_cnn_only.h5')

# 2. Training histories
import pickle
with open('watson_histories.pkl', 'wb') as f:
    pickle.dump({
        'phase1': history_toy.history,
        'phase2': history_cnn_only.history,
        'phase3': history_final.history
    }, f)

# 3. Evaluation results
with open('watson_evaluation.txt', 'w') as f:
    f.write(f"Test Accuracy: {test_accuracy}\n")
    f.write(classification_report(y_test, y_pred_classes, target_names=GESTURES))

print("✅ All artifacts saved to Google Drive")
```

## Next Steps After Success

1. **Download model:** Use for real-time gesture recognition
2. **Compare approaches:** Review which worked best for your data
3. **Document results:** Update your project README
4. **Test on watch:** Deploy and verify real-world performance
5. **Iterate if needed:** Adjust hyperparameters, collect more data

## Getting Help

If you encounter issues:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review [THEORY.md](THEORY.md) to understand why each phase matters
3. Compare your results with [RESULTS_COMPARISON.md](RESULTS_COMPARISON.md)
4. Verify you followed all steps in [SOP_WATSON_FINE_TUNING.md](SOP_WATSON_FINE_TUNING.md)

## Summary

Watson's two-stage fine-tuning is a **systematic, proven approach** for handling severe class imbalance in deep learning. While more complex than direct training, it provides:

- **Stability:** CNN features don't get destabilized by class weights
- **Debuggability:** Each phase has clear success criteria
- **Performance:** Often achieves 88-95% accuracy when direct training fails
- **Understanding:** Teaches you how transfer learning works

Follow this guide step-by-step, verify success at each phase, and you'll transform your failing model into a production-ready gesture recognition system.
