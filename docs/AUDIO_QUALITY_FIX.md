# Audio Quality Fix - "Underwater" Sound Resolved

## Problem

Voice recordings sounded "underwater" or like a telephone - muffled with missing high frequencies.

## Root Cause

The script was recording at **16kHz sample rate** which is too low for natural-sounding audio:
- 16kHz cuts off all frequencies above 8kHz
- Human speech has important harmonics up to 10-12kHz
- Result: Muffled, "telephone quality" sound

## Why Was It Set to 16kHz?

Whisper (the transcription AI) was trained on 16kHz audio, so the recommendation is to match that for best transcription accuracy. However, this creates poor listening quality.

## Solution

**Record at 44.1kHz (CD quality), then downsample to 16kHz for Whisper**

### What Changed

1. **Recording sample rate:** 16kHz → 44.1kHz
2. **Output files:** Now generates TWO audio files:
   - `session_name.wav` - 44.1kHz (sounds natural)
   - `session_name_16k.wav` - 16kHz (for Whisper transcription)

### Code Changes

**Before:**
```python
self.audio_sample_rate = 16000  # 16kHz for Whisper
```

**After:**
```python
self.audio_sample_rate = 44100  # 44.1kHz for quality audio
self.whisper_sample_rate = 16000  # Downsample to 16kHz for Whisper later
```

**Downsampling (using scipy):**
```python
from scipy import signal
downsample_factor = self.audio_sample_rate // self.whisper_sample_rate
audio_downsampled = signal.resample_poly(
    audio_array.flatten(),
    up=1,
    down=downsample_factor
)
```

## Installation (if scipy not installed)

```bash
# Activate your venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# Install scipy
pip install scipy
```

**Alternative (if scipy fails):**
The script will still save the 44.1kHz version. Use ffmpeg to downsample manually:
```bash
ffmpeg -i session_name.wav -ar 16000 session_name_16k.wav
```

## Usage

### Recording (Same as Before)
```bash
cd src
python continuous_data_collector.py --duration 600 --session game_01
```

### After Recording (Updated)

**OLD workflow:**
```bash
# Run Whisper on the main file
whisper session_game_01.wav --model large-v3-turbo
```

**NEW workflow:**
```bash
# Run Whisper on the 16kHz version
whisper session_game_01_16k.wav --model large-v3-turbo

# Listen to the 44.1kHz version if you want to hear quality audio
open session_game_01.wav
```

## Output Files Explained

After recording `game_01`, you'll have:

| File | Sample Rate | Purpose | Sound Quality |
|------|-------------|---------|---------------|
| `game_01.wav` | 44.1kHz | Playback, review | ✅ Natural, clear |
| `game_01_16k.wav` | 16kHz | Whisper transcription | ⚠️ Muffled (but accurate transcription) |
| `game_01.csv` | N/A | Sensor data | N/A |
| `game_01_metadata.json` | N/A | Session info | N/A |

## Benefits

✅ **Natural sound quality** - No more underwater effect
✅ **Better for review** - Listen back to verify your voice commands
✅ **Optimal Whisper accuracy** - 16kHz version matches Whisper's training data
✅ **Automatic conversion** - No manual steps needed

## Technical Details

### Sample Rate Comparison

| Sample Rate | Frequency Range | Sound Quality | Use Case |
|-------------|-----------------|---------------|----------|
| 8kHz | 0-4kHz | Telephone quality | Old phone calls |
| 16kHz | 0-8kHz | AM radio quality | Whisper, speech recognition |
| 22.05kHz | 0-11kHz | FM radio quality | Compressed audio |
| **44.1kHz** | 0-22kHz | **CD quality** | **Music, natural voice** |
| 48kHz | 0-24kHz | Professional audio | Video production |

**Human hearing:** 20Hz - 20kHz
**Speech fundamentals:** 85Hz - 500Hz
**Speech harmonics/clarity:** 500Hz - 12kHz ⚠️ Missing at 16kHz!

### Why 44.1kHz?

- Nyquist theorem: Sample rate must be 2× highest frequency
- Human hearing goes up to ~20kHz
- 44.1kHz captures up to 22.05kHz
- Standard for CD audio, well-supported everywhere
- Good balance of quality vs file size

### File Size Impact

**Per 10-minute recording:**
- 16kHz mono: ~19 MB
- 44.1kHz mono: ~53 MB
- **Extra storage:** ~34 MB per session

With 10 sessions for training:
- 16kHz only: 190 MB
- 44.1kHz + 16kHz: 720 MB
- Still very manageable on modern computers!

## Troubleshooting

### "scipy not installed" Warning

**Option 1: Install scipy**
```bash
pip install scipy
```

**Option 2: Use ffmpeg**
The script still saves 44.1kHz. Convert manually:
```bash
# Install ffmpeg (if not installed)
brew install ffmpeg  # macOS
# or download from https://ffmpeg.org/

# Convert to 16kHz
ffmpeg -i session_name.wav -ar 16000 session_name_16k.wav
```

### "Still sounds underwater"

1. Check which file you're playing:
   - `session_name.wav` should sound clear ✅
   - `session_name_16k.wav` will sound muffled (expected) ⚠️

2. Verify recording settings:
   ```bash
   # Check file info
   file session_name.wav
   # Should show: 44100 Hz

   ffprobe session_name.wav 2>&1 | grep Hz
   # Should show: 44100 Hz, mono
   ```

3. Test your microphone:
   ```bash
   # Record 5 seconds at 44.1kHz
   python -c "
   import sounddevice as sd
   import wave
   import numpy as np

   print('Recording 5s...')
   audio = sd.rec(int(5 * 44100), samplerate=44100, channels=1)
   sd.wait()

   with wave.open('test.wav', 'wb') as wf:
       wf.setnchannels(1)
       wf.setsampwidth(2)
       wf.setframerate(44100)
       audio_int16 = (audio * 32767).astype(np.int16)
       wf.writeframes(audio_int16.tobytes())
   print('Saved test.wav - play it back!')
   "

   # Play it
   open test.wav  # macOS
   # or
   aplay test.wav  # Linux
   ```

## Summary

**Before:** 🎤 → 16kHz recording → 📼 Sounds like you're underwater
**After:** 🎤 → 44.1kHz recording → 📼 Natural sound + 🔽 16kHz for Whisper

Your voice will now sound clear and natural when you play back recordings! The script automatically handles the downsampling for Whisper transcription. 🎉

---

**Files Modified:**
- `src/continuous_data_collector.py` - Updated audio recording and saving

**Dependencies:**
- `scipy` (optional but recommended for clean downsampling)
- Alternative: `ffmpeg` for manual conversion
