# Cloud GPU Guide: Accelerating WhisperX & Model Training

**Date:** October 17, 2025
**Status:** ✅ Recommended for WhisperX transcription and CNN/LSTM training
**Estimated Time Savings:** Hours → Minutes

---

## Table of Contents

1. [Why Use Cloud GPUs?](#why-use-cloud-gpus)
2. [Local vs. Cloud Comparison](#local-vs-cloud-comparison)
3. [Google Colab Setup (Recommended)](#google-colab-setup-recommended)
4. [Alternative Cloud Platforms](#alternative-cloud-platforms)
5. [Cost Analysis](#cost-analysis)
6. [Troubleshooting](#troubleshooting)

---

## Why Use Cloud GPUs?

### The Situation

You have successfully collected gesture data and are now facing the computational cost of:
1. **WhisperX Transcription** - Processing audio with the `large-v3` model
2. **CNN/LSTM Training** - Training your gesture recognition model

### Current Performance on M2 Air

- ✅ **MPS acceleration is working** (Apple Silicon GPU)
- ⚠️ **Speed is limited** for large models
- ⏱️ **Estimated times:**
  - WhisperX `large-v3`: 15-60 minutes per 10-minute audio file
  - CNN/LSTM training: 2-6 hours per training run
  - Total time for all sessions: **Several days**

### Cloud GPU Performance

- ⚡ **WhisperX `large-v3`**: 2-5 minutes per 10-minute audio file
- ⚡ **CNN/LSTM training**: 20-60 minutes per training run
- ⏱️ **Total time for all sessions: A few hours**

### The Verdict

**For WhisperX transcription and model training, cloud GPUs are highly recommended.**

The speed advantage is so significant that it will save you days of waiting and enable rapid iteration on your model architecture.

---

## Local vs. Cloud Comparison

| Factor | M2 Air (Local) | Cloud GPU (Colab) |
|--------|----------------|-------------------|
| **Cost** | Free | Free tier available |
| **Setup** | Already configured | 5-10 minutes initial setup |
| **WhisperX Speed** | 15-60 min/10min audio | 2-5 min/10min audio |
| **Training Speed** | 2-6 hours/run | 20-60 min/run |
| **Iteration Cycle** | Days | Hours |
| **Machine Availability** | Tied up during processing | Your Mac stays free |
| **Failure Recovery** | Lost hours if crash | Quick retry |
| **Best For** | Small debugging, quick tests | Full transcription, training |

**Recommendation:** Use local for quick tests and debugging. Use cloud for production transcription and training.

---

## Google Colab Setup (Recommended)

### What is Google Colab?

A free Jupyter Notebook environment that runs in your browser with access to powerful NVIDIA GPUs (T4, P100, or A100).

- 🆓 **Free tier:** Up to 12 hours continuous runtime
- ⚡ **Fast GPUs:** 10-50x faster than M2 Air
- 🌐 **Browser-based:** No local installation needed
- 💾 **Google Drive integration:** Easy file access

---

## Step-by-Step: WhisperX in Google Colab

### Step 1: Prepare Your Data in Google Drive

1. **Open Google Drive** ([drive.google.com](https://drive.google.com))

2. **Create folder structure:**
   ```
   My Drive/
   └── silksong_data/
       └── 20251017_125600_session/
           └── audio_16k.wav
       └── [other_session_folders]/
   ```

3. **Upload your audio file:**
   - Go to your local project folder: `data/continuous/20251017_125600_session/`
   - Upload `audio_16k.wav` to the corresponding Google Drive folder
   - Repeat for other sessions you want to process

**💡 Tip:** You can upload multiple session folders to process them in batch.

---

### Step 2: Create a New Colab Notebook

1. **Go to Google Colab:** [colab.research.google.com](https://colab.research.google.com)

2. **Create a new notebook:**
   - Click **"New notebook"**
   - Rename it: `WhisperX_Silksong_Transcription`

3. **Enable GPU acceleration:**
   - Go to menu: **Runtime → Change runtime type**
   - Set **Hardware accelerator** to **GPU**
   - Click **Save**

4. **Verify GPU is available:**
   - Run this in a cell:
     ```python
     !nvidia-smi
     ```
   - You should see GPU details (T4, P100, or A100)

---

### Step 3: Install WhisperX and Dependencies

**In the first code cell, run:**

```python
# Install WhisperX and dependencies
!pip install -q git+https://github.com/m-bain/whisperx.git
!pip install -q torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

print("✅ Installation complete!")
```

**Expected time:** 2-3 minutes

---

### Step 4: Mount Google Drive

**In a new cell, run:**

```python
from google.colab import drive
drive.mount('/content/drive')

# Verify the mount
!ls "/content/drive/My Drive/silksong_data/"
```

**What happens:**
- You'll see an authorization prompt
- Click the link and sign in with your Google account
- Copy the authorization code and paste it
- Your Google Drive is now accessible at `/content/drive/My Drive/`

---

### Step 5: Run WhisperX Transcription

**Option A: Single Session**

```python
import os

# Define paths
session_name = "20251017_125600_session"
audio_path = f"/content/drive/My Drive/silksong_data/{session_name}/audio_16k.wav"
output_dir = f"/content/drive/My Drive/silksong_data/{session_name}/"

# Run WhisperX with custom prompt
!whisperx "{audio_path}" \
    --model large-v3 \
    --output_dir "{output_dir}" \
    --language en \
    --align_model WAV2VEC2_ASR_LARGE_LV60K_960H \
    --diarize False \
    --initial_prompt "The following is a transcription of a person playing the video game Hollow Knight: Silksong. They are speaking their character's actions out loud. The key commands are: jump, punch, attack, turn, walk, walking, walk start, idle, rest, stop, noise. The speaker might say phrases like 'I'm gonna jump here', 'punch punch', 'let me walk over there', 'okay, now idle', or 'that was noise'."

print(f"✅ Transcription complete! Check output in: {output_dir}")
```

**Option B: Batch Processing Multiple Sessions**

```python
import os

# List of session folders to process
sessions = [
    "20251017_125600_session",
    "20251017_130000_session",
    "20251017_131500_session"
    # Add more session names here
]

base_path = "/content/drive/My Drive/silksong_data/"

# Custom prompt for gesture commands
custom_prompt = (
    "The following is a transcription of a person playing the video game "
    "Hollow Knight: Silksong. They are speaking their character's actions out loud. "
    "The key commands are: jump, punch, attack, turn, walk, walking, walk start, "
    "idle, rest, stop, noise. The speaker might say phrases like 'I'm gonna jump here', "
    "'punch punch', 'let me walk over there', 'okay, now idle', or 'that was noise'."
)

# Process each session
for i, session in enumerate(sessions, 1):
    print(f"\n{'='*70}")
    print(f"Processing session {i}/{len(sessions)}: {session}")
    print(f"{'='*70}\n")

    audio_path = os.path.join(base_path, session, "audio_16k.wav")
    output_dir = os.path.join(base_path, session)

    # Check if audio file exists
    if not os.path.exists(audio_path):
        print(f"⚠️  Audio file not found: {audio_path}")
        continue

    # Run WhisperX
    !whisperx "{audio_path}" \
        --model large-v3 \
        --output_dir "{output_dir}" \
        --language en \
        --align_model WAV2VEC2_ASR_LARGE_LV60K_960H \
        --diarize False \
        --initial_prompt "{custom_prompt}"

    print(f"✅ Session {session} complete!")

print("\n" + "="*70)
print("🎉 All sessions processed successfully!")
print("="*70)
```

**Expected time per 10-minute audio file:** 2-5 minutes

---

### Step 6: Download Results

Your transcription files are saved directly to Google Drive:

```
My Drive/silksong_data/20251017_125600_session/
├── audio_16k.wav
├── audio_16k.json           ← WhisperX output (word-level timestamps)
├── audio_16k.srt            ← Subtitle format
└── audio_16k.txt            ← Plain text transcript
```

**To download to your local machine:**

1. **In Google Drive:** Navigate to the session folder
2. **Right-click** on `audio_16k.json`
3. **Select "Download"**
4. **Move to your local project:**
   ```bash
   mv ~/Downloads/audio_16k.json \
      data/continuous/20251017_125600_session/whisperx_output.json
   ```

**Or use the Colab download cell:**

```python
from google.colab import files

# Download the JSON output
session_name = "20251017_125600_session"
json_path = f"/content/drive/My Drive/silksong_data/{session_name}/audio_16k.json"

files.download(json_path)
```

---

## Alternative: Use Your Modified Script in Colab

If you want to use your custom `whisperx_transcribe.py` script:

### Step 1: Upload Your Script to Google Drive

Upload `whisperx_transcribe.py` to: `My Drive/silksong_data/scripts/`

### Step 2: Run Your Script in Colab

```python
# Navigate to script directory
%cd "/content/drive/My Drive/silksong_data/scripts/"

# Run your custom script
!python whisperx_transcribe.py \
    --audio "/content/drive/My Drive/silksong_data/20251017_125600_session/audio_16k.wav" \
    --output "/content/drive/My Drive/silksong_data/20251017_125600_session/whisperx_output.json" \
    --model large-v3 \
    --device cuda \
    --language en
```

**Benefits:**
- ✅ Uses your custom prompt automatically
- ✅ Familiar output format
- ✅ Same preprocessing pipeline

---

## Step 7: Verify Results

**In Colab, check the output:**

```python
import json

# Load the transcription results
session_name = "20251017_125600_session"
json_path = f"/content/drive/My Drive/silksong_data/{session_name}/audio_16k.json"

with open(json_path, 'r') as f:
    results = json.load(f)

# Print summary
print(f"Segments: {len(results['segments'])}")
print(f"Language: {results.get('language', 'unknown')}")

# Show first 10 words with timestamps
print("\nFirst 10 words:")
for i, segment in enumerate(results['segments'][:3]):
    for word_info in segment.get('words', [])[:10]:
        word = word_info['word']
        start = word_info['start']
        end = word_info['end']
        confidence = word_info.get('score', 0)
        print(f"  {start:7.2f}s-{end:7.2f}s | {word:15s} | conf: {confidence:.3f}")
```

---

## Alternative Cloud Platforms

### Paperspace Gradient (Paid)

**Best for:** Longer training runs, persistent storage

**Setup:**
1. Sign up at [gradient.paperspace.com](https://gradient.paperspace.com)
2. Create a new notebook with GPU
3. Follow similar steps as Colab

**Cost:** ~$0.07/hour for basic GPU

---

### Lambda Labs (Paid)

**Best for:** High-performance GPUs (A100, H100)

**Setup:**
1. Sign up at [lambdalabs.com](https://lambdalabs.com)
2. Launch a GPU instance
3. SSH in and install dependencies

**Cost:** ~$1.10/hour for A100

---

### Kaggle Notebooks (Free)

**Best for:** Kaggle users, similar to Colab

**Setup:**
1. Go to [kaggle.com/code](https://www.kaggle.com/code)
2. Create a new notebook
3. Enable GPU in settings

**Limits:** 30 hours/week GPU time

---

## Cost Analysis

### Google Colab

| Tier | Cost | GPU Hours | Best For |
|------|------|-----------|----------|
| **Free** | $0 | ~12 hrs/day | Your project ✅ |
| **Colab Pro** | $9.99/month | 24 hrs/day | Heavy usage |
| **Colab Pro+** | $49.99/month | Priority access | Research teams |

**Recommendation for Silksong Project:**
- **Free tier is sufficient** for transcribing all your sessions
- Estimated total time: 2-4 hours for all transcriptions
- Estimated training time: 1-2 hours for CNN/LSTM experiments

**Total cost: $0** ✅

---

## Troubleshooting

### Issue: "Runtime disconnected"

**Cause:** Colab free tier has time limits (~12 hours)

**Solution:**
- Save your work regularly to Google Drive
- Close the tab or click "Reconnect"
- Your files in Google Drive are safe

---

### Issue: "Out of memory" error

**Cause:** GPU VRAM exceeded

**Solutions:**
1. Use smaller batch size:
   ```python
   !whisperx ... --batch_size 8
   ```

2. Use smaller model:
   ```python
   !whisperx ... --model large-v2
   ```

3. Restart runtime: **Runtime → Restart runtime**

---

### Issue: WhisperX installation fails

**Solution:**

```python
# Force reinstall with specific versions
!pip install --force-reinstall git+https://github.com/m-bain/whisperx.git
!pip install --upgrade torch torchvision torchaudio
```

---

### Issue: Can't find audio file in Google Drive

**Debug:**

```python
# Check if Drive is mounted
!ls /content/drive/

# Check path exists
import os
audio_path = "/content/drive/My Drive/silksong_data/20251017_125600_session/audio_16k.wav"
print(f"File exists: {os.path.exists(audio_path)}")

# List directory contents
!ls -lh "/content/drive/My Drive/silksong_data/20251017_125600_session/"
```

---

## Complete Workflow Summary

### Phase 1: Setup (One-Time, 10 minutes)

1. ✅ Upload audio files to Google Drive
2. ✅ Create Colab notebook
3. ✅ Enable GPU
4. ✅ Install WhisperX
5. ✅ Mount Google Drive

### Phase 2: Transcription (Per Session, 2-5 minutes)

1. ✅ Run WhisperX with custom prompt
2. ✅ Verify output in Google Drive
3. ✅ Download JSON results

### Phase 3: Model Training (Later Phase)

1. ✅ Upload training data to Google Drive
2. ✅ Run CNN/LSTM training in Colab
3. ✅ Download trained model
4. ✅ Deploy to local machine

---

## Next Steps

### After WhisperX Transcription Completes:

1. **Download all `audio_16k.json` files** from Google Drive

2. **Move to local project:**
   ```bash
   mv ~/Downloads/audio_16k.json \
      data/continuous/20251017_125600_session/whisperx_output.json
   ```

3. **Run label alignment** (on your local machine):
   ```bash
   python align_voice_labels.py \
     --session 20251017_125600_session \
     --whisper data/continuous/20251017_125600_session/whisperx_output.json
   ```

4. **Continue with Phase III** (training data preparation)

5. **Return to Colab** for CNN/LSTM training

---

## Tips for Success

### ✅ DO:

- Save work frequently to Google Drive
- Use batch processing for multiple sessions
- Monitor GPU usage with `!nvidia-smi`
- Keep browser tab open during processing
- Download results immediately after completion

### ❌ DON'T:

- Don't close browser during long runs
- Don't exceed free tier limits (Colab will warn you)
- Don't store sensitive data in public notebooks
- Don't forget to download results before runtime expires

---

## Resources

- **WhisperX GitHub:** [github.com/m-bain/whisperx](https://github.com/m-bain/whisperx)
- **Google Colab Docs:** [colab.research.google.com/notebooks/intro.ipynb](https://colab.research.google.com/notebooks/intro.ipynb)
- **PyTorch + CUDA:** [pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/)

---

## Conclusion

Using Google Colab for WhisperX transcription will:

✅ **Save you days of waiting time**
✅ **Free up your M2 Air for other work**
✅ **Enable rapid iteration on model training**
✅ **Cost you $0** (with free tier)
✅ **Provide professional-grade GPU acceleration**

**Recommendation:** Start with Colab free tier for all transcription and initial model training. Only upgrade if you need longer continuous runtimes.

---

**Questions?** Check the [Troubleshooting](#troubleshooting) section or refer to the Phase V documentation.
