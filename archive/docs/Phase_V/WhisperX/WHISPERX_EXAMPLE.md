# WhisperX Usage Examples

This document provides practical examples for using WhisperX for research-grade word segmentation.

## Example 1: Basic Transcription

Transcribe a recorded session with default settings (large-v3 model):

```bash
cd src
python whisperx_transcribe.py --audio ../data/continuous/session_01.wav
```

**Output files:**
- `session_01_whisperx.json` - Full transcription with word-level timestamps
- `session_01_whisperx_summary.txt` - Human-readable summary

**Expected output:**
```
======================================================================
WhisperX Research-Grade Word Segmentation
======================================================================

Input audio: ../data/continuous/session_01.wav
Model: large-v3
Language: auto-detect

✓ Using CUDA GPU acceleration

🎵 Preprocessing audio...
  • Loaded audio: 120.50s @ 16000 Hz
  • VAD trimmed: 2.34s of silence
  • Normalized volume
✓ Preprocessed audio saved: ../data/continuous/preprocessed_session_01.wav

🤖 Loading WhisperX model...
  • Model: large-v3
  • Device: cuda
  • Compute type: float16
✓ Model loaded

📝 Transcribing audio...
✓ Transcription complete
  • Detected language: en
  • Segments: 45

🎯 Applying forced alignment...
  • Language: en
✓ Alignment complete
  • Word-level timestamps: 523 words

💾 Saving results...
✓ Saved JSON: ../data/continuous/session_01_whisperx.json
✓ Saved summary: ../data/continuous/session_01_whisperx_summary.txt

======================================================================
✅ WhisperX transcription complete!
======================================================================
```

## Example 2: Specify Language

For better alignment accuracy, specify the language:

```bash
python whisperx_transcribe.py \
  --audio session_02.wav \
  --language en
```

**Supported languages:** en, es, fr, de, it, pt, pl, tr, ru, nl, cs, ar, zh, ja, ko, and many more.

## Example 3: Use Different Model

Try `large-v2` for better multilingual support:

```bash
python whisperx_transcribe.py \
  --audio session_03.wav \
  --model large-v2 \
  --language es
```

**Available models:**
- `large-v3` - Latest, best English performance
- `large-v2` - Better multilingual support
- `medium` - Faster, good accuracy
- `base` - Fastest, basic accuracy

## Example 4: Enable Diarization

Add speaker labels if multiple speakers:

```bash
python whisperx_transcribe.py \
  --audio interview.wav \
  --model large-v3 \
  --diarize \
  --hf-token hf_xxxxxxxxxxxxxxxxxxxxx
```

**Prerequisites:**
1. Create HuggingFace account: https://huggingface.co/
2. Get token: https://huggingface.co/settings/tokens
3. Accept pyannote agreement: https://huggingface.co/pyannote/speaker-diarization

**Output includes speaker labels:**
```json
{
  "word": "hello",
  "start": 0.12,
  "end": 0.45,
  "score": 0.98,
  "speaker": "SPEAKER_00"
}
```

## Example 5: All Output Formats

Generate JSON, TXT, and SRT:

```bash
python whisperx_transcribe.py \
  --audio session_04.wav \
  --format all
```

**Outputs:**
- `session_04_whisperx.json` - Full data with word timestamps
- `session_04_whisperx.txt` - Plain text transcript
- `session_04_whisperx.srt` - Subtitle format
- `session_04_whisperx_summary.txt` - Summary

## Example 6: Skip Preprocessing

If audio is already optimized:

```bash
python whisperx_transcribe.py \
  --audio clean_audio.wav \
  --no-preprocess
```

## Example 7: CPU-Only Processing

For systems without GPU:

```bash
python whisperx_transcribe.py \
  --audio session_05.wav \
  --model medium \
  --batch-size 4 \
  --device cpu
```

**Performance tip:** Use `medium` or `base` model for faster CPU processing.

## Example 8: Complete Research Workflow

Full workflow from recording to analysis:

### Step 1: Record Session

```bash
cd src
python continuous_data_collector.py --duration 300 --session research_01
```

### Step 2: Transcribe with WhisperX

```bash
python whisperx_transcribe.py \
  --audio ../data/continuous/research_01.wav \
  --model large-v3 \
  --language en \
  --format json
```

### Step 3: Align with Sensor Data

```bash
python align_voice_labels.py \
  --session research_01 \
  --whisper ../data/continuous/research_01_whisperx.json \
  --min-confidence 0.7
```

### Step 4: Review Results

```bash
# Check summary
cat ../data/continuous/research_01_whisperx_summary.txt

# Check labels
head -30 ../data/continuous/research_01_labels.csv

# Check alignment metadata
cat ../data/continuous/research_01_alignment.json
```

## Example 9: Batch Processing

Process multiple files:

```bash
cd data/continuous
for file in session_*.wav; do
    python ../../src/whisperx_transcribe.py \
        --audio "$file" \
        --model large-v3 \
        --language en
done
```

## Example 10: Research-Grade Setup

Optimal settings for research papers and quantitative analysis:

```bash
python whisperx_transcribe.py \
  --audio research_session.wav \
  --model large-v3 \
  --language en \
  --batch-size 16 \
  --format all
```

Then filter by confidence:

```bash
python align_voice_labels.py \
  --session research_session \
  --whisper research_session_whisperx.json \
  --min-confidence 0.8
```

## Output Analysis Examples

### Example: Count Gesture Commands

```bash
# Using jq to analyze JSON
cat session_01_whisperx.json | jq '.segments[].words[] | select(.word | contains("jump")) | .start'
```

### Example: Extract High-Confidence Words

```python
import json

with open('session_01_whisperx.json') as f:
    data = json.load(f)

high_conf_words = []
for segment in data['segments']:
    for word in segment.get('words', []):
        if word.get('score', 0) > 0.9:
            high_conf_words.append({
                'word': word['word'],
                'start': word['start'],
                'confidence': word['score']
            })

print(f"High confidence words: {len(high_conf_words)}")
```

### Example: Visualize Timestamps

```python
import json
import matplotlib.pyplot as plt

with open('session_01_whisperx.json') as f:
    data = json.load(f)

# Extract gesture command timestamps
gestures = {'jump': [], 'punch': [], 'turn': []}

for segment in data['segments']:
    for word in segment.get('words', []):
        word_text = word['word'].strip().lower()
        if word_text in gestures:
            gestures[word_text].append(word['start'])

# Plot timeline
fig, ax = plt.subplots(figsize=(12, 4))
for i, (gesture, times) in enumerate(gestures.items()):
    ax.scatter(times, [i] * len(times), label=gesture, s=50)

ax.set_yticks(range(len(gestures)))
ax.set_yticklabels(gestures.keys())
ax.set_xlabel('Time (seconds)')
ax.set_title('Gesture Command Timeline')
ax.legend()
plt.tight_layout()
plt.savefig('gesture_timeline.png')
```

## Troubleshooting Examples

### Issue: Out of Memory

Reduce batch size:
```bash
python whisperx_transcribe.py --audio large_file.wav --batch-size 4
```

### Issue: Slow on CPU

Use smaller model:
```bash
python whisperx_transcribe.py --audio file.wav --model medium --device cpu
```

### Issue: Poor Alignment

Specify language explicitly:
```bash
python whisperx_transcribe.py --audio file.wav --language en
```

### Issue: Audio Format Not Supported

Convert first:
```bash
ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav
python whisperx_transcribe.py --audio output.wav
```

## Performance Benchmarks

Approximate processing times for 10 minutes of audio:

| Hardware | Model | Time |
|----------|-------|------|
| RTX 3090 (24GB) | large-v3 | ~1-2 min |
| RTX 3060 (12GB) | large-v3 | ~2-4 min |
| M2 Pro | large-v3 | ~3-5 min |
| M1 Air | medium | ~5-8 min |
| i7 CPU | medium | ~15-20 min |
| i7 CPU | large-v3 | ~40-60 min |

## Summary

Key recommendations:
1. **Use `large-v3`** for research-grade accuracy
2. **Specify language** with `--language en` for better alignment
3. **Enable preprocessing** (default) for audio normalization
4. **Filter by confidence** >= 0.7 in post-processing
5. **Save as JSON** for programmatic analysis
6. **Document settings** for reproducibility

For reproducible timing in research, **WhisperX's forced alignment is the best choice**.
