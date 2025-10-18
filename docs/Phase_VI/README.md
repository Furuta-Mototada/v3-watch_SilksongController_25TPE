# Phase VI: Watson's Two-Stage Fine-Tuning Approach

## Overview

Phase VI implements Professor Patrick Watson's systematic debugging and training methodology for resolving model collapse in imbalanced time-series classification. This approach uses a two-stage fine-tuning strategy to build stable, high-performance gesture recognition models.

## Problem Statement

The CNN-LSTM model trained on imbalanced gesture data exhibits **model collapse**:
- Overall accuracy: 77-78% (misleading)
- Model only predicts majority class ("walk")
- All minority classes show 0% precision and recall
- Training appears successful but model is unusable in practice

## Watson's Core Insight

> "The issue is that your optimizer is being destabilized by the class weights. The CNN layers are trying to learn features while simultaneously being pushed around by the aggressive weighting scheme. This creates chaos in the gradient updates."

## Solution: Two-Stage Fine-Tuning

Instead of training all layers simultaneously with class weights, we:

1. **Stage 1**: Train CNN layers as feature extractors on full dataset
2. **Stage 2**: Freeze CNN, train only LSTM/Dense layers with class weights

This decouples feature learning from classification, preventing gradient instability.

## Documentation Structure

- **[SOP_WATSON_FINE_TUNING.md](SOP_WATSON_FINE_TUNING.md)** - Complete Standard Operating Procedure
- **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** - Step-by-step implementation in Colab
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions
- **[THEORY.md](THEORY.md)** - Why this approach works
- **[RESULTS_COMPARISON.md](RESULTS_COMPARISON.md)** - Before/after metrics

## Quick Start

```python
# Phase 1: Train CNN-only model
cnn_only_model = create_cnn_only_model(...)
cnn_only_model.fit(X_train, y_train, class_weight=class_weights)

# Phase 2: Freeze CNN, add LSTM, fine-tune
cnn_base = cnn_only_model
cnn_base.trainable = False
final_model = build_composite_model(cnn_base)
final_model.fit(X_train, y_train, class_weight=class_weights)
```

## Expected Results

| Stage | Validation Accuracy | All Classes Working? |
|-------|-------------------|---------------------|
| Original (failed) | 78% | No (only walk) |
| Stage 1 (CNN-only) | 80-85% | Partial |
| Stage 2 (Fine-tuned) | 88-95% | Yes ✅ |

## Integration with Previous Work

This Phase VI builds on:
- **Phase V**: Voice-controlled data collection (WhisperX)
- **Phase IV**: Multi-threaded ML controller
- **Phase III**: Feature engineering and SVM classifier
- **Previous PR**: Class imbalance solutions (weights, augmentation, focal loss)

Watson's approach provides an **alternative training strategy** that can be used standalone or combined with data augmentation from the previous PR.

## When to Use This Approach

✅ **Use Watson's two-stage fine-tuning when:**
- Model collapses with direct class weight application
- Data augmentation alone is insufficient
- You have extreme class imbalance (>50x)
- You need maximum stability and performance

⚠️ **Try simpler approaches first:**
- Softened class weights (from previous PR)
- Data augmentation (from previous PR)
- Focal loss (from previous PR)

## Next Steps

1. Read [SOP_WATSON_FINE_TUNING.md](SOP_WATSON_FINE_TUNING.md) for complete procedure
2. Follow [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) for Colab implementation
3. Use [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if issues arise
4. Compare results with previous approaches

## References

- Original issue: Model collapse with class imbalance
- Professor Watson's advice: Two-stage fine-tuning methodology
- Related: Andrej Karpathy's "Recipe for Training Neural Networks"
