# Session-Based Data Organization

## Overview

Data collection now uses **timestamp-prefixed session directories** to keep recordings organized and prevent file conflicts.

## Directory Structure

### Old Structure (Before)
```
data/continuous/
├── session_20251017_143022.wav
├── session_20251017_143022_16k.wav
├── session_20251017_143022.csv
├── session_20251017_143022_metadata.json
├── session_20251017_145533.wav
├── session_20251017_145533_16k.wav
├── session_20251017_145533.csv
├── session_20251017_145533_metadata.json
└── ... (gets messy with many files)
```

### New Structure (After)
```
data/continuous/
├── 20251017_143022_game_01/
│   ├── audio.wav              # 44.1kHz audio
│   ├── audio_16k.wav          # 16kHz for Whisper
│   ├── sensor_data.csv        # IMU data
│   ├── metadata.json          # Session info
│   └── README.md              # Documentation
├── 20251017_145533_game_02/
│   ├── audio.wav
│   ├── audio_16k.wav
│   ├── sensor_data.csv
│   ├── metadata.json
│   └── README.md
└── 20251017_150245_test/
    ├── audio.wav
    ├── audio_16k.wav
    ├── sensor_data.csv
    ├── metadata.json
    └── README.md
```

## Benefits

✅ **Organized by session** - Each recording in its own directory
✅ **Timestamp prefix** - Sessions automatically sorted chronologically
✅ **Clean filenames** - No redundant timestamps in each filename
✅ **Self-documenting** - Each session includes README.md
✅ **Easy to find** - Session names clearly visible
✅ **Batch operations** - Easy to process all files in a session

## Session Naming Convention

### Format
```
YYYYMMDD_HHMMSS_<session_name>
```

### Examples
```bash
# With custom session name:
python continuous_data_collector.py --duration 600 --session game_01
# Creates: 20251017_143022_game_01/

# Without custom name (auto-generated):
python continuous_data_collector.py --duration 600
# Creates: 20251017_143022_session/

# Another custom name:
python continuous_data_collector.py --duration 300 --session test_jump
# Creates: 20251017_150245_test_jump/
```

### Timestamp Components
- `YYYYMMDD` - Date (e.g., 20251017 = October 17, 2025)
- `HHMMSS` - Time (e.g., 143022 = 2:30:22 PM)
- `<session_name>` - Your custom name or "session" if not provided

## Files in Each Session

| Filename | Description | Sample Rate | Use For |
|----------|-------------|-------------|---------|
| `audio.wav` | High-quality audio | 44.1kHz | Playback, review, listening |
| `audio_16k.wav` | Downsampled audio | 16kHz | Whisper transcription |
| `sensor_data.csv` | IMU sensor data | ~50Hz | Model training |
| `metadata.json` | Session metadata | N/A | Reference, analysis |
| `README.md` | Documentation | N/A | Quick reference |

## Usage Examples

### Recording Sessions

```bash
cd src

# Session 1: Morning gameplay
python continuous_data_collector.py --duration 600 --session morning_gameplay
# Creates: data/continuous/20251017_090000_morning_gameplay/

# Session 2: Afternoon gameplay
python continuous_data_collector.py --duration 600 --session afternoon_gameplay
# Creates: data/continuous/20251017_143000_afternoon_gameplay/

# Session 3: Evening test
python continuous_data_collector.py --duration 300 --session evening_test
# Creates: data/continuous/20251017_190000_evening_test/
```

### Processing Sessions

```bash
# Navigate to a specific session
cd data/continuous/20251017_143000_afternoon_gameplay/

# Transcribe audio
whisper audio_16k.wav --model large-v3-turbo --word_timestamps True --output_format json

# Align voice with sensor data
cd ../../../src
python align_voice_labels.py \
  --session 20251017_143000_afternoon_gameplay \
  --whisper ../data/continuous/20251017_143000_afternoon_gameplay/audio_16k.json
```

### Batch Processing All Sessions

```bash
# List all sessions
ls -d data/continuous/*/

# Process all sessions with a script
for session in data/continuous/*/; do
    echo "Processing: $session"
    cd "$session"
    whisper audio_16k.wav --model large-v3-turbo --word_timestamps True --output_format json
    cd -
done
```

## Session README.md

Each session automatically includes a README.md with:
- Recording timestamp and duration
- File descriptions
- Next steps for processing
- Command examples for Whisper
- Quick reference guide

## Migration from Old Format

If you have old recordings (flat file structure), no action needed! They'll continue to work. New recordings automatically use the new structure.

### Converting Old Sessions (Optional)

```bash
# Create a migration script if needed
cd data/continuous

# Group old files by timestamp prefix
for timestamp in $(ls *.wav | sed 's/_.*//g' | sort -u); do
    mkdir -p "${timestamp}_migrated"
    mv ${timestamp}_* "${timestamp}_migrated/" 2>/dev/null || true
    # Rename files to new format
    cd "${timestamp}_migrated"
    for f in ${timestamp}_*; do
        new_name=$(echo "$f" | sed "s/${timestamp}_//")
        mv "$f" "$new_name" 2>/dev/null || true
    done
    cd ..
done
```

## Finding Sessions

### By Date
```bash
# All sessions from October 17, 2025
ls -d data/continuous/20251017_*/

# Sessions from afternoon (12:00-18:00)
ls -d data/continuous/202510**_1[2-7]*/
```

### By Name
```bash
# All "game" sessions
ls -d data/continuous/*_game_*/

# All "test" sessions
ls -d data/continuous/*_test*/
```

### Most Recent Session
```bash
# Get the latest session
ls -td data/continuous/*/ | head -1
```

## Tips for Session Management

### Naming Conventions

**Good session names:**
```bash
--session game_01          # Clear sequence
--session morning_test     # Time + purpose
--session jump_focused     # Specific gesture
--session fast_pace        # Recording characteristic
```

**Avoid:**
```bash
--session test            # Too generic
--session asdfg           # Meaningless
--session 2025-10-17      # Redundant (timestamp already included)
```

### Organizing Multiple Recording Days

```bash
data/continuous/
├── 20251017_*_game_01/    # Day 1 recordings
├── 20251017_*_game_02/
├── 20251017_*_game_03/
├── 20251018_*_game_04/    # Day 2 recordings
├── 20251018_*_game_05/
├── 20251019_*_test_01/    # Day 3 tests
└── 20251019_*_test_02/
```

### Grouping Sessions for Training

```bash
# Training set: First 8 sessions
data/continuous/202510**_*_game_{01..08}/

# Validation set: Sessions 9-10
data/continuous/202510**_*_game_{09,10}/

# Test set: All test sessions
data/continuous/202510**_*_test_*/
```

## Advantages Over Flat Structure

| Aspect | Old (Flat) | New (Organized) |
|--------|-----------|-----------------|
| **File count per session** | 4+ files | 1 directory (5 files inside) |
| **Finding specific session** | Search through 40+ files | Browse 10 directories |
| **Batch processing** | Complex wildcards | Simple directory iteration |
| **Documentation** | Separate docs | Built-in README per session |
| **File conflicts** | Possible with same timestamp | Impossible (unique directories) |
| **Cleanup** | Delete files individually | Delete one directory |

## Summary

**Old workflow:**
```bash
python continuous_data_collector.py --duration 600 --session game_01
# Creates multiple files in data/continuous/
```

**New workflow:**
```bash
python continuous_data_collector.py --duration 600 --session game_01
# Creates directory: data/continuous/20251017_143022_game_01/
# Contains: audio.wav, audio_16k.wav, sensor_data.csv, metadata.json, README.md
```

**Result:** Clean, organized, self-documenting data structure! 🎉

---

**Implementation:** This structure is now the default in `continuous_data_collector.py`
**Backward compatible:** Old flat files continue to work
**Migration:** Optional (old files work as-is)
