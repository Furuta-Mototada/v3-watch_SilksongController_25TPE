# Phase V Data Collection Guide - Voice Commands + Post-Processing

## Overview

This guide provides **specific, step-by-step instructions** for collecting natural gesture data while playing Hollow Knight: Silksong. The system records sensor data and audio simultaneously, then uses Whisper post-processing to align voice commands with IMU data.

## System Requirements

### Hardware
- Pixel Watch with sensor streaming app
- Computer with microphone (M2 Air 8GB confirmed working)
- Whisper Large V3 Turbo model installed locally

### Software
```bash
# Install dependencies for data collector
pip install sounddevice numpy

# Install PortAudio
sudo apt-get install portaudio19-dev  # Linux
brew install portaudio                # macOS

# Install Whisper locally (for post-processing)
pip install openai-whisper
```

## Workflow Overview

```
1. Start Data Collector → Records sensor data + audio
2. Play Hollow Knight: Silksong → Speak commands naturally while playing
3. Recording Ends → Audio and sensor data saved
4. Run Whisper → Transcribe audio with word-level timestamps
5. Run Alignment Script → Map voice commands to sensor data
6. Review Labels → Validate and use for training
```

---

## Step 1: Preparation

### Before Recording

1. **Launch Hollow Knight: Silksong** on your gaming device
2. **Position yourself** comfortably with microphone 1-2 feet away
3. **Start watch sensor streaming** (ensure data is flowing)
4. **Test microphone** - speak a few words and verify it's working

### Mental Preparation

- You'll be speaking **naturally** as you play
- Don't overthink - react to the game naturally
- Speak commands **RIGHT WHEN** you perform the gesture
- It's okay to be slightly early or late - post-processing will handle it

---

## Step 2: Start Recording

```bash
cd src
python continuous_data_collector.py --duration 600 --session gameplay_session_01
```

**What happens:**
- Terminal displays instructions
- Press [Enter] to start countdown
- 3-second countdown begins
- Recording starts (sensor + audio)

**Recording Duration:**
- Recommended: **5-10 minutes per session**
- Minimum: **3 minutes** (for useful data)
- Maximum: **15 minutes** (longer gets tiring)

---

## Step 3: Data Collection - The Natural Way

### Starting the Session

**As soon as recording starts:**

1. Say **"walk start"** clearly
2. Begin moving naturally (walking in place or moving around)
3. Start playing Hollow Knight: Silksong

### During Gameplay - Speak Commands Naturally

| Game Action | What You Do | What You Say | Timing |
|-------------|-------------|--------------|--------|
| Walking in game | Walk naturally | Nothing (or "walk") | Default state |
| Standing still | Stop walking, stand still | **"idle"**, **"rest"**, or **"stop"** | When stationary |
| Hornet jumps | Perform jump gesture | **"jump"** | Right as you gesture |
| Hornet attacks | Perform punch gesture | **"punch"** | Right as you gesture |
| Hornet turns around | Perform turn gesture | **"turn"** | Right as you gesture |
| Adjusting watch, scratching | Any non-game motion | **"noise"** | During the motion |

### Natural Speaking Examples

**Good (Natural):**
```
"jump" - [perform jump]
"punch punch" - [rapid attacks]
"turn" - [turning around]
"idle" - [standing still]
"rest" - [standing, preparing]
"stop" - [pause movement]
"jump oh no" - [jump while reacting]
"punch jump punch" - [combo attack]
"noise" - [adjusting watch]
"walk" - [just walking]
```

**Also Good (Conversational):**
```
"I'm gonna jump here" - [jump gesture]
"punching this enemy" - [punch gesture]
"turning around" - [turn gesture]
"let me walk over there" - [walking]
```

The post-processing script detects keywords, so natural speech is fine!

### Important Rules

1. **Say "walk start" at the beginning** - Marks the start of walking
2. **Say "walk" occasionally** - Every 20-30 seconds during walking segments
3. **Don't say commands unless performing gesture** - Voice must match action
4. **Speak clearly but naturally** - No need to shout or enunciate perfectly
5. **Match your gestures to game timing** - React to the game naturally

### What NOT to Do

❌ **Don't** speak commands without performing gestures
❌ **Don't** perform gestures without speaking
❌ **Don't** overthink timing - be natural
❌ **Don't** stop mid-session - keep playing naturally
❌ **Don't** worry about mistakes - variety is good!

### Walking Segments & State Management

**Question:** Should I say "walk" multiple times or just once at the start?

**Answer:** **Just say "walk start" at the beginning!**
- Say **"walk start"** at the very beginning
- **All gaps between gestures are automatically labeled as "walk"**
- You don't need to keep saying "walk" - it's the default state!
- Optional: Say "walk" occasionally if you want to reinforce walking state explicitly

**Question:** What if I want to mark standing still (not walking)?

**Answer:** **Use "idle", "rest", or "stop" to mark standing still!**
- Say **"idle"** when you stop moving and stand still (2-second duration)
- Say **"rest"** as an alternative to idle (2-second duration)
- Say **"stop"** when you pause or stop moving (2-second duration)
- These create a standing-still state separate from walking
- Use these when you're actually standing still, not walking in place

**Example - Simple (Recommended):**
```
[Recording starts]
"walk start" [begin walking]
[walk for 10 seconds - automatic, no need to speak]
"jump" [jump gesture]
[walk for 5 seconds - automatic]
"punch" [punch gesture]
[walk for 8 seconds - automatic]
"turn" [turn gesture]
...
```

**Example - With Precision (Using Idle State):**
```
[Recording starts]
"walk start" [begin walking]
[walk for 10 seconds - automatic]
"idle" [stop walking, stand still for 2 seconds]
"jump" [precise jump from standing]
[walk resumes automatically]
"punch" [punch while walking]
[walk continues]
"rest" [stop, prepare for combo]
"jump punch turn" [precise combo from standing]
...
```

**Available Commands:**
- **Quick Gestures**: `jump` (0.3s), `punch` (0.3s), `turn` (0.5s)
- **States**: `walk` (default/auto-fill), `idle` (2.0s), `rest` (2.0s), `stop` (2.0s)
- **Other**: `noise` (1.0s for non-game movements like adjusting watch)

---

## Step 4: Ending the Session

### Normal End
- Recording automatically stops after the specified duration
- Audio and sensor data saved automatically

### Early Stop
- Press **Ctrl+C** to stop early
- Choose 'y' to save partial recording
- Minimum 2-3 minutes recommended

---

## Step 5: Post-Processing with Whisper

### Run Whisper Transcription

```bash
# Navigate to the data directory
cd data/continuous

# Run Whisper with word-level timestamps
whisper session_gameplay_01.wav \
  --model large-v3-turbo \
  --word_timestamps True \
  --output_format json \
  --output_dir .
```

**What this does:**
- Transcribes the audio file
- Generates word-level timestamps
- Saves output as JSON
- Takes 2-5 minutes depending on audio length

**Output:** `session_gameplay_01.json`

### Verify Transcription

```bash
# Check the JSON file
less session_gameplay_01.json
```

**Look for:**
- `"segments"` array
- `"words"` array within segments
- Each word has `"word"`, `"start"`, `"end"`, `"probability"`

---

## Step 6: Align Voice Commands with Sensor Data

```bash
cd ../../src

python align_voice_labels.py \
  --session session_gameplay_01 \
  --whisper ../data/continuous/session_gameplay_01.json \
  --min-confidence 0.6
```

**What this does:**
- Loads Whisper transcription with timestamps
- Extracts gesture keywords (jump, punch, turn, noise, walk)
- Aligns commands with sensor data timestamps
- Fills gaps with default "walk" state
- Generates `session_gameplay_01_labels.csv`

**Parameters:**
- `--session`: Your session name
- `--whisper`: Path to Whisper JSON output
- `--min-confidence`: Minimum word confidence (0.5-1.0, default 0.6)

---

## Step 7: Review and Validate

### Check the Labels CSV

```bash
cd ../data/continuous
head -20 session_gameplay_01_labels.csv
```

**Expected format:**
```csv
timestamp,gesture,duration
0.0,walk,15.2
15.2,jump,0.3
15.5,walk,12.1
27.6,punch,0.3
...
```

### Review Statistics

The alignment script outputs:
```
Gesture Distribution:
  walk    : 387.2s (64.5%)
  jump    :  18 events, 5.4s total
  punch   :  24 events, 7.2s total
  turn    :   8 events, 4.0s total
  noise   :   6 events, 6.0s total
```

**Good indicators:**
- Walk: 60-75% of total time ✓
- Jump/Punch: 10-25 events per 10 minutes ✓
- Turn: 5-15 events per 10 minutes ✓
- Noise: 5-10 events per 10 minutes ✓

### Visualize (Optional)

Create a simple visualization:

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load labels
labels = pd.read_csv('session_gameplay_01_labels.csv')

# Plot gesture timeline
fig, ax = plt.subplots(figsize=(15, 3))
colors = {'walk': 'blue', 'jump': 'green', 'punch': 'red', 'turn': 'orange', 'noise': 'gray'}

for _, row in labels.iterrows():
    ax.barh(0, row['duration'], left=row['timestamp'],
            color=colors[row['gesture']], height=0.5)

ax.set_xlabel('Time (seconds)')
ax.set_title('Gesture Timeline')
plt.show()
```

---

## Troubleshooting

### Issue: Whisper doesn't detect words

**Causes:**
- Microphone volume too low
- Too much background noise
- Speaking too quietly

**Solutions:**
- Test microphone before recording
- Speak slightly louder (but naturally)
- Record in quieter environment

### Issue: Commands misaligned with gestures

**Causes:**
- Speaking too early/late
- Microphone latency
- Timing drift

**Solutions:**
- Practice a test session first
- Speak RIGHT as you gesture
- Check microphone latency settings
- Adjust `--min-confidence` parameter

### Issue: Too many "walk" labels

**Causes:**
- Not saying gesture commands during actions
- Speaking "walk" too frequently

**Solutions:**
- Say gesture commands reliably
- Only say "walk" at start and occasionally (20-30s)
- Default state is walk - no need to over-label

### Issue: Missing gesture commands

**Causes:**
- Whisper confidence too low
- Speaking unclear
- Background noise

**Solutions:**
- Lower `--min-confidence` to 0.5 or 0.4
- Speak more clearly
- Review Whisper JSON to see what was detected

---

## Best Practices for Natural Data

### Do's ✓
- Play the game naturally
- React to gameplay with gestures
- Speak commands as you perform them
- Vary your speed and intensity
- Include mistakes and corrections
- Walk between gestures naturally
- Take short breaks if tired

### Don'ts ✗
- Don't perform gestures robotically
- Don't overthink timing
- Don't try to be perfect
- Don't record when exhausted
- Don't skip the "walk start" command
- Don't record in very noisy environments

---

## Session Planning

### Recommended Session Structure

**Session 1-3: Learning** (5 minutes each)
- Focus on clean, clear commands
- Moderate gameplay speed
- Build muscle memory

**Session 4-7: Natural Gameplay** (7-10 minutes each)
- Play normally, react naturally
- Vary speed and intensity
- Include combat and exploration

**Session 8-10: Challenging Scenarios** (5-7 minutes each)
- Rapid combat sequences
- Complex movement patterns
- Edge cases and transitions

### Total Data Target

**Minimum for Training:**
- 10 sessions × 5 minutes = **50 minutes**
- ~100 jumps, ~150 punches, ~50 turns

**Ideal for Production:**
- 15+ sessions × 7 minutes = **105 minutes**
- ~200+ jumps, ~300+ punches, ~100+ turns

---

## Quick Reference

### Recording Checklist
- [ ] Hollow Knight: Silksong launched
- [ ] Watch streaming sensor data
- [ ] Microphone tested and working
- [ ] `continuous_data_collector.py` ready
- [ ] Gaming setup comfortable

### During Recording
- [ ] Said "walk start" at beginning
- [ ] Speaking commands with gestures
- [ ] Playing naturally
- [ ] Saying "walk" occasionally

### After Recording
- [ ] Run Whisper on audio file
- [ ] Run alignment script
- [ ] Review labels CSV
- [ ] Check gesture distribution
- [ ] Validate timing if needed

---

## Summary

**The Natural Way:**
1. Start recording
2. Say "walk start"
3. Play Hollow Knight: Silksong naturally
4. Speak gesture commands as you perform them
5. Let it record fully
6. Post-process with Whisper
7. Align voice to sensor data
8. Review and validate

**Key Insight:** The system is designed for **natural, reactive gameplay**. Don't overthink it - play the game and speak naturally. The post-processing handles the complexity of alignment.

**Remember:** Variety and naturalness are MORE important than perfection!

---

**Next:** `POST_PROCESSING.md` - Advanced post-processing techniques and validation methods
