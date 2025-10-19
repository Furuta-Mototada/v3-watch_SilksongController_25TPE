# Documentation Index

Welcome to the Silksong Motion Controller documentation. This project has evolved through multiple phases, each with distinct approaches to data collection and gesture recognition.

---

## 📋 Quick Reference Guides

### For Assignment Reference

**⚡ [BUTTON_PROTOCOL_QUICK_START.md](BUTTON_PROTOCOL_QUICK_START.md)** ← **START HERE**  
Quick reference guide with visual diagrams and implementation checklist:
- Requirements addressed from problem statement
- Data flow diagrams
- 15-minute collection session timeline
- MVP implementation checklist
- Success criteria

**🎯 [BUTTON_DATA_COLLECTION_PROTOCOL.md](BUTTON_DATA_COLLECTION_PROTOCOL.md)**  
Complete specification for the button-based data collection protocol (20 pages). Essential reading for:
- Understanding the press-and-hold interaction model
- Implementing the Android_2_Grid app
- Setting up the three-stage pipeline (Watch → Phone → MacBook)
- Dual classifier architecture rationale
- Data integrity and testing protocols

**🤔 [ALTERNATIVE_DATA_COLLECTION_BRAINSTORM.md](ALTERNATIVE_DATA_COLLECTION_BRAINSTORM.md)**  
Design thinking and expert analysis exploring different data collection approaches:
- Voice-labeled vs. button-based trade-offs
- Expert panel perspectives (Andrew Ng, Fei-Fei Li, Michael Jordan, Don Norman, Eric Ries)
- Academic context and first draft considerations

### For Understanding Project History

**📖 [CHRONOLOGICAL_NARRATIVE.md](CHRONOLOGICAL_NARRATIVE.md)**  
Complete timeline of project evolution from V2 to current state

**📊 [REFACTOR_SUMMARY.md](REFACTOR_SUMMARY.md)**  
Recent refactoring decisions and code organization changes

**📝 [RECENT_ACTIVITY_SUMMARY.md](RECENT_ACTIVITY_SUMMARY.md)**  
Latest development activities and status updates

---

## 🔬 Phase Documentation

The project has progressed through distinct phases, each building on previous learnings:

### Phase II: Manual Data Collection *(Archived)*
**Location**: `Phase_II/`

Guided recording system with predefined physical stances. Users followed prompts to collect labeled gesture samples with manual organization.

**Status**: Superseded by voice-labeled approach  
**Key Learning**: Need for more natural, continuous data collection

---

### Phase III: SVM Classifier *(Archived)*
**Location**: `Phase_III/`

Traditional machine learning pipeline using hand-engineered features (~60 features) with SVM classification.

**Key Files**:
- `README.md` - Phase overview
- `TRAINING_DATA_FORMAT.md` - Data structure specifications
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `PHASE_IV_INTEGRATION.md` - Migration to multi-threaded controller

**Key Learning**: Feature engineering critical for IMU data; achieved ~70-75% accuracy

---

### Phase IV: Multi-Threaded Controller ✅ **(Current)**
**Location**: `Phase_IV/`

Real-time ML deployment with decoupled architecture for low-latency performance.

**Key Files**:
- `README.md` - Architecture overview
- `MULTI_THREADED_ARCHITECTURE.md` - Threading design patterns
- `ML_DEPLOYMENT_GUIDE.md` - Model integration
- `INTEGRATION_SUMMARY.md` - System integration details
- `QUICK_TEST.md` - Testing procedures

**Architecture**: Collector → Predictor → Actor (three threads with queues)  
**Achievement**: <500ms latency using 0.3s micro-windows

**Code**: `../src/udp_listener.py`

---

### Phase V: Voice-Labeled Data Collection ✅ **(Current)**
**Location**: `Phase_V/`

Natural gameplay recording with voice commands, retrospectively processed using WhisperX for word-level timestamp alignment.

**Key Approach**:
```bash
# 1. Collect natural gameplay + voice labels
python src/continuous_data_collector.py --duration 600 --session gameplay_01

# 2. Post-process with WhisperX for precise timestamps
./process_transcripts.sh YYYYMMDD_HHMMSS_gameplay_01
```

**Advantages**: Hands-free, natural motion, word-level timestamps  
**Challenges**: Voice-motion coordination, noisy labels

**Status**: Data collected but acknowledged as messy; exploring alternatives

---

### Phase VI: Button Data Collection *(Proposed)*

Press-and-hold button grid for precise, controlled data labeling during gameplay.

**Key Documentation**:
- **[BUTTON_DATA_COLLECTION_PROTOCOL.md](BUTTON_DATA_COLLECTION_PROTOCOL.md)** - Full specification
- **Android App Location**: `../Android_2_Grid/`

**Key Innovation**: Real-time labeling without interrupting gameplay flow

---

## 📚 Additional Resources

### Training Guides

**[COMPLETE_TRAINING_GUIDE.md](COMPLETE_TRAINING_GUIDE.md)**  
Comprehensive guide covering all training approaches from SVM to CNN-LSTM

### Historical Documentation

**`archive/`** - Older troubleshooting guides, training experiments, and deprecated approaches

**`v2/`** - Documentation from V2 project (pre-Pixel Watch integration)

**`v3_p1/`** - First draft pipeline documentation for CS156 assignment

**`101425_P1/`** - Specific assignment deliverables

---

## 🗺️ Documentation Navigation by Task

### "I want to implement the button data collection app"
1. Read: [BUTTON_DATA_COLLECTION_PROTOCOL.md](BUTTON_DATA_COLLECTION_PROTOCOL.md)
2. Check: `../Android_2_Grid/README.md`
3. Reference: Phase IV architecture for UDP integration

### "I want to understand why we're using buttons instead of voice"
1. Read: [ALTERNATIVE_DATA_COLLECTION_BRAINSTORM.md](ALTERNATIVE_DATA_COLLECTION_BRAINSTORM.md)
2. Compare: Phase V (voice) vs. Phase VI (button) approaches

### "I want to train a new model"
1. Read: [COMPLETE_TRAINING_GUIDE.md](COMPLETE_TRAINING_GUIDE.md)
2. Check: Phase III for SVM approach
3. Reference: `../notebooks/watson_Colab_CNN_LSTM_Training.ipynb`

### "I want to deploy the controller in real-time"
1. Read: `Phase_IV/README.md`
2. Study: `Phase_IV/MULTI_THREADED_ARCHITECTURE.md`
3. Run: `../src/udp_listener.py`

### "I want to collect new training data"
**Option A - Voice Labels** (Phase V):
1. Read: `Phase_V/` documentation
2. Run: `../src/continuous_data_collector.py`
3. Post-process: WhisperX transcription

**Option B - Button Labels** (Phase VI, Proposed):
1. Read: [BUTTON_DATA_COLLECTION_PROTOCOL.md](BUTTON_DATA_COLLECTION_PROTOCOL.md)
2. Implement: `../Android_2_Grid/` app
3. Collect: Using phone button grid

### "I need to understand the complete project history"
1. Start: [CHRONOLOGICAL_NARRATIVE.md](CHRONOLOGICAL_NARRATIVE.md)
2. Then: Read phase docs in order (II → III → IV → V → VI)
3. Context: `../README.md` for current status

---

## 📊 Project Status Summary (October 2025)

**Active Components**:
- ✅ Watch app streaming sensor data (Android/)
- ✅ Multi-threaded ML controller (Phase IV)
- ✅ Voice-labeled data collection (Phase V)
- ⏳ Button data collection protocol (Phase VI - documented, not implemented)

**Current Focus**:
- Finalizing first draft ML pipeline for CS156
- Exploring button-based data collection for improved label quality
- Documenting design decisions and trade-offs

**Next Steps**:
1. Decide: Voice data vs. button data for first draft
2. If button: Implement MVP in Android_2_Grid
3. Train models and compare approaches
4. Document findings in assignment write-up

---

## 🔗 External References

**Main README**: `../README.md` - Project overview and quick start  
**Android Watch App**: `../Android/` - Pixel Watch sensor streaming  
**Android Button App**: `../Android_2_Grid/` - Proposed button grid interface  
**Python Pipeline**: `../src/` - Data collection and ML controller  
**Notebooks**: `../notebooks/` - Training experiments (local and Colab)  
**Models**: `../models/` - Trained model artifacts

---

## 📝 Documentation Maintenance

**Last Updated**: October 18, 2025  
**Maintained By**: CarlKho-Minerva  
**Course Context**: CS156 Machine Learning - First Draft Pipeline

**Contributing**: When adding new documentation:
1. Create file in appropriate phase folder or root docs/
2. Update this README with new entry
3. Add cross-references in related documents
4. Update main project README if significant change

---

*This documentation structure reflects the iterative, exploratory nature of the project. Not all proposed approaches have been implemented - emphasis is on demonstrating design thinking and informed decision-making for academic evaluation.*
