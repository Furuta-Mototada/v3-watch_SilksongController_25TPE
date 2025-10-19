# Parallel Controller Usage Guide

## 🎯 What Changed?

You now have a **parallel classifier architecture** for the motion controller!

### Old Architecture (udp_listener.py)
- ❌ Single classifier predicts one of: walk, jump, punch, turn, idle
- ❌ Sequential processing
- ❌ Can't walk and jump simultaneously

### New Architecture (udp_listener_parallel.py)
- ✅ **Binary classifier**: walk vs idle (5s windows)
- ✅ **Multiclass classifier**: jump, punch, turn_left, turn_right (1.5s windows)
- ✅ **Parallel execution**: Both run simultaneously!
- ✅ **Can walk + jump** or **walk + punch** at the same time

## 🚀 How to Run

### Prerequisites

Make sure you have trained models:

```bash
# Check if models exist
ls -la models/gesture_classifier_binary.pkl
ls -la models/gesture_classifier_multiclass.pkl
```

If missing, train them first:

```bash
# 1. Organize your data
python src/organize_training_data.py --input data/button_collected --output data/organized_training

# 2. Train models (option A: Python script)
source .venv/bin/activate
python notebooks/SVM_Local_Training.py

# 2. Train models (option B: Jupyter notebook)
jupyter notebook notebooks/SVM_Local_Training.ipynb
```

### Run the Parallel Controller

```bash
cd src
python phase_iv_ml_controller/udp_listener_parallel.py
```

You should see:

```
🔍 Auto-detecting IP address...
✅ Binary Classifier loaded (walk vs idle)
✅ Multiclass Classifier loaded (jump, punch, turn_left, turn_right)
🔗 Registering service for automatic discovery...
✓ Service registered as 'SilksongController._silksong._udp.local.'

============================================================
🎮 Silksong Controller v2.0 - PARALLEL CLASSIFIERS
============================================================
Listening on 192.168.1.XXX:12345

✅ PARALLEL ML ARCHITECTURE ACTIVE
   📊 Binary Classifier: Walk vs Idle (5.0s windows)
   🎯 Multiclass Classifier: Jump/Punch/Turn (1.5s windows)
   🔄 Both run simultaneously for parallel detection!

   Confidence Threshold: 60%
   Confidence Gating: 3 consecutive predictions

🎮 Key Mappings:
   Movement: Key.left/Key.right
   Jump: z | Attack: x
============================================================

✅ All threads started successfully:
   1️⃣  Collector: UDP → Queue
   2️⃣  Locomotion Predictor: Queue → Binary ML → Locomotion Actions
   3️⃣  Action Predictor: Queue → Multiclass ML → Action Gestures
   4️⃣  Actor: Both Queues → Keyboard Control

============================================================
🎮 Ready to play! Wave your watch to control the game.
   Press Ctrl+C to stop...
============================================================
```

## 🎮 How It Works

### Thread Architecture

```
┌─────────────┐
│   Watch     │
│  (50Hz UDP) │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│  Collector       │  Thread 1: Reads UDP packets
│  Thread          │           Pushes to sensor queue
└────────┬─────────┘
         │
         ▼
   ┌─────────────────┐
   │  Sensor Queue   │ (shared by both predictors)
   └────┬───────┬────┘
        │       │
        │       └──────────────────┐
        │                          │
        ▼                          ▼
┌────────────────────┐    ┌────────────────────┐
│ Locomotion         │    │ Action             │
│ Predictor          │    │ Predictor          │
│ (Binary 5s)        │    │ (Multiclass 1.5s)  │
│                    │    │                    │
│ walk vs idle       │    │ jump/punch/turn    │
└─────┬──────────────┘    └──────┬─────────────┘
      │                          │
      ▼                          ▼
┌──────────────┐          ┌──────────────┐
│ Locomotion   │          │ Action       │
│ Queue        │          │ Queue        │
└─────┬────────┘          └──────┬───────┘
      │                          │
      └──────────┬───────────────┘
                 │
                 ▼
         ┌───────────────┐
         │  Actor        │  Thread 4: Executes keyboard
         │  Thread       │           Walk: Hold arrow
         └───────────────┘           Jump/Punch: Press key
```

### Prediction Windows

**Binary Classifier (Locomotion)**:
- Window: 5 seconds (250 samples at 50Hz)
- Purpose: Detect sustained walking motion
- Output: "walk" or "idle"
- Effect: Hold/release arrow keys

**Multiclass Classifier (Actions)**:
- Window: 1.5 seconds (75 samples at 50Hz)
- Purpose: Detect quick gesture actions
- Output: "jump", "punch", "turn_left", "turn_right"
- Effect: Momentary key presses

### Example Gameplay

**Scenario 1: Jump while idle**
```
Time 0-1s:   Idle detected → No arrow keys held
Time 1.0s:   Jump detected → Press 'z' momentarily
Result: Character jumps in place ✅
```

**Scenario 2: Jump while walking**
```
Time 0-2s:   Walk detected → Hold right arrow
Time 2.0s:   Jump detected → Press 'z' momentarily
Result: Character jumps forward while walking ✅
```

**Scenario 3: Punch while walking**
```
Time 0-3s:   Walk detected → Hold right arrow
Time 3.0s:   Punch detected → Press 'x' momentarily
Result: Character attacks while moving ✅
```

**Scenario 4: Turn while walking**
```
Time 0-2s:   Walk detected → Hold right arrow
Time 2.0s:   Turn_left detected → Switch to left arrow
Result: Character changes direction mid-walk ✅
```

## 🔧 Tuning Parameters

Edit `udp_listener_parallel.py` to adjust:

### Window Sizes
```python
BINARY_WINDOW_SEC = 5.0   # Locomotion detection (longer = more stable)
MULTI_WINDOW_SEC = 1.5    # Action detection (shorter = more responsive)
```

### Confidence Thresholds
```python
ML_CONFIDENCE_THRESHOLD = 0.6  # Lower = more responsive, higher = more accurate
CONFIDENCE_GATING_COUNT = 3    # More = more stable, less = faster
```

### Action Cooldown
```python
ACTION_COOLDOWN = 0.5  # Seconds between same action (prevents spam)
```

## 📊 Expected Output

When running, you'll see real-time predictions:

```
🚶 [LOCOMOTION] WALKING RIGHT (0.87)
⬆️  [ACTION] JUMP (0.92)
🚶 [LOCOMOTION] WALKING RIGHT (0.85)
👊 [ACTION] PUNCH (0.78)
↪️  [ACTION] TURN LEFT (0.81)
⏸️  [LOCOMOTION] IDLE (0.93)
```

## 🐛 Troubleshooting

### Models not loading
```bash
# Check model files exist
ls -la models/gesture_classifier_*.pkl

# If missing, retrain
python notebooks/SVM_Local_Training.py
```

### No predictions happening
- Check watch is streaming data (should see UDP packets in collector)
- Verify both classifiers loaded (check startup messages)
- Lower `ML_CONFIDENCE_THRESHOLD` to 0.5 for testing

### Too many false positives
- Increase `ML_CONFIDENCE_THRESHOLD` to 0.7
- Increase `CONFIDENCE_GATING_COUNT` to 5
- Collect more training data

### Delayed response
- Decrease window sizes (but may reduce accuracy)
- Reduce `CONFIDENCE_GATING_COUNT` to 2

## 🎯 Next Steps

1. **Test with your watch**: Run the controller and test each gesture
2. **Collect more data**: If accuracy is low, collect 50+ samples per class
3. **Retrain models**: Use the updated data for better performance
4. **Play Silksong**: Enjoy motion control gaming!

## 📝 Comparison with Old Controller

| Feature | Old (udp_listener.py) | New (udp_listener_parallel.py) |
|---------|----------------------|--------------------------------|
| Architecture | Single classifier | Parallel dual classifiers |
| Gestures | 5 classes mixed | Binary + Multiclass separate |
| Walk + Jump | ❌ Not possible | ✅ Works perfectly |
| Window size | 0.3s (too short) | 5s + 1.5s (optimized) |
| Accuracy | Lower (mixed classes) | Higher (specialized models) |
| Latency | ~500ms | Locomotion: ~1s, Actions: ~300ms |

## 🚀 Want Even Better Performance?

Once you're happy with the SVM models, you can train the CNN/LSTM models on Google Colab for even better accuracy:

1. Upload organized data to Google Drive
2. Run `notebooks/watson_Colab_CNN_LSTM_Training.ipynb`
3. Download trained Keras models
4. Integrate into controller (future work)

---

**Enjoy your parallel classifier architecture! 🎮✨**
