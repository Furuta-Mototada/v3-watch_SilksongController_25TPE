# Archive Folder

This folder contains older versions and deprecated files from the v1.0 (2-class, 50-sample) system.

## What's Here

Files related to the original 2-class classification system:
- Binary classification (Rest vs Signal only)
- 25 samples per class (50 total)
- ~30 minute data collection
- No pause mechanism
- No noise class

## Current Version

For the current v2.0 system, see the parent directory:
- **Main Protocol:** `Kho2025_High-Fidelity-sEMG-Gesture-Classification_v2.md`
- **Quick Start:** `QUICK_START_3CLASS.md`
- **Data Collector:** `data_collector.py`
- **Notebook:** `CS156_Assignment_Kho_FINAL.ipynb`

## Why the Upgrade?

The v2.0 system adds a third "Noise" class to handle false positives in real-world scenarios. This makes the bike turn signal robust enough for actual road use by teaching the model to reject confounding movements like coughs, head turns, and grip adjustments.

---

**Note:** These archived files are kept for reference and reproducibility of earlier experiments.
