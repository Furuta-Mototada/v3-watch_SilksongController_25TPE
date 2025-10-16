# WhisperX Research-Grade Word Segmentation

Complete documentation for using WhisperX with the Silksong Motion Controller for word-specific research grade word segmentation.

## Overview

This implementation provides WhisperX integration for research-grade word-level timestamp extraction with forced alignment. WhisperX provides more stable per-word timings than Large-V3-Turbo's internal alignment, especially on fast speech, code-switching, and noisy clips.

## Quick Links

📚 **Documentation**
- [Installation Guide](WHISPERX_INSTALL.md) - Complete setup instructions
- [User Guide](WHISPERX_GUIDE.md) - Comprehensive usage documentation
- [Examples](WHISPERX_EXAMPLE.md) - Practical usage examples
- [Quick Reference](WHISPERX_QUICKREF.md) - One-page command reference

🚀 **Quick Start**

```bash
# 1. Install
pip install whisperx librosa soundfile

# 2. Transcribe
cd src
python whisperx_transcribe.py --audio session.wav --model large-v3

# 3. Align with sensor data
python align_voice_labels.py --session session --whisper session_whisperx.json
```

## What's Included

### New Scripts

1. **`src/whisperx_transcribe.py`** - Main WhisperX transcription script
   - Supports all Whisper models (large-v3, large-v2, medium, base, tiny)
   - Automatic audio preprocessing (16kHz mono, VAD, normalization)
   - Forced alignment for word-level timestamps
   - Optional speaker diarization
   - Multiple output formats (JSON, TXT, SRT)
   - GPU acceleration (CUDA, MPS, CPU)
   - Confidence scores for each word

2. **Updated `src/align_voice_labels.py`**
   - Now supports both standard Whisper and WhisperX JSON formats
   - Handles WhisperX's `score` field for confidence
   - Compatible with existing workflow

### Documentation

1. **`docs/WHISPERX_GUIDE.md`** - Complete user guide
   - Why use WhisperX for research
   - Installation and setup
   - Recommended configurations
   - Output format explanation
   - Trade-offs analysis
   - Troubleshooting

2. **`docs/WHISPERX_EXAMPLE.md`** - Practical examples
   - 10 detailed usage examples
   - Complete workflow demonstrations
   - Batch processing examples
   - Output analysis examples
   - Visualization examples

3. **`docs/WHISPERX_QUICKREF.md`** - Quick reference
   - All commands at a glance
   - Option comparison tables
   - Model comparison
   - Common issues and solutions

4. **`docs/WHISPERX_INSTALL.md`** - Installation guide
   - Step-by-step installation
   - System requirements
   - GPU setup
   - Verification steps
   - Troubleshooting

5. **`docs/WHISPERX_README.md`** - This file

### Updated Files

1. **`requirements.txt`**
   - Added `whisperx>=3.1.1`
   - Added `librosa>=0.10.0`
   - Added `soundfile>=0.12.0`

2. **`README.md`**
   - Added WhisperX section
   - Comparison with Large-V3-Turbo
   - Quick start examples

## Key Features

### Research-Grade Word Segmentation

- ✅ **Best-in-class accuracy**: Forced alignment using wav2vec2
- ✅ **Stable timestamps**: Consistent word-level timing
- ✅ **Low drift**: Better performance on long files
- ✅ **Handles difficult audio**: Fast speech, code-switching, noisy clips
- ✅ **Confidence scores**: Per-word alignment confidence (0.0-1.0)
- ✅ **Reproducible**: Consistent results for research

### Audio Preprocessing

- 🎵 **Automatic normalization**: Convert to 16kHz mono WAV
- 🎵 **VAD (Voice Activity Detection)**: Trim silence, reduce jitter
- 🎵 **Volume normalization**: Consistent audio levels
- 🎵 **Optional**: Can skip preprocessing if audio is pre-optimized

### Flexible Output

- 📄 **JSON**: Full data with word timestamps and confidence
- 📄 **TXT**: Plain text transcript
- 📄 **SRT**: Subtitle format
- 📄 **Summary**: Human-readable statistics

### Optional Features

- 👥 **Speaker Diarization**: Identify and label different speakers
- 🌍 **Multi-language**: Support for 50+ languages
- ⚡ **GPU Acceleration**: CUDA, Apple Silicon MPS, or CPU
- 🔧 **Configurable**: Batch size, model selection, output format

## Usage Overview

### Basic Workflow

```bash
# 1. Record audio and sensor data
python continuous_data_collector.py --duration 600 --session gameplay_01

# 2. Transcribe with WhisperX (research-grade)
python whisperx_transcribe.py \
  --audio ../data/continuous/gameplay_01.wav \
  --model large-v3 \
  --language en

# 3. Align voice commands with sensor data
python align_voice_labels.py \
  --session gameplay_01 \
  --whisper ../data/continuous/gameplay_01_whisperx.json \
  --min-confidence 0.7

# 4. Review results
cat ../data/continuous/gameplay_01_whisperx_summary.txt
head ../data/continuous/gameplay_01_labels.csv
```

### Output Example

**JSON Output** (`gameplay_01_whisperx.json`):
```json
{
  "segments": [
    {
      "start": 0.0,
      "end": 2.5,
      "text": "jump now turn punch",
      "words": [
        {
          "word": "jump",
          "start": 0.12,
          "end": 0.45,
          "score": 0.98
        },
        {
          "word": "turn",
          "start": 1.20,
          "end": 1.55,
          "score": 0.97
        }
      ]
    }
  ],
  "language": "en"
}
```

**Labels Output** (`gameplay_01_labels.csv`):
```csv
timestamp,gesture,duration
0.0,walk,0.12
0.12,jump,0.3
0.42,walk,0.78
1.20,turn,0.5
1.70,walk,0.18
1.88,punch,0.3
```

## Why WhisperX?

### For Research

When you need **precise, consistent timestamps** for:
- 📊 Linguistic analysis
- 🎯 Keyword timing alignment
- 📈 Quantitative metrics
- 🔬 Studies requiring reproducibility

**WhisperX's forced alignment is the safer choice.**

### Comparison

| Feature | WhisperX | Large-V3-Turbo |
|---------|----------|----------------|
| Word timing accuracy | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐ Good |
| Fast speech | ⭐⭐⭐⭐⭐ Handles well | ⭐⭐⭐ Less stable |
| Long files | ⭐⭐⭐⭐⭐ Low drift | ⭐⭐⭐ More drift |
| Noisy audio | ⭐⭐⭐⭐⭐ Robust | ⭐⭐⭐ Less robust |
| Speed | ⭐⭐⭐⭐ Fast | ⭐⭐⭐⭐⭐ Fastest |
| Setup | ⭐⭐⭐ Moderate | ⭐⭐⭐⭐⭐ Simple |
| Research use | ✅ Recommended | ⚠️ Less stable |
| Real-time | ⚠️ Possible | ✅ Optimized |

## Installation

### Quick Install

```bash
# Install WhisperX and dependencies
pip install whisperx librosa soundfile

# Verify installation
python -c "import whisperx; print('WhisperX installed!')"

# Test script
cd src
python whisperx_transcribe.py --help
```

### Full Setup

See [WHISPERX_INSTALL.md](WHISPERX_INSTALL.md) for:
- System requirements
- GPU setup (CUDA, Apple Silicon)
- Diarization setup
- Troubleshooting
- Verification steps

## Configuration

### Recommended Settings for Research

```bash
python whisperx_transcribe.py \
  --audio session.wav \
  --model large-v3 \
  --language en \
  --format json
```

**Why these settings:**
- `large-v3` or `large-v2`: Highest accuracy
- `--language en`: Better alignment (specify your language)
- `--format json`: Best for programmatic analysis
- Default preprocessing: Enabled for audio normalization

### With Diarization

```bash
python whisperx_transcribe.py \
  --audio interview.wav \
  --model large-v3 \
  --diarize \
  --hf-token YOUR_HF_TOKEN
```

Get HuggingFace token at: https://huggingface.co/settings/tokens

## Model Selection

| Model | Accuracy | Speed | Memory | Best For |
|-------|----------|-------|--------|----------|
| large-v3 | Highest | Moderate | 3GB | Research, English |
| large-v2 | Highest | Moderate | 3GB | Research, Multilingual |
| medium | Good | Fast | 1.5GB | Balance |
| base | Basic | Fastest | 150MB | Quick tests |

## About MacWhisper CoreML Models

If you have existing MacWhisper models (like those at `/Users/cvk/Library/Application Support/MacWhisper/models/`):

**Important**: These CoreML models are **not directly compatible** with WhisperX, which uses PyTorch models.

**Solution**: Let WhisperX download its own models (~3GB). They will be cached separately and won't interfere with your MacWhisper installation.

See [WHISPERX_GUIDE.md - Using Existing Models](WHISPERX_GUIDE.md#using-existing-models) for details.

## Performance

### Processing Speed (10 minutes of audio)

| Hardware | Model | Time |
|----------|-------|------|
| RTX 3090 | large-v3 | ~1-2 min |
| M2 Pro | large-v3 | ~3-5 min |
| M1 Air | medium | ~5-8 min |
| i7 CPU | medium | ~15-20 min |

### Tips for Better Performance

1. **Use GPU**: 10-20x faster than CPU
2. **Batch size**: Increase if you have more VRAM
3. **Model size**: Use `medium` on CPU for better speed
4. **Preprocessing**: Can skip if audio is pre-optimized

## Troubleshooting

Common issues and solutions:

### WhisperX not installed
```bash
pip install whisperx
```

### Out of memory
```bash
python whisperx_transcribe.py --audio file.wav --batch-size 4
```

### Alignment failed
```bash
python whisperx_transcribe.py --audio file.wav --language en
```

### Slow on CPU
```bash
python whisperx_transcribe.py --audio file.wav --model medium
```

See [WHISPERX_GUIDE.md - Troubleshooting](WHISPERX_GUIDE.md#troubleshooting) for more.

## Examples

### Example 1: Basic Transcription
```bash
python whisperx_transcribe.py --audio session.wav
```

### Example 2: With Language
```bash
python whisperx_transcribe.py --audio session.wav --language en
```

### Example 3: All Formats
```bash
python whisperx_transcribe.py --audio session.wav --format all
```

### Example 4: Complete Workflow
```bash
# Record
python continuous_data_collector.py --duration 300 --session test

# Transcribe
python whisperx_transcribe.py --audio ../data/continuous/test.wav --model large-v3

# Align
python align_voice_labels.py --session test --whisper ../data/continuous/test_whisperx.json
```

See [WHISPERX_EXAMPLE.md](WHISPERX_EXAMPLE.md) for 10 detailed examples.

## Best Practices for Research

1. ✅ **Use large-v3 or large-v2** for highest accuracy
2. ✅ **Specify language** explicitly (`--language en`)
3. ✅ **Enable preprocessing** (default) for normalization
4. ✅ **Save as JSON** for programmatic analysis
5. ✅ **Filter by confidence** >= 0.7 in post-processing
6. ✅ **Document settings** for reproducibility
7. ✅ **Validate results** spot-check for critical research

## Support and Resources

- 📖 **Documentation**: All guides in `docs/WHISPERX_*.md`
- 🐛 **Issues**: Check WhisperX GitHub issues
- 💬 **Discussions**: PyTorch forum for GPU issues
- 📚 **Research**: Cite WhisperX paper if used in publications

### External Links

- WhisperX: https://github.com/m-bain/whisperX
- Whisper: https://github.com/openai/whisper
- PyTorch: https://pytorch.org/
- HuggingFace: https://huggingface.co/

## Citation

If you use WhisperX in your research:

```bibtex
@inproceedings{bain2022whisperx,
  title={WhisperX: Time-Accurate Speech Transcription of Long-Form Audio},
  author={Bain, Max and Huh, Jaesung and Han, Tengda and Zisserman, Andrew},
  booktitle={INTERSPEECH},
  year={2023}
}
```

## Summary

**WhisperX provides research-grade word segmentation with:**
- ✅ Best-in-class word timing accuracy
- ✅ Forced alignment using wav2vec2
- ✅ Stable timestamps for long files
- ✅ Handles difficult audio conditions
- ✅ Confidence scores for validation
- ✅ Reproducible results for research

**For reproducible timing in studies or quantitative analysis, WhisperX's forced alignment is the safer choice.**

---

## Quick Command Reference

```bash
# Install
pip install whisperx librosa soundfile

# Basic usage
python whisperx_transcribe.py --audio file.wav

# Research setup
python whisperx_transcribe.py --audio file.wav --model large-v3 --language en

# With diarization
python whisperx_transcribe.py --audio file.wav --diarize --hf-token TOKEN

# Complete workflow
python continuous_data_collector.py --duration 300 --session S1
python whisperx_transcribe.py --audio ../data/continuous/S1.wav --model large-v3
python align_voice_labels.py --session S1 --whisper ../data/continuous/S1_whisperx.json
```

---

**Ready to use WhisperX?** Start with the [Installation Guide](WHISPERX_INSTALL.md)!
