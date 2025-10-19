# Phase V Quick Start

Get up and running with CNN/LSTM gesture recognition in 4 steps.

## Prerequisites

- Python 3.8+
- Wear OS watch with sensor streaming app
- Both devices on same WiFi network

## Step 1: Install (5 minutes)

```bash
# Install all dependencies including TensorFlow
pip install -r requirements.txt
```

**Installation size**: ~500MB (TensorFlow is large)

## Step 2: Collect Data (60 minutes)

```bash
# Start data collector
cd src
python continuous_data_collector.py --duration 600
```

**During recording**:
1. Walk naturally around your space
2. Every 10-15 seconds, perform a gesture:
   - Press `j` right when you jump
   - Press `p` right when you punch
   - Press `t` right when you turn
   - Press `n` for random motion
3. Keep walking between gestures
4. Repeat for 10 minutes

**Repeat**: Do this 5-10 times (different sessions)

**Result**: Files in `data/continuous/`
- `session_*.csv` (sensor data)
- `session_*_labels.csv` (gesture labels)

## Step 3: Train Model (10-60 minutes)

```bash
# Open training notebook
jupyter notebook notebooks/Phase_V_Training.ipynb
```

**In the notebook**:
1. Edit the `SESSION_FILES` list:
   ```python
   SESSION_FILES = [
       ('session_20241016_120000.csv', 'session_20241016_120000_labels.csv'),
       ('session_20241016_121500.csv', 'session_20241016_121500_labels.csv'),
       # ... add all your sessions
   ]
   ```

2. Run all cells (Cell → Run All)

3. Wait for training to complete:
   - CPU: 1-2 hours
   - GPU: 10-20 minutes

4. Check final accuracy:
   - Should be >90% on test set
   - If lower, collect more data

**Result**: `models/cnn_lstm_gesture.h5` (trained model)

## Step 4: Test Real-Time (immediately)

```bash
# Start real-time gesture recognition
cd src
python udp_listener_v3.py
```

**What you'll see**:
```
✓ CNN/LSTM model loaded
✓ System ready!
Waiting for sensor data...

🚶 Walking right
🦘 JUMP (confidence: 0.94)
👊 PUNCH (confidence: 0.89)
🔄 TURN (confidence: 0.92)
```

**Performance**:
- Predictions every 20ms
- Actions execute when confidence >80%
- Much faster than Phase IV!

## Verification Checklist

- [ ] TensorFlow installed (`pip list | grep tensorflow`)
- [ ] Collected 5+ sessions of 10 minutes each
- [ ] Training accuracy >90%
- [ ] Test accuracy >85%
- [ ] Model file exists: `models/cnn_lstm_gesture.h5`
- [ ] Real-time predictions working
- [ ] Latency feels responsive (<100ms)

## Common Issues

### "TensorFlow not installed"
```bash
pip install tensorflow
# Or for M1/M2 Mac:
pip install tensorflow-macos tensorflow-metal
```

### "No data recorded"
- Make sure watch is streaming (toggle ON in app)
- Check both devices on same WiFi
- Verify IP in `config.json`

### "Training accuracy low"
- Collect more sessions (aim for 10+)
- Check label distribution is balanced
- Try collecting more gesture events per session

### "Model file not found"
- Make sure training completed successfully
- Check `models/` directory exists
- Verify notebook saved the model

## Tips for Best Results

1. **Data Quality**: Natural, varied gestures beat perfect repetitions
2. **Label Timing**: Press keys at gesture START, not during
3. **Transitions**: Walk between gestures for realistic flow
4. **Variety**: Different speeds, positions, orientations
5. **Balance**: Roughly equal amounts of each gesture

## Expected Timeline

| Task | Time |
|------|------|
| Install dependencies | 5 min |
| Collect 1 session | 10 min |
| Collect 10 sessions | 100 min |
| Train model (GPU) | 10-20 min |
| Train model (CPU) | 60-120 min |
| Test real-time | 5 min |
| **Total (GPU)** | **~2-3 hours** |
| **Total (CPU)** | **~3-4 hours** |

## What's Different from Phase IV?

| Aspect | Phase IV | Phase V |
|--------|----------|---------|
| Data collection | 40 isolated clips | Continuous recording |
| Feature engineering | Manual (60+ features) | Automatic (CNN) |
| Temporal awareness | None | LSTM memory |
| Inference speed | 300-500ms | 10-30ms ⚡ |
| Accuracy | 85-95% | 90-98% ✨ |
| Setup complexity | Simpler | More involved |

## Next Steps

1. ✅ Get Phase V working
2. 📊 Compare with Phase IV performance
3. 🎮 Test in actual Hollow Knight gameplay
4. 🔧 Fine-tune thresholds if needed
5. 📈 Collect more data to improve accuracy

## Need Help?

See detailed guides:
- `IMPLEMENTATION_GUIDE.md` - Complete documentation
- `DATA_COLLECTION.md` - Data collection best practices
- `CNN_LSTM_ARCHITECTURE.md` - Technical deep dive

---

**Ready to start?** Run the install command above! 🚀
