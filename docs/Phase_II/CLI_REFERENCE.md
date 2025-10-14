# Data Collector CLI Reference

## Quick Command Examples

### 🎯 Collect Specific Gestures

```bash
# Collect only PUNCH
python data_collector.py --gestures punch

# Collect PUNCH and JUMP
python data_collector.py --gestures punch,jump

# Collect only WALK (test continuous mode)
python data_collector.py --gestures walk

# Collect TURN and NOISE
python data_collector.py --gestures turn,noise
```

### ⚙️ Custom Parameters

```bash
# Collect NOISE with 100 samples instead of 80
python data_collector.py --gestures noise --samples 100

# Collect PUNCH with 5-second recordings instead of 2.5s
python data_collector.py --gestures punch --duration 5.0

# Collect WALK with 5-minute continuous recording instead of 2.5min
python data_collector.py --gestures walk --continuous-duration 5.0
```

### 📁 Resume/Specific Session

```bash
# Resume an interrupted session
python data_collector.py --session-id 20251014_143052 --gestures turn

# Add more NOISE samples to existing session
python data_collector.py --session-id 20251014_143052 --gestures noise --samples 20
```

### ℹ️ Information

```bash
# List all available gestures and their modes
python data_collector.py --list-gestures

# See help and all options
python data_collector.py --help
```

## 📋 Available Gestures

| Gesture | Mode       | Stance  | Default Samples |
|---------|------------|---------|-----------------|
| punch   | Snippet    | combat  | 40 × 2.5s       |
| jump    | Snippet    | neutral | 40 × 2.5s       |
| turn    | Snippet    | travel  | 40 × 2.5s       |
| walk    | Continuous | travel  | 1 × 2.5min      |
| noise   | Snippet    | neutral | 80 × 2.5s       |

## 🎓 Common Workflows

### Incremental Collection (Recommended)

Collect gestures across multiple sessions to avoid fatigue:

```bash
# Day 1: Combat stance gestures
python data_collector.py --gestures punch

# Day 2: Neutral stance gestures
python data_collector.py --gestures jump,noise

# Day 3: Travel stance gestures
python data_collector.py --gestures turn,walk
```

### Test New Hardware/Setup

Quick validation with minimal samples:

```bash
# Test with just 5 samples each
python data_collector.py --gestures punch,jump --samples 5
```

### Focus on Specific Gesture

Deep dive into one gesture:

```bash
# Collect 100 PUNCH samples for extra robustness
python data_collector.py --gestures punch --samples 100
```

### Quick WALK Test

Test continuous recording mode:

```bash
# Short 1-minute WALK test
python data_collector.py --gestures walk --continuous-duration 1.0
```

## 🔧 Command-Line Arguments Reference

### `--gestures GESTURE1,GESTURE2`
**Type:** Comma-separated list
**Default:** All gestures
**Example:** `--gestures punch,jump,walk`

Specifies which gestures to collect. If omitted, all gestures will be collected in sequence.

### `--samples N`
**Type:** Integer
**Default:** 40
**Example:** `--samples 50`

Number of samples to collect for each gesture in snippet mode. Does not affect continuous mode (WALK).

### `--duration SEC`
**Type:** Float
**Default:** 2.5
**Example:** `--duration 3.0`

Recording duration in seconds for each sample in snippet mode. Useful if you need longer recordings to capture slower gestures.

### `--continuous-duration MIN`
**Type:** Float
**Default:** 2.5
**Example:** `--continuous-duration 5.0`

Recording duration in minutes for continuous mode gestures (WALK). Longer durations = more training data but more fatigue.

### `--session-id ID`
**Type:** String
**Default:** Auto-generated timestamp
**Example:** `--session-id 20251014_143052`

Use a specific session ID. Useful for:
- Resuming interrupted sessions
- Adding more samples to existing session
- Organizing related collection runs

### `--list-gestures`
**Type:** Flag (no value needed)
**Example:** `python data_collector.py --list-gestures`

Displays detailed information about all available gestures, their collection modes, and requirements. Script exits after displaying info.

## 💡 Pro Tips

### 1. Start Small
```bash
# Test with minimal samples first
python data_collector.py --gestures punch --samples 5
```

### 2. One Stance at a Time
```bash
# Combat stance only
python data_collector.py --gestures punch

# Neutral stance only
python data_collector.py --gestures jump,noise

# Travel stance only
python data_collector.py --gestures turn,walk
```

### 3. WALK Separately
Since WALK uses continuous mode and is quite different, collect it separately:
```bash
# Do all snippet gestures first
python data_collector.py --gestures punch,jump,turn,noise

# Then do WALK when you're ready for 2.5 minutes of continuous movement
python data_collector.py --gestures walk
```

### 4. Resume on Connection Issues
If your watch disconnects mid-session:
```bash
# Note your session ID from the console (e.g., 20251014_143052)
# Then resume with missing gestures
python data_collector.py --session-id 20251014_143052 --gestures turn,walk
```

### 5. Extra NOISE Samples
NOISE benefits from diversity:
```bash
# Collect extra NOISE samples on different days/conditions
python data_collector.py --gestures noise --samples 50
# Later, add more
python data_collector.py --gestures noise --samples 50
```

## 🚫 Common Mistakes

### ❌ Wrong: Space-separated gestures
```bash
python data_collector.py --gestures punch jump walk  # WRONG
```

### ✅ Correct: Comma-separated gestures
```bash
python data_collector.py --gestures punch,jump,walk  # CORRECT
```

### ❌ Wrong: Typo in gesture name
```bash
python data_collector.py --gestures punchh  # WRONG - will error
```

### ✅ Correct: Valid gesture names
```bash
python data_collector.py --list-gestures  # Check valid names first
python data_collector.py --gestures punch  # Use exact name
```

## 🎯 Output Structure

### Full Collection
```
training_data/session_20251014_143052/
├── punch_sample01.csv ... punch_sample40.csv
├── jump_sample01.csv ... jump_sample40.csv
├── turn_sample01.csv ... turn_sample40.csv
├── walk_continuous.csv
├── noise_sample01.csv ... noise_sample80.csv
└── session_metadata.json
```

### Partial Collection (e.g., `--gestures punch,walk`)
```
training_data/session_20251014_143052/
├── punch_sample01.csv ... punch_sample40.csv
├── walk_continuous.csv
└── session_metadata.json
```

## 📊 Time Estimates

| Command | Gestures | Approx. Time |
|---------|----------|--------------|
| `--gestures punch` | PUNCH | 15 min |
| `--gestures jump` | JUMP | 15 min |
| `--gestures turn` | TURN | 15 min |
| `--gestures walk` | WALK | 3 min |
| `--gestures noise` | NOISE | 30 min |
| `--gestures punch,jump` | PUNCH + JUMP | 30 min |
| `--gestures turn,walk` | TURN + WALK | 18 min |
| No arguments | ALL | 78 min |

Times include setup, breaks, and occasional retries.

## 🔍 Troubleshooting

### "Invalid gesture(s): xyz"
- Check spelling: gesture names are lowercase
- Use `--list-gestures` to see valid options

### "No gestures to collect!"
- You may have filtered out all gestures
- Check your `--gestures` argument

### Session ID not found
- Make sure the session directory exists in `training_data/`
- Session format: `YYYYMMDD_HHMMSS`

### Connection issues
- See main DATA_COLLECTION_GUIDE.md troubleshooting section
- Try collecting one gesture at a time to isolate issues

## 📚 Related Documentation

- **Full Guide:** `docs/Phase_II/DATA_COLLECTION_GUIDE.md`
- **Quick Start:** `docs/Phase_II/QUICK_START.md`
- **Hybrid Protocol:** `docs/Phase_II/HYBRID_COLLECTION_PROTOCOL.md`
- **Implementation:** `docs/Phase_II/IMPLEMENTATION_SUMMARY.md`

---

**TIP:** Start with `python data_collector.py --list-gestures` to familiarize yourself with options, then use `--gestures` to collect incrementally!
