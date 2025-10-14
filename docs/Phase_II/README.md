# Phase II Documentation Index

Welcome to the Phase II documentation for the Silksong Controller project. This phase focuses on guided data collection for machine learning gesture recognition.

## � NEW: Hybrid Data Collection Protocol (v3.1.0)

**MAJOR UPDATE (Oct 14, 2025):** We've implemented a sophisticated hybrid approach that treats event-based gestures (PUNCH, JUMP, TURN) differently from state-based gestures (WALK). This fundamental improvement enhances data quality and model robustness.

-   **`IMPLEMENTATION_SUMMARY.md`** ⭐ **START HERE** - Executive summary of the hybrid protocol
-   **`HYBRID_COLLECTION_PROTOCOL.md`** - Complete technical specification
-   **`HYBRID_PROTOCOL_VISUAL.md`** - Visual diagrams and flowcharts

**Key Benefits:**
- 37x more training examples for WALK gesture
- 13% faster data collection
- Training-inference alignment (both use sliding windows)
- Significantly improved model robustness

## �📚 Documentation Overview

### Getting Started

-   **`QUICK_START.md`** - 5-minute guide to run your first data collection session.
    -   Prerequisites checklist
    -   Simple setup steps
    -   What to expect
    -   Tips for success

### Comprehensive Guide

-   **`DATA_COLLECTION_GUIDE.md`** - Full technical documentation.
    -   Design principles and architecture
    -   Detailed stance and gesture definitions
    -   Complete workflow walkthrough
    -   Output format specification
    -   Best practices and troubleshooting
    -   Technical notes on sensors

### Examples and References

-   **`SAMPLE_OUTPUT.md`** - What to expect from data collection.
    -   Console output examples
    -   File system structure
    -   CSV data format samples
    -   Python loading examples
    -   Data statistics

-   **`ML_PIPELINE_PREVIEW.md`** - Preview of Phase III.
    -   Feature engineering examples
    -   Model training code
    -   Real-time deployment strategy
    -   Performance expectations
    -   Visualization tools

## 🎯 Quick Navigation

**I want to...**

-   ...collect training data for the first time → Start with [`QUICK_START.md`](./QUICK_START.md)
-   ...understand the technical details → Read [`DATA_COLLECTION_GUIDE.md`](./DATA_COLLECTION_GUIDE.md)
-   ...see what the output looks like → Check [`SAMPLE_OUTPUT.md`](./SAMPLE_OUTPUT.md)
-   ...prepare for ML model training → Review [`ML_PIPELINE_PREVIEW.md`](./ML_PIPELINE_PREVIEW.md)
-   ...troubleshoot connection issues → See `DATA_COLLECTION_GUIDE.md#troubleshooting` or refer to [`../101425_P1/TESTING_GUIDE.md`](../101425_P1/TESTING_GUIDE.md)

## 🗂️ File Structure

```
docs/Phase_II/
├── README.md                    ← You are here
├── QUICK_START.md               ← Start here for first-time users
├── DATA_COLLECTION_GUIDE.md     ← Comprehensive technical guide
├── SAMPLE_OUTPUT.md             ← Examples and reference
└── ML_PIPELINE_PREVIEW.md       ← Phase III preparation
```

## 🎮 What is Phase II?

Phase II builds on Phase I's real-time sensor streaming to create a data collection pipeline for training machine learning models. Instead of using hand-tuned thresholds for gesture detection, Phase II collects labeled training data that will enable more robust, personalized gesture recognition in Phase III.

### Key Features

-   **Guided Collection**: Step-by-step prompts through stances and gestures.
-   **Structured Protocol**: 3 stances, 8 gestures, 5 samples each.
-   **High-Fidelity Data**: 3-second time-series recordings at ~50Hz.
-   **Proper Labeling**: Gesture, stance, sample, and timestamp metadata.
-   **ML-Ready Output**: CSV files ready for feature engineering.

### Design Philosophy

Based on lessons from the EMG project (mentioned in problem statement):

-   ✅ Use composite sensors for efficient data collection.
-   ✅ Define user stances before gesture execution.
-   ✅ Provide clear, unambiguous instructions.
-   ✅ Record full time-series dynamics.
-   ✅ Enable reproducible data collection.

## 📊 Data Collection At A Glance

| Parameter             | Value                                     |
| --------------------- | ----------------------------------------- |
| **Total Duration**    | 20-30 minutes                             |
| **Gestures**          | 8 types                                   |
| **Samples per Gesture** | 5                                         |
| **Recording per Sample**| 3 seconds                                 |
| **Sensors**           | `rotation_vector`, `linear_acceleration`, `gyroscope` |
| **Output Files**      | 40 CSV files + 1 metadata JSON            |
| **Total Data Points** | ~6,000 sensor readings                    |

## 🚀 Quick Command Reference

```bash
# Run data collection
cd src
python data_collector.py

# Check if script is working
python -c "import data_collector; print('OK')"

# View collected data
ls training_data/session_*/

# Load data in Python
python -c "import pandas as pd; df = pd.read_csv('training_data/session_*/punch_forward_sample01.csv'); print(df.head())"
```

## 🔗 Related Documentation

-   **Phase I (Prerequisites)**
    -   [`../101425_P1/TESTING_GUIDE.md`](../101425_P1/TESTING_GUIDE.md) - Setting up watch connection
    -   [`../101425_P1/AUTOMATIC_CONNECTION.md`](../101425_P1/AUTOMATIC_CONNECTION.md) - Network service discovery
-   **Core Project Documentation**
    -   [`../v2/DEVELOPER_GUIDE.md`](../v2/DEVELOPER_GUIDE.md) - Development workflow
    -   [`../v2/PROJECT_STRUCTURE.md`](../v2/PROJECT_STRUCTURE.md) - Repository organization
    -   [`../../README.md`](../../README.md) - Project overview
-   **Android App**
    -   `../../Android/app/src/main/java/com/cvk/silksongcontroller/MainActivity.kt` - Sensor streaming code

## 💡 Tips for Success

-   **Environment**: Clear space, comfortable temperature, water nearby.
-   **Hardware**: Watch charged (>50%), secure fit on wrist.
-   **Connection**: Verify streaming before starting collection.
-   **Execution**: Deliberate motions, consistent technique, return to stance.
-   **Breaks**: Take breaks between gestures and stances.
-   **Quality > Speed**: Focus on good form, not rushing through.

## 🐛 Common Issues

-   **No sensor data received**
    -   Check watch streaming toggle is **ON**.
    -   Verify both devices on same network.
    -   Ensure `udp_listener.py` is **NOT** running (port conflict).
-   **Low data point count**
    -   Keep watch screen awake (tap periodically).
    -   Check WiFi signal strength.
    -   Move closer to WiFi router if needed.
-   **Inconsistent gestures**
    -   Review stance description before each recording.
    -   Practice gesture once before recording.
    -   Take longer breaks if fatigued.

> See full troubleshooting section in [`DATA_COLLECTION_GUIDE.md`](./DATA_COLLECTION_GUIDE.md).

## 📈 Project Phases Overview

-   **Phase I** ✅ - Sensor streaming and automatic connection (Complete)
-   **Phase II** ← You are here - Guided data collection (In Progress)
-   **Phase III** 🔮 - Machine learning model training (Next)
-   **Phase IV** 🔮 - Real-time ML-based gesture recognition (Future)

## 🤝 Contributing

If you collect multiple data sessions, consider:

-   Varying your execution style (fast/slow, large/small motions).
-   Recording at different times of day (fatigue effects).
-   Testing with different users (generalization).

More diverse data = more robust models!

---

## 📝 Version History

-   **v1.0 (2025-10-13)** - Initial Phase II implementation
    -   Complete data collection script
    -   Comprehensive documentation
    -   8 gestures across 3 stances
    -   CSV export and metadata tracking

## 📞 Support

-   **Technical Issues**: Check troubleshooting sections in guides.
-   **Feature Requests**: Open issue on GitHub repository.
-   **Questions**: Review full documentation or contact maintainer.

---

> ### Ready to collect data? → [Start with QUICK_START.md](./QUICK_START.md)
>
> ### Want to understand the details first? → [Read DATA_COLLECTION_GUIDE.md](./DATA_COLLECTION_GUIDE.md)
