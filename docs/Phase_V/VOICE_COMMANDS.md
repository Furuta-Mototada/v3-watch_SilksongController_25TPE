# Voice Commands for Data Collection

## Overview

The Phase V continuous data collector uses **voice commands** instead of keyboard shortcuts to mark gestures during recording. This approach offers several advantages:

### Why Voice Commands?

1. **Ergonomics**: No need to reach for keyboard while performing gestures
2. **Natural Motion**: Keyboard interaction could affect sensor readings and pollute data
3. **Hands-Free**: Focus on performing gestures naturally without interruption
4. **Real-time**: Speak commands as you perform gestures

## Technology Stack

The voice command system uses:

- **OpenAI Whisper**: State-of-the-art speech recognition model
- **sounddevice**: Real-time audio capture
- **Threading**: Non-blocking voice processing

## System Requirements

### Audio Hardware
- Working microphone (built-in or external)
- Recommended: Headset microphone for better recognition

### Software Dependencies

**Linux**:
```bash
sudo apt-get install portaudio19-dev
pip install openai-whisper sounddevice
```

**macOS**:
```bash
brew install portaudio
pip install openai-whisper sounddevice
```

**Windows**:
```bash
# PortAudio usually included with sounddevice
pip install openai-whisper sounddevice
```

## Voice Commands

### Gesture Commands

Speak these words clearly to mark gestures:

| Command | Gesture | Duration | Example Phrase |
|---------|---------|----------|----------------|
| "jump" | Jump | 0.3s | "jump", "jump now" |
| "punch" | Punch | 0.3s | "punch", "I'm punching" |
| "turn" | Turn | 0.5s | "turn", "turning around" |
| "noise" | Noise | 1.0s | "noise", "this is noise" |

### Control Commands

| Command | Action | Notes |
|---------|--------|-------|
| "quit" | Stop recording | Also: "stop", "exit" |
| "save" | Save immediately | Recording continues |

### Default Behavior

- If no command is spoken, the system automatically labels the time as **"walk"**
- Walk is the default state during continuous motion

## Usage Guide

### Starting a Recording Session

1. **Start the collector**:
```bash
cd src
python continuous_data_collector.py --duration 600
```

2. **Wait for Whisper to load** (takes ~5-10 seconds first time)

3. **Test your microphone** by speaking clearly

4. **Press Enter** when ready to begin recording

### During Recording

**Best Practices**:

1. **Speak clearly** but naturally - don't shout or whisper
2. **Time your commands** - speak RIGHT when you start the gesture
3. **Keep speaking distance consistent** - about 1-2 feet from microphone
4. **Minimize background noise** - recording in quiet environment helps
5. **Don't over-think it** - natural speech patterns work best

**Example Session Flow**:
```
[Start recording]
[Perform walking motion for 10 seconds]
[Start jump gesture] → Say "jump"
[Continue walking for 15 seconds]
[Start punch gesture] → Say "punch"
[Continue walking for 20 seconds]
[Start turn gesture] → Say "turn"
... continue naturally ...
```

### Troubleshooting

#### Command Not Recognized

**Symptoms**: You speak but nothing happens

**Causes & Solutions**:
- **Too quiet**: Speak louder or move closer to microphone
- **Background noise**: Reduce ambient sound
- **Accent/pronunciation**: Try clearer enunciation
- **Wrong word**: Use exact keywords (jump, punch, turn, noise)

#### Delayed Recognition

**Symptoms**: Command registers 1-2 seconds late

**Causes & Solutions**:
- **Normal behavior**: Whisper processes in 0.5s intervals
- **CPU load**: Close other applications
- **Model size**: System uses "base" model for speed/accuracy balance

#### False Positives

**Symptoms**: Random words trigger gestures

**Causes & Solutions**:
- **Similar words**: Avoid saying trigger words in conversation
- **Background speech**: Mute microphone during breaks
- **TV/radio**: Turn off media during recording

## Technical Details

### Audio Processing Pipeline

```
Microphone → Audio Stream (16kHz) → Buffer (1.5s) → Whisper → Command Detection → Gesture Marking
```

### Processing Parameters

- **Sample Rate**: 16kHz (Whisper standard)
- **Buffer Duration**: 1.5 seconds
- **Processing Interval**: 0.5 seconds
- **Silence Threshold**: 0.01 (energy level)
- **Language**: English

### Whisper Model

The system uses the **"base"** Whisper model:

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| tiny | 39M | Fastest | Low |
| base | 74M | **Fast** | **Good** ✓ |
| small | 244M | Medium | Better |
| medium | 769M | Slow | Best |

**Why "base"?**
- Good balance of speed and accuracy
- Processes in <500ms on modern CPUs
- Sufficient for single-word commands
- Smaller memory footprint

### Command Detection Logic

```python
# Simple keyword matching in transcribed text
text = whisper.transcribe(audio)
if 'jump' in text:
    mark_gesture('jump')
elif 'punch' in text:
    mark_gesture('punch')
...
```

- Case-insensitive matching
- Partial word matching (e.g., "jumping" → "jump")
- First match wins (if multiple keywords)

## Performance Considerations

### CPU Usage

- **Whisper model**: ~30-40% of one CPU core
- **Audio capture**: <5% CPU
- **Total impact**: Minimal on modern systems (4+ cores)

### Latency

- **Audio buffer**: 0-1.5 seconds
- **Whisper processing**: 0.2-0.5 seconds
- **Total delay**: 0.5-2 seconds typical

### Memory

- **Whisper base model**: ~300MB RAM
- **Audio buffer**: <5MB
- **Total overhead**: ~350MB

## Alternatives Considered

### Why not keyboard shortcuts?

**Original concern** (from user):
> "Keyboard is so far away, could pollute data collection"

**Issues with keyboard**:
- Requires reaching away from natural motion
- Hand movement to keyboard affects sensor readings
- Breaks flow of continuous motion
- Requires visual attention to find keys

### Why not gesture detection?

**Chicken-and-egg problem**:
- Need labeled data to train gesture detector
- Can't use detector to label training data
- Voice commands solve the bootstrapping problem

### Why not post-recording labeling?

**Timing challenges**:
- Hard to remember exact timing after the fact
- Video review is time-consuming
- Manual timestamp marking is error-prone
- Real-time marking more accurate

## Future Improvements

### Potential Enhancements

1. **Custom wake word**: "Hey Silksong, mark jump"
2. **Confidence thresholds**: Require high recognition confidence
3. **Visual feedback**: Show recognized commands on screen
4. **Audio feedback**: Beep confirmation when command recognized
5. **Multi-language**: Support other languages beyond English

### Advanced Features

1. **Gesture counting**: "That's 5 jumps"
2. **Session summary**: "You did 15 jumps today"
3. **Real-time tips**: "Try more punches"
4. **Quality checks**: "That didn't look like a jump"

## FAQ

**Q: Do I need internet for voice commands?**  
A: No, Whisper runs entirely locally.

**Q: Can I use in noisy environments?**  
A: It works, but quiet environments give better results.

**Q: What if I have a strong accent?**  
A: Whisper is trained on diverse accents. Simple words like "jump" should work fine.

**Q: Can I customize the command words?**  
A: Currently no, but it's a planned feature. For now, use: jump, punch, turn, noise.

**Q: Does it work offline?**  
A: Yes, completely offline after initial model download.

**Q: How much disk space does Whisper need?**  
A: ~140MB for the base model.

## Related Documentation

- [Phase V Data Collection Guide](DATA_COLLECTION.md)
- [Phase V Quick Start](QUICK_START.md)
- [CNN/LSTM Architecture](CNN_LSTM_ARCHITECTURE.md)

---

**Status**: ✅ Implemented and tested  
**Version**: Phase V  
**Last Updated**: October 2025
