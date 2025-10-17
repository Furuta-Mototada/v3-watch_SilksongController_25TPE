# Data Organization Update - Session-Based Structure

## What Changed?

Your data collector now organizes recordings into **session directories with timestamp prefixes** instead of flat files.

## Quick Comparison

### Before
```bash
python continuous_data_collector.py --duration 600 --session game_01
```
**Created:**
```
data/continuous/
├── session_20251017_143022.wav
├── session_20251017_143022_16k.wav
├── session_20251017_143022.csv
└── session_20251017_143022_metadata.json
```

### After
```bash
python continuous_data_collector.py --duration 600 --session game_01
```
**Creates:**
```
data/continuous/20251017_143022_game_01/
├── audio.wav           # 44.1kHz (natural sound)
├── audio_16k.wav       # 16kHz (for Whisper)
├── sensor_data.csv     # IMU data
├── metadata.json       # Session info
└── README.md           # Session documentation
```

## Benefits

✅ **Cleaner organization** - One directory per session
✅ **Chronological sorting** - Timestamp prefix auto-sorts
✅ **Self-documenting** - Each session includes README
✅ **No file conflicts** - Each session in separate directory
✅ **Easy batch processing** - Process all files in a session together

## Usage

### Recording

```bash
cd src

# With custom name (recommended)
python continuous_data_collector.py --duration 600 --session game_01
# Creates: data/continuous/20251017_143022_game_01/

# Without name (auto-generated)
python continuous_data_collector.py --duration 600
# Creates: data/continuous/20251017_143022_session/
```

### Finding Sessions

```bash
# List all sessions
ls -d data/continuous/*/

# Most recent session
ls -td data/continuous/*/ | head -1

# Specific date (October 17)
ls -d data/continuous/20251017_*/

# By name pattern
ls -d data/continuous/*_game_*/
```

### Processing

```bash
# Navigate to session
cd data/continuous/20251017_143022_game_01/

# Transcribe (use the 16kHz version)
whisper audio_16k.wav --model large-v3-turbo --word_timestamps True --output_format json

# Align with sensor data
cd ../../../src
python align_voice_labels.py \
  --session 20251017_143022_game_01 \
  --whisper ../data/continuous/20251017_143022_game_01/audio_16k.json
```

## Session Directory Contents

Each session directory contains:

| File | Purpose |
|------|---------|
| `audio.wav` | High-quality audio (44.1kHz) for playback |
| `audio_16k.wav` | Downsampled audio (16kHz) for Whisper |
| `sensor_data.csv` | Raw IMU sensor data |
| `metadata.json` | Recording metadata |
| `README.md` | Session-specific documentation |

## Recommended Naming

**Good names:**
```bash
--session game_01        # Clear sequence
--session morning_test   # Time + purpose
--session jump_focused   # Specific gesture
```

**Avoid:**
```bash
--session test           # Too generic
--session 20251017       # Redundant (timestamp added automatically)
```

## Batch Recording Workflow

```bash
cd src

# Day 1: Main gameplay sessions
python continuous_data_collector.py --duration 600 --session game_01
python continuous_data_collector.py --duration 600 --session game_02
python continuous_data_collector.py --duration 600 --session game_03

# Day 1: Test sessions
python continuous_data_collector.py --duration 300 --session test_01
python continuous_data_collector.py --duration 300 --session test_02

# Result:
# data/continuous/
# ├── 20251017_090000_game_01/
# ├── 20251017_100500_game_02/
# ├── 20251017_110200_game_03/
# ├── 20251017_140000_test_01/
# └── 20251017_145000_test_02/
```

## Migration

**Old flat files:** Continue to work (no migration needed)
**New recordings:** Automatically use new structure
**Optional migration:** See `docs/Phase_V/SESSION_ORGANIZATION.md`

## Documentation

- **Full details:** `docs/Phase_V/SESSION_ORGANIZATION.md`
- **Audio quality fix:** `docs/AUDIO_QUALITY_FIX.md`
- **Session README:** Auto-generated in each session directory

## Summary

Your data collection is now more organized! 🎉

**What you need to know:**
1. Sessions are now in timestamped directories
2. Use `--session <name>` for custom names
3. Each session includes a README with instructions
4. Old flat files still work (backward compatible)

---

**Implementation:** Updated in `continuous_data_collector.py`
**Date:** October 17, 2025
