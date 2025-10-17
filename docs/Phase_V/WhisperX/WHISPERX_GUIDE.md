# WhisperX Research-Grade Word Segmentation Guide

This guide explains how to use WhisperX for word-specific research-grade word segmentation with precise, consistent timestamps for linguistic analysis, alignment, or keyword timing.

## Table of Contents

- [Why WhisperX?](#why-whisperx)
- [Voice Command Reference](#voice-command-reference)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Recommended Setup for Research](#recommended-setup-for-research)
- [Using Existing Models](#using-existing-models)
- [Complete Workflow](#complete-workflow)
- [Output Format](#output-format)
- [Trade-offs](#trade-offs)
- [Troubleshooting](#troubleshooting)

## Why WhisperX?

For word-level research—where you need precise, consistent timestamps for linguistic analysis, alignment, or keyword timing—WhisperX with forced alignment is the best choice.

### Benefits

- **Best-in-class word timing accuracy**: Forced alignment using wav2vec2 provides more stable per-word timings
- **Fewer drift issues**: Better handling of long files compared to standard Whisper
- **Handles difficult audio**: More reliable on fast speech, code-switching, and noisy clips
- **Reproducible results**: Consistent timing for studies and quantitative analysis

### When to Use WhisperX

- ✅ Research-grade word timestamps needed
- ✅ Linguistic analysis or keyword timing
- ✅ Fine-grained quantitative metrics
- ✅ Fast speech, code-switching, or noisy audio
- ✅ Long audio files (reduced boundary jitter)

### When to Use Large-V3-Turbo Instead

- ✅ Real-time transcription needed
- ✅ Speed is more important than precision
- ✅ General-purpose transcription
- ⚠️ Word timings are less stable for fine-grained research

## Voice Command Reference

### Quick Answer: How to Label Your Gestures

**Q: Should I say "walk start" once or multiple times?**
**A: Just once at the beginning!** All gaps between gestures are automatically filled with "walk" labels.

**Q: Can I be more specific, like stopping before a jump?**
**A: Yes! Use "idle", "rest", or "stop" to mark when you're standing still.**

**Q: Can I say "walk end"?**
**A: You can, but it's unnecessary.** The system treats it the same as "walk". Just start your next gesture when ready.

### Command Categories

| Category | Commands | Duration | When to Use |
|----------|----------|----------|-------------|
| **Gestures** | `jump`, `punch`, `turn` | 0.3-0.5s | Right when you perform the action |
| **States** | `walk`, `idle`, `rest`, `stop` | 1-2s | To mark movement states |
| **Other** | `noise` | 1.0s | Non-game movements (adjusting watch, etc.) |

### Detailed Command Guide

#### Gesture Commands (Action Labels)
- **`jump`** - Jump gesture (0.3s label)
- **`punch`** - Attack/punch gesture (0.3s label)
- **`turn`** - Turn around gesture (0.5s label)

#### State Commands (Movement Labels)
- **`walk`** / **`walking`** / **`start`** - Walking/moving state
  - Default state - automatically fills all gaps
  - Say "walk start" at beginning
  - Optional: Say "walk" occasionally to reinforce
- **`idle`** / **`rest`** / **`stop`** - Standing still state (2.0s label)
  - Use when you stop moving to prepare for a precise gesture
  - Creates a distinct "not walking" period
  - Example: "idle" [stand still] "jump" [precise jump from standing]

#### Other Commands
- **`noise`** - Non-game movement (1.0s label)
  - Adjusting watch, scratching, fidgeting
  - Any movement that's NOT part of gameplay

### Usage Examples

#### Simple Flow (Recommended for Most Cases)
```text
[Start recording]
"walk start" → [walk naturally for 10s, automatic labeling]
"jump" → [jump gesture while walking]
→ [walk for 5s, automatic labeling]
"punch" → [punch gesture]
→ [walk for 8s, automatic labeling]
"turn" → [turn gesture]
```

**Result:** Gaps automatically labeled as "walk" - no need to keep saying it!

#### Precise Control Flow (For Specific Needs)
```text
[Start recording]
"walk start" → [walk for 10s, automatic]
"idle" → [stop walking, stand still for 2s]
"jump" → [precise jump from stationary position]
→ [walk resumes automatically]
"rest" → [stop, prepare for combo]
"punch jump turn" → [execute combo from standing]
→ [walk resumes automatically]
```

**Result:** Mix walking with stationary periods for more precise gesture timing.

### What the System Does

1. **Detects keywords** in your speech: `jump`, `punch`, `turn`, `idle`, `walk`, etc.
2. **Creates time-stamped labels** at the word's timestamp
3. **Fills ALL gaps** between labels with "walk" (default state)
4. **No "end" commands needed** - next command automatically ends the previous state

### Pro Tips

✅ **DO:**
- Say "walk start" at the beginning to mark baseline
- Speak commands RIGHT when performing gestures
- Use "idle"/"rest"/"stop" when you need precision
- Speak naturally - keywords are detected within sentences

❌ **DON'T:**
- Don't worry about saying "walk end" or "stop walking"
- Don't keep repeating "walk" - it's automatic
- Don't speak commands without performing gestures
- Don't perform gestures without speaking

## Installation

### 1. Install WhisperX

```bash
# Install WhisperX and dependencies
pip install whisperx

# Or install from the project requirements
pip install -r requirements.txt
```

### 2. System Dependencies

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download ffmpeg from https://ffmpeg.org/download.html and add to PATH.

### 3. Optional: GPU Support

For faster processing, install PyTorch with CUDA support:

```bash
# CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

For Apple Silicon (M1/M2/M3), PyTorch with MPS support is included by default.

## Quick Start

### Basic Usage

```bash
# Transcribe with default settings (large-v3 model)
cd src
python whisperx_transcribe.py --audio ../data/continuous/session_01.wav
```

This will:
1. Load the audio file
2. Preprocess (normalize to 16kHz mono, apply VAD)
3. Transcribe using Whisper large-v3
4. Apply forced alignment for word-level timestamps
5. Save results as JSON with word timestamps and confidence scores

### Output

The script creates:
- `session_01_whisperx.json` - Full transcription with word-level timestamps
- `session_01_whisperx_summary.txt` - Human-readable summary

## Recommended Setup for Research

For the best research-grade results, use these settings:

```bash
python whisperx_transcribe.py \
  --audio session_01.wav \
  --model large-v3 \
  --language en \
  --format all
```

### Key Parameters

- `--model large-v3`: Highest accuracy model (or `large-v2` for better multilingual support)
- `--language en`: Specify language for better alignment (auto-detect if omitted)
- `--format all`: Save JSON, TXT, and SRT formats

### With Diarization (Speaker Segmentation)

If speaker segmentation matters:

```bash
python whisperx_transcribe.py \
  --audio session_01.wav \
  --model large-v3 \
  --diarize \
  --hf-token YOUR_HUGGINGFACE_TOKEN
```

Get a HuggingFace token at: https://huggingface.co/settings/tokens

## Using Existing Models

### Option 1: Let WhisperX Download Models

WhisperX will automatically download models on first use. They're cached in:
- Linux/macOS: `~/.cache/whisper/`
- Windows: `%USERPROFILE%\.cache\whisper\`

### Option 2: Use Existing Whisper Models

If you already have Whisper models (like MacWhisper CoreML models), note the following:

#### About MacWhisper CoreML Models

The MacWhisper CoreML models (like those at `/Users/cvk/Library/Application Support/MacWhisper/models/whisperkit/models/`) are optimized for Apple's CoreML framework and are **not directly compatible** with WhisperX, which uses PyTorch models.

**Key differences:**
- **MacWhisper/WhisperKit**: Uses CoreML format (.mlmodelc files) optimized for Apple Neural Engine
- **WhisperX**: Uses PyTorch format (.pt files) for cross-platform compatibility
- **File structure**: CoreML has AudioEncoder.mlmodelc, TextDecoder.mlmodelc, etc.
- **PyTorch**: Has single .pt files with all weights

#### Solution: Let WhisperX Download Its Own Models

The easiest and recommended approach:

```bash
# Just specify the model name - WhisperX handles downloading
python whisperx_transcribe.py --audio session_01.wav --model large-v3
```

**Benefits:**
- Automatic download and caching
- Cross-platform compatibility
- Guaranteed compatibility with forced alignment
- No conversion needed

**Storage:**
- WhisperX models are cached in `~/.cache/whisper/`
- Models are relatively compact:
  - `large-v3`: ~3GB (PyTorch)
  - `large-v2`: ~3GB (PyTorch)
  - `medium`: ~1.5GB (PyTorch)
- Your CoreML models can stay where they are for MacWhisper

#### Why Not Convert?

Converting CoreML to PyTorch for Whisper is complex:
1. Export from CoreML to ONNX format
2. Convert ONNX to PyTorch
3. Align weight names with Whisper model structure
4. Test compatibility with forced alignment models
5. Validate accuracy matches original

**Our recommendation:** Let WhisperX use its own models. The 3GB download is worth it for:
- Guaranteed compatibility
- No conversion headaches
- Better support and updates
- Consistent behavior across platforms

## Complete Workflow

### 1. Record Audio and Sensor Data

```bash
cd src
python continuous_data_collector.py --duration 600 --session gameplay_01
```

This records:
- Sensor data from smartwatch
- Audio from microphone (16kHz mono WAV)

### 2. Transcribe with WhisperX

```bash
python whisperx_transcribe.py \
  --audio ../data/continuous/gameplay_01.wav \
  --model large-v3 \
  --language en \
  --format json
```

Output: `gameplay_01_whisperx.json`

### 3. Align Voice Commands with Sensor Data

```bash
python align_voice_labels.py \
  --session gameplay_01 \
  --whisper ../data/continuous/gameplay_01_whisperx.json
```

This generates:
- `gameplay_01_labels.csv` - Gesture labels aligned with sensor timestamps
- `gameplay_01_alignment.json` - Alignment metadata and statistics

### 4. Review and Validate

Check the generated labels:

```bash
# View summary
cat ../data/continuous/gameplay_01_whisperx_summary.txt

# View aligned labels
head -20 ../data/continuous/gameplay_01_labels.csv
```

## Output Format

### JSON Structure

The WhisperX JSON output contains:

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
          "word": "now",
          "start": 0.48,
          "end": 0.65,
          "score": 0.95
        },
        {
          "word": "turn",
          "start": 1.20,
          "end": 1.55,
          "score": 0.97
        },
        {
          "word": "punch",
          "start": 1.88,
          "end": 2.15,
          "score": 0.99
        }
      ]
    }
  ],
  "language": "en"
}
```

### Key Fields

- `start`, `end`: Word-level timestamps in seconds (precise to milliseconds)
- `word`: Transcribed word text
- `score`: Confidence score (0.0 - 1.0) from forced alignment
- `speaker`: Speaker label (if diarization enabled)

### Confidence Scores

WhisperX provides alignment confidence scores:
- `> 0.9`: Excellent alignment
- `0.7 - 0.9`: Good alignment
- `0.5 - 0.7`: Fair alignment
- `< 0.5`: Poor alignment (consider reviewing)

Filter by confidence in post-processing:

```bash
python align_voice_labels.py \
  --session gameplay_01 \
  --whisper gameplay_01_whisperx.json \
  --min-confidence 0.7
```

## Trade-offs

### WhisperX

**Pros:**
- ✅ Best-in-class word timing accuracy
- ✅ Fewer drift issues over long files
- ✅ Better handling of fast speech, code-switching, noisy clips
- ✅ Reproducible timing for research
- ✅ Confidence scores for each word

**Cons:**
- ⚠️ Slightly heavier pipeline (requires alignment model)
- ⚠️ Slower than Large-V3-Turbo (but still fast on GPU)
- ⚠️ Requires ~3GB model download

### Large-V3-Turbo

**Pros:**
- ✅ Fastest option
- ✅ Simple, single model
- ✅ Good for general transcription

**Cons:**
- ⚠️ Word timings less stable for fine-grained research
- ⚠️ More drift on long files
- ⚠️ Less accurate on difficult audio

## Troubleshooting

### Issue: "WhisperX is not installed"

```bash
pip install whisperx
```

If installation fails, try:
```bash
pip install git+https://github.com/m-bain/whisperX.git
```

### Issue: "No GPU available"

WhisperX works on CPU but is slower. For faster processing:
- **NVIDIA GPU**: Install CUDA-enabled PyTorch
- **Apple Silicon**: PyTorch with MPS support is automatic
- **CPU only**: Consider using smaller models (`medium` instead of `large-v3`)

### Issue: "Alignment failed"

If forced alignment fails:
1. Specify the language explicitly: `--language en`
2. Try a different model: `--model large-v2`
3. Skip alignment for basic transcription: `--no-alignment`

### Issue: "Out of memory"

Reduce batch size:
```bash
python whisperx_transcribe.py --audio file.wav --batch-size 8
```

Or use a smaller model:
```bash
python whisperx_transcribe.py --audio file.wav --model medium
```

### Issue: "Audio preprocessing failed"

If librosa/soundfile aren't installed:
```bash
pip install librosa soundfile
```

Or skip preprocessing:
```bash
python whisperx_transcribe.py --audio file.wav --no-preprocess
```

### Issue: "Diarization requires HuggingFace token"

Get a free token:
1. Sign up at https://huggingface.co/
2. Go to https://huggingface.co/settings/tokens
3. Create a new token
4. Accept the pyannote model agreement at https://huggingface.co/pyannote/speaker-diarization

Then use:
```bash
python whisperx_transcribe.py --audio file.wav --diarize --hf-token YOUR_TOKEN
```

## Performance Tips

### GPU Acceleration

- **NVIDIA GPU**: ~10-20x faster than CPU
- **Apple Silicon (M1/M2/M3)**: ~5-10x faster than CPU
- **CPU**: Use smaller models for better speed

### Batch Size

Larger batch sizes are faster but use more memory:
- GPU with 8GB VRAM: `--batch-size 16` (default)
- GPU with 4GB VRAM: `--batch-size 8`
- CPU: `--batch-size 4`

### Model Selection

Processing speed (approximate for 1 hour of audio):
- `large-v3`: ~5-10 minutes (GPU), ~1-2 hours (CPU)
- `large-v2`: ~5-10 minutes (GPU), ~1-2 hours (CPU)
- `medium`: ~3-5 minutes (GPU), ~30-45 minutes (CPU)
- `base`: ~1-2 minutes (GPU), ~10-15 minutes (CPU)

Accuracy:
- `large-v3`, `large-v2`: Best accuracy for research
- `medium`: Good accuracy, faster
- `base`: Basic accuracy, fastest

## Best Practices for Research

1. **Use high-quality audio**: 16kHz or higher sample rate, minimal background noise
2. **Enable preprocessing**: Normalization and VAD reduce timing jitter
3. **Specify language**: Helps alignment accuracy
4. **Save as JSON**: Easiest format for programmatic analysis
5. **Filter by confidence**: Use `--min-confidence 0.7` for reliable words
6. **Document your setup**: Note model version, settings for reproducibility
7. **Validate results**: Spot-check timestamps against audio for critical research

## Additional Resources

- WhisperX GitHub: https://github.com/m-bain/whisperX
- Whisper Models: https://github.com/openai/whisper
- PyAnnote (for diarization): https://github.com/pyannote/pyannote-audio
- HuggingFace: https://huggingface.co/

## Summary

For research-grade word segmentation:
```bash
# Recommended command
python whisperx_transcribe.py \
  --audio session.wav \
  --model large-v3 \
  --language en \
  --format json
```

This provides:
- ✅ High accuracy transcription
- ✅ Stable word-level timestamps
- ✅ Confidence scores for each word
- ✅ Reproducible results for research

If you need reproducible timing for studies or quantitative analysis, **WhisperX's forced alignment is the safer choice**.
