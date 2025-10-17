# WhisperX Installation Guide

Complete installation guide for WhisperX research-grade word segmentation.

## System Requirements

### Minimum Requirements
- Python 3.8 or higher
- 8GB RAM (16GB recommended for large models)
- 5GB free disk space for models
- ffmpeg

### Recommended Requirements
- Python 3.9-3.11
- 16GB RAM
- NVIDIA GPU with 8GB+ VRAM (for GPU acceleration)
- Or Apple Silicon Mac (M1/M2/M3)
- 10GB free disk space

## Step-by-Step Installation

### 1. Install System Dependencies

#### macOS
```bash
# Install ffmpeg
brew install ffmpeg

# Install PortAudio (for audio recording)
brew install portaudio
```

#### Linux (Ubuntu/Debian)
```bash
# Install ffmpeg
sudo apt-get update
sudo apt-get install -y ffmpeg

# Install PortAudio (for audio recording)
sudo apt-get install -y portaudio19-dev
```

#### Windows
1. Download ffmpeg from https://ffmpeg.org/download.html
2. Extract and add to PATH
3. PortAudio is usually bundled with sounddevice on Windows

### 2. Install Python Dependencies

#### Option A: Install from project requirements (Recommended)
```bash
# Navigate to project directory
cd /path/to/v3-watch_SilksongController_25TPE

# Install all dependencies including WhisperX
pip install -r requirements.txt
```

#### Option B: Install WhisperX separately
```bash
# Install WhisperX
pip install whisperx

# Install audio processing libraries
pip install librosa soundfile

# Install other project dependencies
pip install -r requirements.txt
```

#### Option C: Install from source (Latest version)
```bash
# Install from GitHub
pip install git+https://github.com/m-bain/whisperX.git
```

### 3. Install GPU Support (Optional but Recommended)

#### NVIDIA GPU (CUDA)

Check your CUDA version:
```bash
nvidia-smi
```

Install PyTorch with CUDA support:

**For CUDA 11.8:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**For CUDA 12.1:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**For CUDA 12.4:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

#### Apple Silicon (M1/M2/M3)

PyTorch with MPS (Metal Performance Shaders) support is included by default:
```bash
pip install torch torchvision torchaudio
```

No additional configuration needed!

#### CPU Only

If you don't have a GPU, PyTorch CPU version is fine:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

Note: Processing will be slower, so consider using smaller models (`medium` instead of `large-v3`).

### 4. Verify Installation

#### Check WhisperX Installation
```bash
python -c "import whisperx; print('WhisperX version:', whisperx.__version__)"
```

Expected output:
```
WhisperX version: 3.1.x
```

#### Check GPU Availability
```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('MPS available:', torch.backends.mps.is_available())"
```

Expected output (CUDA GPU):
```
CUDA available: True
MPS available: False
```

Expected output (Apple Silicon):
```
CUDA available: False
MPS available: True
```

Expected output (CPU only):
```
CUDA available: False
MPS available: False
```

#### Test WhisperX Script
```bash
cd src
python whisperx_transcribe.py --help
```

You should see the help message without errors.

### 5. Download Models (Automatic)

WhisperX will automatically download models on first use. To pre-download:

```bash
# Create a test audio file
cd /tmp
echo "test audio" | \
  ffmpeg -f lavfi -i "sine=frequency=1000:duration=1" -ar 16000 test.wav -y

# Run WhisperX (will download large-v3 model)
cd /path/to/v3-watch_SilksongController_25TPE/src
python whisperx_transcribe.py --audio /tmp/test.wav --model large-v3
```

Models are cached in:
- **Linux/macOS**: `~/.cache/whisper/`
- **Windows**: `%USERPROFILE%\.cache\whisper\`

Model sizes:
- `large-v3`: ~3GB
- `large-v2`: ~3GB
- `medium`: ~1.5GB
- `base`: ~150MB
- `tiny`: ~75MB

### 6. Setup for Diarization (Optional)

If you need speaker diarization:

#### Create HuggingFace Account
1. Go to https://huggingface.co/
2. Sign up for a free account

#### Get Access Token
1. Go to https://huggingface.co/settings/tokens
2. Create a new token (read access is sufficient)
3. Copy the token (starts with `hf_`)

#### Accept Model Agreements
1. Visit https://huggingface.co/pyannote/speaker-diarization
2. Accept the user agreement
3. Visit https://huggingface.co/pyannote/segmentation
4. Accept the user agreement

#### Save Token
Create a file to store your token (optional):
```bash
echo "export HF_TOKEN=hf_your_token_here" >> ~/.bashrc
source ~/.bashrc
```

Or pass it directly:
```bash
python whisperx_transcribe.py --audio file.wav --diarize --hf-token hf_your_token
```

## Troubleshooting

### Issue: "WhisperX is not installed"

**Solution:**
```bash
pip install whisperx
```

If that fails:
```bash
pip install git+https://github.com/m-bain/whisperX.git
```

### Issue: "No module named 'librosa'"

**Solution:**
```bash
pip install librosa soundfile
```

### Issue: "CUDA out of memory"

**Solutions:**
1. Reduce batch size:
   ```bash
   python whisperx_transcribe.py --audio file.wav --batch-size 4
   ```

2. Use a smaller model:
   ```bash
   python whisperx_transcribe.py --audio file.wav --model medium
   ```

3. Use CPU mode:
   ```bash
   python whisperx_transcribe.py --audio file.wav --device cpu
   ```

### Issue: "RuntimeError: Failed to import transformers"

**Solution:**
```bash
pip install transformers
```

### Issue: "Cannot find alignment model for language"

**Solution:**
Specify a supported language or skip alignment:
```bash
python whisperx_transcribe.py --audio file.wav --language en
```

Supported languages for alignment:
- en (English)
- es (Spanish)
- fr (French)
- de (German)
- it (Italian)
- pt (Portuguese)
- and many more...

Or skip alignment:
```bash
python whisperx_transcribe.py --audio file.wav --no-alignment
```

### Issue: "ffmpeg not found"

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
1. Download from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to PATH

### Issue: Installation is very slow

**Solution:**
Use a faster mirror:
```bash
pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple whisperx
```

Or use conda (if you use conda):
```bash
conda install -c conda-forge whisperx
```

### Issue: "torch version incompatible"

**Solution:**
Reinstall PyTorch:
```bash
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio
```

## Verification Checklist

After installation, verify everything works:

- [ ] Python 3.8+ installed: `python --version`
- [ ] ffmpeg installed: `ffmpeg -version`
- [ ] WhisperX installed: `python -c "import whisperx"`
- [ ] GPU detected (if available): `python -c "import torch; print(torch.cuda.is_available())"`
- [ ] Can run help: `python whisperx_transcribe.py --help`
- [ ] Audio preprocessing works: `python -c "import librosa; import soundfile"`

## Disk Space Requirements

Plan for these storage needs:

| Component | Size | Location |
|-----------|------|----------|
| WhisperX package | ~200MB | Python site-packages |
| large-v3 model | ~3GB | ~/.cache/whisper/ |
| large-v2 model | ~3GB | ~/.cache/whisper/ |
| medium model | ~1.5GB | ~/.cache/whisper/ |
| Alignment models | ~1GB | ~/.cache/torch/hub/ |
| Diarization models | ~1GB | ~/.cache/torch/hub/ |

Total for full setup: ~10GB

## Uninstallation

To remove WhisperX:

```bash
# Uninstall packages
pip uninstall whisperx torch torchvision torchaudio

# Remove cached models
rm -rf ~/.cache/whisper/
rm -rf ~/.cache/torch/hub/
```

## Alternative: Docker Installation

If you prefer Docker:

```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install whisperx librosa soundfile

WORKDIR /app
COPY . .

CMD ["python", "src/whisperx_transcribe.py", "--help"]
```

Build and run:
```bash
docker build -t whisperx .
docker run -v $(pwd):/app whisperx python src/whisperx_transcribe.py --audio /app/data/audio.wav
```

## Next Steps

After successful installation:

1. Read the full guide: `docs/WHISPERX_GUIDE.md`
2. Try examples: `docs/WHISPERX_EXAMPLE.md`
3. Check quick reference: `docs/WHISPERX_QUICKREF.md`
4. Run your first transcription:
   ```bash
   python whisperx_transcribe.py --audio your_audio.wav
   ```

## Support

If you encounter issues:

1. Check WhisperX GitHub: https://github.com/m-bain/whisperX/issues
2. Check Whisper GitHub: https://github.com/openai/whisper/issues
3. Check PyTorch forum: https://discuss.pytorch.org/
4. Check this project's issues

## Summary

**Quick Install:**
```bash
# 1. Install system dependencies
brew install ffmpeg portaudio  # macOS
# or
sudo apt-get install ffmpeg portaudio19-dev  # Linux

# 2. Install Python packages
pip install whisperx librosa soundfile

# 3. Verify
python -c "import whisperx; print('Success!')"

# 4. Test
python whisperx_transcribe.py --help
```

You're ready to use WhisperX for research-grade word segmentation!
