# WhisperX Quick Reference

One-page reference for WhisperX commands and options.

## Installation

```bash
pip install whisperx
# or
pip install -r requirements.txt
```

## Basic Commands

### Transcribe Audio
```bash
python whisperx_transcribe.py --audio file.wav
```

### Specify Model
```bash
python whisperx_transcribe.py --audio file.wav --model large-v3
```

### Specify Language
```bash
python whisperx_transcribe.py --audio file.wav --language en
```

### All Output Formats
```bash
python whisperx_transcribe.py --audio file.wav --format all
```

### With Diarization
```bash
python whisperx_transcribe.py --audio file.wav --diarize --hf-token TOKEN
```

## Common Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--audio` | path | required | Input audio file |
| `--model` | tiny, base, small, medium, large, large-v2, large-v3 | large-v3 | Whisper model |
| `--language` | en, es, fr, de, etc. | auto | Language code |
| `--output` | path | auto | Output file path |
| `--format` | json, txt, srt, all | json | Output format |
| `--batch-size` | 1-32 | 16 | Batch size for inference |
| `--device` | cuda, cpu, mps | auto | Compute device |
| `--no-preprocess` | flag | - | Skip audio preprocessing |
| `--no-alignment` | flag | - | Skip forced alignment |
| `--diarize` | flag | - | Enable speaker diarization |
| `--hf-token` | string | - | HuggingFace token |

## Model Comparison

| Model | Size | Accuracy | Speed (GPU) | Speed (CPU) | Best For |
|-------|------|----------|-------------|-------------|----------|
| large-v3 | ~3GB | ⭐⭐⭐⭐⭐ | Fast | Slow | Research, English |
| large-v2 | ~3GB | ⭐⭐⭐⭐⭐ | Fast | Slow | Research, Multilingual |
| medium | ~1.5GB | ⭐⭐⭐⭐ | Faster | Medium | Good balance |
| base | ~150MB | ⭐⭐⭐ | Fastest | Fast | Quick tests |

## Output Format

### JSON Structure
```json
{
  "segments": [
    {
      "start": 0.0,
      "end": 2.5,
      "text": "hello world",
      "words": [
        {
          "word": "hello",
          "start": 0.12,
          "end": 0.45,
          "score": 0.98
        }
      ]
    }
  ],
  "language": "en"
}
```

### Key Fields
- `start`, `end` - Timestamps in seconds
- `word` - Transcribed text
- `score` - Confidence (0.0-1.0)
- `speaker` - Speaker ID (if diarization enabled)

## Confidence Scores

| Score | Quality | Action |
|-------|---------|--------|
| > 0.9 | Excellent | Use directly |
| 0.7-0.9 | Good | Use with confidence |
| 0.5-0.7 | Fair | Review manually |
| < 0.5 | Poor | Consider filtering |

## Complete Workflow

```bash
# 1. Record
python continuous_data_collector.py --duration 300 --session my_session

# 2. Transcribe with WhisperX
python whisperx_transcribe.py \
  --audio ../data/continuous/my_session.wav \
  --model large-v3 \
  --language en

# 3. Align with sensor data
python align_voice_labels.py \
  --session my_session \
  --whisper ../data/continuous/my_session_whisperx.json \
  --min-confidence 0.7

# 4. Review
cat ../data/continuous/my_session_whisperx_summary.txt
head ../data/continuous/my_session_labels.csv
```

## Performance Tips

### GPU (Recommended)
```bash
python whisperx_transcribe.py --audio file.wav --batch-size 16
```

### CPU (Use smaller model)
```bash
python whisperx_transcribe.py --audio file.wav --model medium --batch-size 4
```

### Out of Memory
```bash
python whisperx_transcribe.py --audio file.wav --batch-size 4
```

### Slow Processing
```bash
python whisperx_transcribe.py --audio file.wav --model medium
```

## Audio Preprocessing

### Automatic (Recommended)
```bash
python whisperx_transcribe.py --audio file.wav
```
- Normalizes to 16kHz mono
- Applies VAD to trim silence
- Normalizes volume

### Skip Preprocessing
```bash
python whisperx_transcribe.py --audio file.wav --no-preprocess
```

### Manual Preprocessing
```bash
ffmpeg -i input.mp3 -ar 16000 -ac 1 -af loudnorm output.wav
python whisperx_transcribe.py --audio output.wav --no-preprocess
```

## Common Issues

### WhisperX not installed
```bash
pip install whisperx
```

### No GPU available
Use CPU mode (slower):
```bash
python whisperx_transcribe.py --audio file.wav --device cpu --model medium
```

### Alignment failed
Specify language:
```bash
python whisperx_transcribe.py --audio file.wav --language en
```

### Audio format error
Convert to WAV:
```bash
ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav
```

### Out of memory
Reduce batch size:
```bash
python whisperx_transcribe.py --audio file.wav --batch-size 4
```

## Batch Processing

Process multiple files:
```bash
for file in *.wav; do
    python whisperx_transcribe.py --audio "$file" --model large-v3
done
```

With parallel processing:
```bash
ls *.wav | parallel -j 2 python whisperx_transcribe.py --audio {} --model large-v3
```

## Research Best Practices

1. **Model**: Use `large-v3` or `large-v2`
2. **Language**: Always specify with `--language en`
3. **Format**: Save as `json` for analysis
4. **Preprocessing**: Enable (default) for normalization
5. **Confidence**: Filter >= 0.7 in post-processing
6. **Documentation**: Record all settings for reproducibility

## Example Commands

### Research-Grade Transcription
```bash
python whisperx_transcribe.py \
  --audio session.wav \
  --model large-v3 \
  --language en \
  --format json
```

### With Speaker Diarization
```bash
python whisperx_transcribe.py \
  --audio interview.wav \
  --model large-v3 \
  --diarize \
  --hf-token hf_xxxxxxxxxxxx
```

### Fast Processing
```bash
python whisperx_transcribe.py \
  --audio file.wav \
  --model medium \
  --no-preprocess
```

### All Outputs
```bash
python whisperx_transcribe.py \
  --audio session.wav \
  --model large-v3 \
  --format all
```

## Device Selection

| Device | Command | Speed | Requirements |
|--------|---------|-------|--------------|
| CUDA GPU | `--device cuda` | Fastest | NVIDIA GPU, CUDA |
| Apple Silicon | `--device mps` | Fast | M1/M2/M3 Mac |
| CPU | `--device cpu` | Slowest | Any CPU |
| Auto | (default) | - | Detects best available |

## Links

- WhisperX: https://github.com/m-bain/whisperX
- Whisper: https://github.com/openai/whisper
- Full Guide: `docs/WHISPERX_GUIDE.md`
- Examples: `docs/WHISPERX_EXAMPLE.md`
- HuggingFace: https://huggingface.co/settings/tokens

## Summary

**For research-grade word segmentation:**
```bash
python whisperx_transcribe.py --audio file.wav --model large-v3 --language en
```

**For quick tests:**
```bash
python whisperx_transcribe.py --audio file.wav --model medium
```

**For production:**
```bash
python whisperx_transcribe.py --audio file.wav --model large-v3 --format all
```

WhisperX provides **best-in-class word timing accuracy** with forced alignment—the safer choice for reproducible research timing.
