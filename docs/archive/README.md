# Archive Directory

This directory contains historical documentation, troubleshooting guides, and training materials that were created during the development process but are no longer part of the main documentation structure.

## Contents

### Troubleshooting Guides (`troubleshooting/`)
These documents were created to diagnose and fix specific issues during Phase V CNN-LSTM training:

- `BALANCED_VALIDATION_FIX.md` - Addressing class imbalance in validation sets
- `DATA_PROCESSING_FIX.md` - Fixing data loading and preprocessing issues
- `DATA_TYPE_FIX.md` - Resolving TensorFlow dtype compatibility issues
- `EXTREME_IMBALANCE_FIX.md` - Handling severely imbalanced training data
- `NAN_LOSS_FIX.md` - Debugging NaN loss during training
- `WINDOW_SIZE_FIX.md` - Optimizing window size for feature extraction
- `QUICK_FIX_SUMMARY.md` - Summary of all troubleshooting solutions

**Status**: Issues resolved. Kept for reference and learning purposes.

### Training Guides (`training_guides/`)
Historical training documentation and analysis:

- `CLASS_BALANCING_GUIDE.md` - Comprehensive guide to handling class imbalance
- `QUICK_START_TRAINING.md` - Quick reference for training models
- `UPDATED_TRAINING_GUIDE.md` - Updated training procedures (superseded by Phase V docs)
- `TRAINING_RESULTS_ANALYSIS.md` - Analysis of training experiments
- `SOLUTION_SUMMARY.md` - Summary of solutions to training challenges

**Status**: Superseded by phase-specific documentation in `docs/Phase_III/` and `docs/Phase_V/`.

### Status Documents
- `ALL_SESSIONS_READY.md` - Historical status update on data collection completion
- `CHANGELOG.md` - Project changelog (no longer maintained, see git history)
- `QUICK_REFERENCE.md` - Old quick reference guide (superseded by README.md)
- `WHAT_TO_DO_NOW.md` - Historical next steps document

**Status**: Historical snapshots. Current status is in main README.md.

## Why Archive These?

These documents were valuable during active development but created clutter in the repository root. Key reasons for archiving:

1. **Over-Engineering**: For a first draft ML pipeline, having extensive troubleshooting docs suggests complexity that shouldn't be in the main view
2. **Duplication**: Many concepts are now consolidated in phase-specific documentation
3. **Historical Context**: Still valuable for understanding the development process, but not needed for current work
4. **Clean Presentation**: Academic projects should present a clear narrative, not expose every debugging session

## How to Use This Archive

- **If you encounter similar issues**: Check these documents for solutions and debugging approaches
- **For learning**: Understand common pitfalls in ML pipeline development
- **For documentation**: Reference when writing about design iterations and problem-solving

## Related Documentation

- **Current Training Guide**: `docs/Phase_V/README.md`
- **Current Architecture**: `docs/Phase_IV/README.md`
- **Project History**: `docs/CHRONOLOGICAL_NARRATIVE.md`
- **Design Thinking**: `docs/ALTERNATIVE_DATA_COLLECTION_BRAINSTORM.md`

---

**Last Updated**: October 18, 2025  
**Reason for Archive**: Repository cleanup for first draft ML pipeline presentation
