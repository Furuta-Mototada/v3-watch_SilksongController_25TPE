# Phase V Post-Processing Guide - WhisperX Transcription & Label Alignment

## Overview

This guide covers the **post-processing workflow** for continuous data collection sessions. After recording sensor data and audio, you'll use WhisperX for research-grade transcription with word-level timestamps, then align those voice commands with sensor data to generate training labels.

## Why WhisperX?

**WhisperX provides research-grade word segmentation** with:
- **Forced alignment** using wav2vec2 for stable per-word timings
- **Higher accuracy** on fast speech, code-switching, and noisy clips
- **VAD (Voice Activity Detection)** to trim silence and reduce boundary jitter
- **Word-level confidence scores** for quality assessment
- **Reproducible timing** essential for quantitative research

WhisperX is more reliable than Large-V3-Turbo's internal alignment, especially for gesture-command timing where precision matters.

---

## Prerequisites

### Software Requirements

1. **WhisperX Installation**
   ```bash
   pip install whisperx
   ```
   See [WHISPERX_INSTALL.md](WhisperX/WHISPERX_INSTALL.md) for detailed setup instructions.

2. **Audio Processing Libraries**
   ```bash
   pip install librosa soundfile
   ```

3. **GPU Acceleration (Recommended)**
   - CUDA: For NVIDIA GPUs (fastest)
   - MPS: For Apple Silicon Macs
   - CPU: Fallback option (slower)

### Data Requirements

Your continuous data collection session should have:
```
src/data/continuous/YYYYMMDD_HHMMSS_session_name/
├── audio.wav           # 44.1kHz original audio
├── audio_16k.wav       # 16kHz audio (for Whisper)
├── sensor_data.csv     # IMU sensor data
├── metadata.json       # Session metadata
└── README.md           # Session documentation
```

---

## Post-Processing Workflow

### Quick Start: Automated Processing

Use the provided bash script to process all sessions:

```bash
# Process a single session
./process_transcripts.sh session_20251017_143022_game_01

# Process all sessions in data/continuous/
./process_transcripts.sh --all

# Process with custom WhisperX model
./process_transcripts.sh session_20251017_143022_game_01 --model large-v2
```

### Manual Processing: Step by Step

#### Step 1: Run WhisperX Transcription

```bash
cd src

# Basic usage with default settings (large-v3 model)
python3.11 whisperx_transcribe.py \
  --audio data/continuous/20251017_125600_session/audio_16k.wav \
  --output data/continuous/20251017_125600_session/whisperx_output.json

# Advanced: Enable preprocessing and diarization
python whisperx_transcribe.py \
  --audio data/continuous/20251017_143022_game_01/audio_16k.wav \
  --output data/continuous/20251017_143022_game_01/whisperx_output.json \
  --model large-v2 \
  --diarize \
  --hf-token YOUR_HUGGINGFACE_TOKEN
```

**What happens:**
- WhisperX loads the specified model (large-v3 by default)
- Audio is preprocessed (normalization, VAD)
- Transcription generates segment-level text
- Forced alignment adds word-level timestamps
- Results saved to JSON with confidence scores

**Output files:**
```
20251017_143022_game_01/
├── whisperx_output.json          # Full transcription with word timestamps
├── whisperx_output_summary.txt   # Human-readable summary
└── preprocessed_audio_16k.wav    # Preprocessed audio (if enabled)
```

#### Step 2: Align Voice Commands with Sensor Data

```bash
# Generate gesture labels from WhisperX output
python align_voice_labels.py \
  --session 20251017_143022_game_01 \
  --whisper data/continuous/20251017_143022_game_01/whisperx_output.json \
  --output-dir data/continuous

# Filter by confidence threshold (default: 0.5)
python align_voice_labels.py \
  --session 20251017_143022_game_01 \
  --whisper data/continuous/20251017_143022_game_01/whisperx_output.json \
  --output-dir data/continuous \
  --min-confidence 0.7
```

**What happens:**
- Extracts gesture keywords from word timestamps
- Filters by confidence threshold
- Fills gaps with default "walk" state
- Generates complete label timeline
- Saves as CSV for training

**Output files:**
```
data/continuous/
├── 20251017_143022_game_01_labels.csv      # Gesture labels timeline
└── 20251017_143022_game_01_alignment.json  # Alignment metadata
```

#### Step 3: Validate and Review

```bash
# View the generated labels
head -20 data/continuous/20251017_143022_game_01_labels.csv

# Check alignment statistics
cat data/continuous/20251017_143022_game_01_alignment.json
```

**Validation checklist:**
- ✓ Gesture distribution looks reasonable (not all one gesture)
- ✓ Walk fills most of the time (expected default state)
- ✓ Jump/punch/turn events match your memory of recording
- ✓ No large gaps in timeline (should be continuous)
- ✓ Timestamps align with sensor_data.csv duration

---

## Understanding the Output

### WhisperX JSON Format

```json
{
  "segments": [
    {
      "start": 1.23,
      "end": 2.45,
      "text": "jump",
      "words": [
        {
          "word": "jump",
          "start": 1.23,
          "end": 1.56,
          "score": 0.95
        }
      ]
    }
  ],
  "language": "en"
}
```

### Labels CSV Format

```csv
timestamp,gesture,duration
0.0,walk,1.23
1.23,jump,0.3
1.53,walk,3.2
4.73,punch,0.3
...
```

### Gesture Keywords

The system recognizes these commands:

| Gesture | Duration | Keywords |
|---------|----------|----------|
| `jump` | 0.3s | "jump" |
| `punch` | 0.3s | "punch", "attack" |
| `turn` | 0.5s | "turn" |
| `noise` | 1.0s | "noise" |
| `idle` | 2.0s | "idle", "rest", "stop" |
| `walk` | variable | "walk", "walking", "start", "moving" |

**Default State:** `walk` fills all gaps between commands.

---

## Troubleshooting

### WhisperX Issues

**Problem:** `ERROR: WhisperX is not installed!`
```bash
# Solution: Install WhisperX
pip install whisperx
```

**Problem:** `CUDA out of memory`
```bash
# Solution: Use smaller model or CPU
python whisperx_transcribe.py --audio session.wav --model medium --device cpu
```

**Problem:** `No word-level timestamps`
```bash
# Solution: Ensure forced alignment is enabled (default)
# Check that you're not using --no-alignment flag
```

### Alignment Issues

**Problem:** `No commands detected`
- Check that you spoke commands during recording
- Lower confidence threshold: `--min-confidence 0.3`
- Check WhisperX output for transcription accuracy

**Problem:** `Gesture distribution is all walk`
- Review WhisperX transcription - were commands recognized?
- Check audio quality - was microphone working?
- Verify gesture keywords match what you actually said

**Problem:** `Timeline has gaps`
- This shouldn't happen - walk fills all gaps
- Check total_duration in metadata.json
- Ensure sensor_data.csv and audio.wav have matching duration

### Audio Quality Issues

**Problem:** Poor transcription accuracy
```bash
# Solution: Use audio preprocessing
python whisperx_transcribe.py --audio session.wav  # Preprocessing is enabled by default

# Or manually preprocess first
ffmpeg -i audio.wav -ar 16000 -ac 1 -c:a pcm_s16le audio_clean.wav
```

**Problem:** Background noise interferes
```bash
# Solution: Enable VAD (enabled by default)
# Or use noise reduction:
ffmpeg -i audio.wav -af "arnndn=model=model.rnnn" audio_clean.wav
```

---

## Advanced Options

### Custom WhisperX Models

```bash
# Use different Whisper model size
python whisperx_transcribe.py --audio session.wav --model large-v2   # More stable
python whisperx_transcribe.py --audio session.wav --model medium     # Faster
python whisperx_transcribe.py --audio session.wav --model small      # Lightweight
```

### Speaker Diarization

For multi-speaker recordings (not typical for this project):

```bash
# Enable diarization (requires HuggingFace token)
python whisperx_transcribe.py \
  --audio session.wav \
  --diarize \
  --hf-token YOUR_TOKEN

# Get token at: https://huggingface.co/settings/tokens
```

### Batch Processing Multiple Sessions

```bash
# Process all sessions
for session in data/continuous/*/; do
    session_name=$(basename "$session")
    echo "Processing $session_name..."
    
    # Run WhisperX
    python whisperx_transcribe.py \
      --audio "$session/audio_16k.wav" \
      --output "$session/whisperx_output.json"
    
    # Align labels
    python align_voice_labels.py \
      --session "$session_name" \
      --whisper "$session/whisperx_output.json"
done
```

---

## Best Practices

### Recording Quality
- **Speak clearly** - don't mumble commands
- **Consistent timing** - say command as you perform gesture
- **Appropriate volume** - not too loud or too soft
- **Minimal background noise** - quiet environment preferred

### Post-Processing
- **Use large-v3 or large-v2** - best accuracy for gesture commands
- **Keep preprocessing enabled** - improves transcription quality
- **Review WhisperX output** - verify commands were recognized
- **Adjust confidence threshold** - balance precision vs recall

### Data Quality
- **Short sessions** - 5-10 minutes keeps you focused
- **Regular breaks** - avoid fatigue affecting performance
- **Validate immediately** - catch issues before collecting more data
- **Document sessions** - note any issues during recording

---

## Integration with Training Pipeline

After post-processing, your labeled data is ready for CNN/LSTM training:

```bash
# Your data is now structured:
data/continuous/
├── 20251017_143022_game_01/
│   ├── sensor_data.csv     # IMU features
│   ├── *_labels.csv        # Ground truth labels
│   └── ...
├── 20251017_150000_game_02/
│   ├── sensor_data.csv
│   ├── *_labels.csv
│   └── ...
└── ...

# Use in training pipeline:
# 1. Load sensor_data.csv for features
# 2. Load *_labels.csv for ground truth
# 3. Align by timestamp
# 4. Split into train/val/test
# 5. Train CNN/LSTM model
```

See [CNN_LSTM_ARCHITECTURE.md](CNN_LSTM_ARCHITECTURE.md) for training details.

---

## Quality Metrics

### Good Post-Processing Session

✅ **WhisperX Statistics:**
- Word count: 100-300 words (for 5-10 min session)
- Average confidence: >0.8
- Language detection: Correct (usually "en")
- Alignment: Word-level timestamps present

✅ **Label Statistics:**
- Walk: 70-85% of total time
- Jump: 10-40 events
- Punch: 10-40 events
- Turn: 5-20 events
- Noise: <5% of total time

✅ **Validation:**
- No timeline gaps
- Gestures match recording memory
- Sensor data duration matches audio duration

### Warning Signs

⚠️ **Poor Quality Indicators:**
- Very few commands detected (<10)
- Walk is >95% or <50% of time
- Many low-confidence words (<0.5)
- Gestures don't match what you remember
- Large gaps in timeline

**Action:** Re-record session with better technique.

---

## Next Steps

After successful post-processing:

1. **Review Labels:** Validate alignment accuracy
2. **Collect More Data:** Aim for 30-60 minutes total across sessions
3. **Train Model:** Use labeled data for CNN/LSTM training
4. **Iterate:** Improve based on model performance

**See also:**
- [WHISPERX_GUIDE.md](WhisperX/WHISPERX_GUIDE.md) - Detailed WhisperX documentation
- [DATA_COLLECTION_GUIDE.md](DATA_COLLECTION_GUIDE.md) - Recording best practices
- [CNN_LSTM_ARCHITECTURE.md](CNN_LSTM_ARCHITECTURE.md) - Model training guide

---

## Quick Reference

### One-Command Processing

```bash
# Recommended workflow (using automation script)
./process_transcripts.sh session_20251017_143022_game_01
```

### Manual Two-Step Process

```bash
# Step 1: WhisperX
python whisperx_transcribe.py --audio data/continuous/SESSION/audio_16k.wav

# Step 2: Align
python align_voice_labels.py --session SESSION --whisper data/continuous/SESSION/SESSION_whisperx.json
```

### Validation

```bash
# Check results
head -20 data/continuous/SESSION_labels.csv
cat data/continuous/SESSION_alignment.json | grep -A 10 "gesture_stats"
```

---

**Last Updated:** October 17, 2025  
**Version:** 1.0.0  
**Status:** Production Ready ✅
