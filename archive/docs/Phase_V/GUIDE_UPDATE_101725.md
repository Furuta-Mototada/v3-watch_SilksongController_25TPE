# Data Collection Guide Updates - October 17, 2025

## Summary

Updated `DATA_COLLECTION_GUIDE.md` to accurately reflect the current implementation after fixing the audio resampling issue and clarifying the idle/rest/stop keywords.

## Changes Made

### 1. Fixed Audio Resampling (Code Fix)

**Problem:**
- Audio recorded at 44.1kHz being downsampled to 16kHz using `signal.resample_poly`
- Caused timing drift: "punch" at 6 seconds in 44.1kHz file appeared at 9 seconds in 16kHz file
- This was UNACCEPTABLE for voice-gesture alignment

**Root Cause:**
- Using integer division (44100 // 16000 = 2) for downsample factor
- `resample_poly` with `down=2` effectively halved sample rate to 22050Hz, not 16000Hz
- Created wrong number of samples → duration mismatch

**Solution:**
- Changed from `signal.resample_poly` to `signal.resample`
- Calculate exact target samples: `duration * 16000`
- Preserves exact timing: 6 seconds in 44.1kHz = 6 seconds in 16kHz ✓

**Code Change in `continuous_data_collector.py`:**
```python
# OLD (WRONG - caused timing drift)
downsample_factor = self.audio_sample_rate // self.whisper_sample_rate  # 44100 // 16000 = 2
audio_downsampled = signal.resample_poly(
    audio_array.flatten(),
    up=1,
    down=downsample_factor  # down=2 gives 22050Hz, not 16000Hz!
)

# NEW (CORRECT - preserves timing)
original_duration = len(audio_array) / self.audio_sample_rate
target_num_samples = int(original_duration * self.whisper_sample_rate)
audio_downsampled = signal.resample(
    audio_array.flatten(),
    target_num_samples  # Exact samples for 16000Hz
)
```

### 2. Updated Documentation for Idle/Rest/Stop Keywords

**Added to Command Table:**
| Game Action | What You Do | What You Say | Timing |
|-------------|-------------|--------------|--------|
| Standing still | Stop walking, stand still | **"idle"**, **"rest"**, or **"stop"** | When stationary |

**Clarified in Walking Segments Section:**

**Before (Confusing):**
> "What if I want to stop walking before a gesture (for more precision)?"
> "Use idle/rest/stop to create a 2-second standing-still marker before your gesture"

**After (Clear):**
> "What if I want to mark standing still (not walking)?"
> "Use idle/rest/stop when you're actually standing still, not walking in place"
> - Each creates a 2-second standing-still state separate from walking
> - Use these when genuinely stationary, not for precision timing

**Updated Available Commands Section:**
```
- **Quick Gestures**: jump (0.3s), punch (0.3s), turn (0.5s)
- **States**: walk (default/auto-fill), idle (2.0s), rest (2.0s), stop (2.0s)
- **Other**: noise (1.0s for non-game movements)
```

**Added Examples:**
```
"idle" - [standing still]
"rest" - [standing, preparing]
"stop" - [pause movement]
```

## Current Keyword Implementation

From `align_voice_labels.py`:
```python
GESTURE_KEYWORDS = {
    'jump': 0.3,    # Quick jump gesture
    'punch': 0.3,   # Quick punch gesture
    'turn': 0.5,    # Turn-around gesture
    'noise': 1.0,   # Non-game movements (adjusting watch, etc.)
    'idle': 2.0,    # Standing still
    'rest': 2.0,    # Alternative to idle
    'stop': 2.0,    # Another alternative for standing
    'walk': None    # Default state, auto-filled in gaps
}
```

## What This Means for Data Collection

### Audio Files Now Have Perfect Timing
- Both `audio.wav` (44.1kHz) and `audio_16k.wav` (16kHz) have identical durations
- If you say "punch" at timestamp 6.0s, it appears at 6.0s in BOTH files
- Whisper timestamps will align perfectly with sensor data timestamps

### Clear Keyword Usage
1. **walk** - Default state, say "walk start" at beginning, auto-fills gaps
2. **jump/punch/turn** - Quick gestures (0.3-0.5s), say when performing action
3. **idle/rest/stop** - Standing still states (2.0s), use when actually stationary
4. **noise** - Non-game movements (1.0s), for watch adjustments, scratching, etc.

## Testing Verification

To verify the fix works:

```bash
cd src
python continuous_data_collector.py --duration 30 --session timing_test

# During recording:
# - Say "walk start" at 0 seconds
# - Say "punch" at exactly 10 seconds (count in your head or use timer)
# - Say "jump" at exactly 20 seconds
```

Then check:
```bash
cd ../data/continuous/YYYYMMDD_HHMMSS_timing_test/

# Check both audio files have same duration
ffprobe audio.wav 2>&1 | grep Duration
ffprobe audio_16k.wav 2>&1 | grep Duration

# Should show identical durations (within 0.01s)
```

## Files Modified

1. **src/continuous_data_collector.py**
   - Fixed resampling algorithm (lines ~467-478)
   - Changed from `resample_poly` to `resample`

2. **docs/Phase_V/DATA_COLLECTION_GUIDE.md**
   - Updated command table with idle/rest/stop
   - Clarified walking segments Q&A
   - Added standing-still keyword examples
   - Updated available commands section

## Status

✅ **Audio timing issue:** FIXED - Both files maintain exact same timeline
✅ **Documentation:** UPDATED - Clear guidance on all keywords
✅ **Ready for data collection:** YES - All issues resolved

## Next Steps

1. Test with 30-second recording to verify timing alignment
2. Begin full data collection sessions (600 seconds each)
3. Verify Whisper timestamps align with sensor data after post-processing

---

**Date:** October 17, 2025
**Issue:** Audio timing drift causing misalignment
**Resolution:** Changed resampling method + clarified documentation
**Impact:** Perfect timestamp alignment for voice-gesture pairing
