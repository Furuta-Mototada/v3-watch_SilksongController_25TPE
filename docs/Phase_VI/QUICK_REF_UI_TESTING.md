# Quick Reference - Dark Theme & Testing Mode

## 🎨 Android UI Changes

### Color Scheme
**Dark sophisticated theme** (like banking apps):
- All buttons: Dark backgrounds (#2C-#30 range)
- Recording state: Subtle colored overlay (20% opacity)
- Text: White at 90% opacity
- Counts: Large minimalist numbers

### New Buttons
- **Connect**: Test UDP connection (dark gray)
- **Reset**: Clear all counters (soft red)

Both at bottom of screen, side-by-side.

---

## 🐍 Python Testing Flag

### Command
```bash
python button_data_collector.py --skip-noise
```

### What It Does
- Skips 30-second baseline noise capture
- Immediately ready after ENTER press
- Perfect for testing button app

### When To Use
✅ Testing connectivity
✅ Debugging labels
✅ Quick gesture tests

❌ NOT for training data collection

---

## 🚀 Quick Test Workflow

1. **Start Python with skip flag:**
   ```bash
   cd src
   python button_data_collector.py --skip-noise
   ```

2. **Start watch app** (streaming sensor data)

3. **Start phone app** (button grid)

4. **Wait for both to connect**, then press ENTER

5. **Tap "Connect" button** on phone to test

6. **Hold gesture buttons** to test labeling

7. **No 30-second wait!** Start testing immediately

---

## 📝 Files Modified

- `Android_2_Grid/.../MainActivity.kt` - Dark theme + buttons
- `Android_2_Grid/.../DataCollectorViewModel.kt` - testConnection()
- `src/button_data_collector.py` - --skip-noise flag

Full details in `UI_TESTING_IMPROVEMENTS.md`
