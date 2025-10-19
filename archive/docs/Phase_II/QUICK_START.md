# Quick Start: Data Collection

A simplified guide to get started with IMU gesture data collection.

## Prerequisites Checklist

- [ ] Watch app installed and connected
- [ ] Python requirements installed (`pip install -r requirements.txt`)
- [ ] Clear space to move around
- [ ] 20-30 minutes available
- [ ] Watch charged (>50% battery recommended)

## 5-Minute Setup

### Step 1: Start Watch App
1. Open "Silksong Controller" on your watch
2. Wait for "Connected!" (green status)
3. Toggle "Stream" switch to ON
4. **Keep the watch screen awake** (tap periodically)

### Step 2: Close Other Scripts
```bash
# Make sure udp_listener.py is NOT running
# Press Ctrl+C in any terminal running it
```

### Step 3: Run Data Collector
```bash
cd /path/to/v3-watch_SilksongController_25TPE/src
python data_collector.py
```

### Step 4: Follow On-Screen Instructions
The script will guide you through:
1. **Connection check** - verify data is flowing
2. **Stance instructions** - adopt physical posture
3. **Gesture execution** - perform each gesture 5 times
4. **Auto-save** - data saved automatically after each recording

## What You'll Do

### Combat Stance Gestures (5-7 min)
- Punch Forward (5 samples)
- Punch Upward (5 samples)

### Neutral Stance Gestures (5-7 min)
- Quick Jump (5 samples)
- Sustained Jump (5 samples)
- Rest/No Motion (5 samples)

### Travel Stance Gestures (7-10 min)
- Walk In Place (5 samples)
- Turn Left (5 samples)
- Turn Right (5 samples)

**Total: 8 gestures × 5 samples = 40 recordings**

## Tips for Success

### Before Starting
- Read the full stance description before adopting it
- Practice each gesture once before recording
- Have water nearby

### During Recording
- **Wait for "GO!"** before executing gesture
- Make movements **crisp and deliberate**
- Return to stance position between samples
- Take breaks if tired

### If Something Goes Wrong
- **No data received**: Check watch streaming is ON
- **Recording failed**: Script will offer to retry
- **Made a mistake**: That's okay! Multiple samples help the model
- **Need to quit**: Press Ctrl+C (partial data is saved)

## Understanding the Output

After completion, you'll see:
```
training_data/
└── session_20251013_141530/
    ├── punch_forward_sample01.csv
    ├── punch_forward_sample02.csv
    ├── ...
    ├── rest_sample05.csv
    └── session_metadata.json
```

**40 CSV files** (one per recording) + **1 metadata file**

## Common Questions

**Q: How long does each recording last?**  
A: 3 seconds per recording, 5 recordings per gesture

**Q: What if I mess up a gesture?**  
A: No problem! The ML model learns from all samples. That's why we do 5 per gesture.

**Q: Can I pause and resume later?**  
A: Not directly, but you can quit (Ctrl+C) and run again. Each session is independent.

**Q: What happens to the data?**  
A: It's saved as CSV files in `training_data/session_YYYYMMDD_HHMMSS/` ready for ML training.

**Q: Do I need to do this multiple times?**  
A: One session provides good baseline data. More sessions improve model robustness.

## Next Steps

After successful data collection:
1. ✓ Data saved in `training_data/session_*/`
2. → Proceed to Phase III: Model Training
3. → Use collected data to train gesture classifier
4. → Deploy model for real-time gesture recognition

## Need Help?

- Review full guide: `docs/Phase_II/DATA_COLLECTION_GUIDE.md`
- Check troubleshooting section in full guide
- Verify watch connection: `docs/101425_P1/TESTING_GUIDE.md`

---

**Ready?** Run `python src/data_collector.py` and follow the prompts!
