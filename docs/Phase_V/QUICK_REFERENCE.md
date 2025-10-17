# Phase V Post-Processing Quick Reference

## TL;DR - Complete Workflow

```bash
# 1. Record continuous session (5-10 minutes)
cd src
python continuous_data_collector.py --duration 600 --session game_01

# 2. Process the recording (automated)
cd ..
./process_transcripts.sh YYYYMMDD_HHMMSS_game_01

# 3. Verify results
head -20 src/data/continuous/YYYYMMDD_HHMMSS_game_01_labels.csv
cat src/data/continuous/YYYYMMDD_HHMMSS_game_01_alignment.json
```

That's it! You now have labeled training data ready for CNN/LSTM model training.

---

## Command Reference

### Data Collection

```bash
# Basic recording (10 minutes)
python continuous_data_collector.py --duration 600 --session game_01

# Custom duration (5 minutes)
python continuous_data_collector.py --duration 300 --session quick_test

# Long session (15 minutes)
python continuous_data_collector.py --duration 900 --session long_game
```

### Post-Processing (Automated)

```bash
# Process single session
./process_transcripts.sh 20251017_143022_game_01

# Process all sessions
./process_transcripts.sh --all

# Use different WhisperX model (faster but less accurate)
./process_transcripts.sh 20251017_143022_game_01 --model medium

# Higher confidence threshold (more precision, less recall)
./process_transcripts.sh 20251017_143022_game_01 --min-confidence 0.7
```

### Post-Processing (Manual)

```bash
# Step 1: WhisperX transcription
python src/whisperx_transcribe.py \
  --audio src/data/continuous/SESSION/audio_16k.wav \
  --output src/data/continuous/SESSION/SESSION_whisperx.json

# Step 2: Label alignment
python src/align_voice_labels.py \
  --session SESSION \
  --whisper src/data/continuous/SESSION/SESSION_whisperx.json \
  --output-dir src/data/continuous
```

### Validation

```bash
# Check transcription output
cat src/data/continuous/SESSION/SESSION_whisperx_summary.txt

# View labels
head -50 src/data/continuous/SESSION_labels.csv

# Check alignment statistics
cat src/data/continuous/SESSION_alignment.json | python -m json.tool
```

---

## File Locations

### Input Files (Created by Data Collection)
- `src/data/continuous/SESSION/audio.wav` - Original 44.1kHz audio
- `src/data/continuous/SESSION/audio_16k.wav` - 16kHz for WhisperX
- `src/data/continuous/SESSION/sensor_data.csv` - IMU data
- `src/data/continuous/SESSION/metadata.json` - Session info

### Output Files (Created by Post-Processing)
- `src/data/continuous/SESSION/SESSION_whisperx.json` - Transcription
- `src/data/continuous/SESSION/SESSION_whisperx_summary.txt` - Summary
- `src/data/continuous/SESSION_labels.csv` - Gesture labels
- `src/data/continuous/SESSION_alignment.json` - Alignment stats

---

## Gesture Keywords

| Gesture | Duration | Keywords | Example |
|---------|----------|----------|---------|
| Jump | 0.3s | "jump" | "jump" |
| Punch | 0.3s | "punch", "attack" | "punch" |
| Turn | 0.5s | "turn" | "turn" |
| Noise | 1.0s | "noise" | "noise" |
| Idle | 2.0s | "idle", "rest", "stop" | "rest" |
| Walk | variable | "walk", "walking", "start" | "walk" |

**Default State**: Walk fills all gaps between commands.

---

## Common Issues & Solutions

### Issue: WhisperX not installed
```bash
# Solution
pip install whisperx
```

### Issue: No commands detected
```bash
# Solutions:
# 1. Lower confidence threshold
./process_transcripts.sh SESSION --min-confidence 0.3

# 2. Check WhisperX transcription
cat src/data/continuous/SESSION/SESSION_whisperx_summary.txt

# 3. Verify you spoke commands during recording
```

### Issue: Audio quality poor
```bash
# Solution: Re-record with better microphone setup
# - Position microphone 1-2 feet away
# - Minimize background noise
# - Speak clearly and naturally
```

### Issue: Labels look incorrect
```bash
# Solution: Review and adjust
# 1. Check alignment stats
cat src/data/continuous/SESSION_alignment.json

# 2. Validate gesture distribution
# - Walk should be 70-85% of time
# - Jump/punch should have 10-40 events each

# 3. Re-process with different settings or re-record
```

---

## Expected Output Statistics

### Good Session (10 minutes)

```
Commands detected: 60-120
Total duration: 600s
Min confidence: 0.5

Gesture Distribution:
- walk    : 450-510s (75-85%)
- jump    : 20-40 events, 6-12s total
- punch   : 20-40 events, 6-12s total
- turn    : 10-20 events, 5-10s total
- noise   : <5% of total time
```

### Warning Signs

⚠️ Commands detected: <10 (too few)  
⚠️ Walk: >95% or <50% (imbalanced)  
⚠️ Any gesture: 0 events (missing data)  
⚠️ Confidence: <0.3 average (poor audio)

**Action**: Re-record session with better technique.

---

## Next Steps After Post-Processing

1. **Validate Data Quality**
   - Review alignment statistics
   - Check gesture distribution
   - Verify label timeline is continuous

2. **Collect More Sessions**
   - Aim for 5-10 sessions minimum
   - Total duration: 30-60 minutes
   - Diverse conditions and orientations

3. **Train CNN/LSTM Model**
   - See: [CNN_LSTM_ARCHITECTURE.md](CNN_LSTM_ARCHITECTURE.md)
   - Use all labeled sessions for training
   - Evaluate on held-out test set

4. **Deploy & Iterate**
   - Integrate trained model into controller
   - Test with real gameplay
   - Collect more data to improve performance

---

## Documentation Links

- **Detailed Guides**
  - [POST_PROCESSING.md](POST_PROCESSING.md) - Complete post-processing guide
  - [DATA_COLLECTION_GUIDE.md](DATA_COLLECTION_GUIDE.md) - Recording instructions
  - [WHISPERX_GUIDE.md](WhisperX/WHISPERX_GUIDE.md) - WhisperX documentation

- **Technical Details**
  - [CNN_LSTM_ARCHITECTURE.md](CNN_LSTM_ARCHITECTURE.md) - Model architecture
  - [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) - Implementation details

- **Quick References**
  - [WHISPERX_QUICKREF.md](WhisperX/WHISPERX_QUICKREF.md) - WhisperX commands
  - [QUICK_START.md](QUICK_START.md) - Getting started guide

---

## Tips for Success

### Recording
✅ Speak commands as you perform gestures  
✅ Natural, relaxed speaking voice  
✅ Consistent timing (not too early/late)  
✅ Variety in gesture patterns  

### Post-Processing
✅ Use large-v3 or large-v2 model for best accuracy  
✅ Keep preprocessing enabled (default)  
✅ Review transcription output before alignment  
✅ Validate label quality immediately  

### Quality Control
✅ Check every session after recording  
✅ Re-record bad sessions immediately  
✅ Maintain consistent recording environment  
✅ Document any issues in session README  

---

**Last Updated**: October 17, 2025  
**Status**: Production Ready ✅
