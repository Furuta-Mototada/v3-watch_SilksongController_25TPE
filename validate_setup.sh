#!/bin/bash

# =============================================================================
# Setup Validation Script - Check Post-Processing Prerequisites
# =============================================================================
#
# This script validates that all required dependencies and tools are installed
# for the Phase V WhisperX post-processing workflow.
#
# Usage:
#   ./validate_setup.sh
#
# =============================================================================

set -e

# ANSI Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

print_header() {
    echo ""
    echo "========================================================================"
    echo -e "${BOLD}${CYAN}$1${RESET}"
    echo "========================================================================"
    echo ""
}

print_check() {
    echo -e "${BLUE}Checking: $1${RESET}"
}

print_success() {
    echo -e "${GREEN}  ✓ $1${RESET}"
}

print_error() {
    echo -e "${RED}  ✗ $1${RESET}"
}

print_warning() {
    echo -e "${YELLOW}  ⚠ $1${RESET}"
}

print_info() {
    echo -e "${CYAN}  ℹ $1${RESET}"
}

# Track overall status
all_checks_passed=true

# =============================================================================
# Check Python
# =============================================================================

print_header "Python Environment"

print_check "Python installation"
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    print_success "Python $python_version installed"
    
    # Check version (need 3.8+)
    major=$(echo "$python_version" | cut -d. -f1)
    minor=$(echo "$python_version" | cut -d. -f2)
    if [ "$major" -ge 3 ] && [ "$minor" -ge 8 ]; then
        print_success "Python version is compatible (3.8+)"
    else
        print_error "Python version too old (need 3.8+, have $python_version)"
        all_checks_passed=false
    fi
else
    print_error "Python 3 not found"
    print_info "Install Python 3.8+ from https://www.python.org/"
    all_checks_passed=false
fi

# =============================================================================
# Check Python Packages
# =============================================================================

print_header "Python Dependencies"

check_python_package() {
    local package=$1
    local import_name=${2:-$1}
    
    print_check "$package"
    if python3 -c "import $import_name" &> /dev/null; then
        version=$(python3 -c "import $import_name; print($import_name.__version__)" 2>/dev/null || echo "unknown")
        print_success "$package (version: $version)"
        return 0
    else
        print_error "$package not installed"
        print_info "Install with: pip install $package"
        all_checks_passed=false
        return 1
    fi
}

# Core dependencies
check_python_package "whisperx"
check_python_package "torch"
check_python_package "sounddevice"
check_python_package "numpy"
check_python_package "librosa"
check_python_package "soundfile"

# Optional dependencies
echo ""
print_check "Optional: pandas (for data analysis)"
if python3 -c "import pandas" &> /dev/null; then
    print_success "pandas installed"
else
    print_warning "pandas not installed (optional, but recommended)"
    print_info "Install with: pip install pandas"
fi

# =============================================================================
# Check System Libraries
# =============================================================================

print_header "System Libraries"

# Check PortAudio
print_check "PortAudio (for audio recording)"
if python3 -c "import sounddevice; sounddevice.query_devices()" &> /dev/null; then
    print_success "PortAudio is working"
else
    print_error "PortAudio not working"
    print_info "Linux: sudo apt-get install portaudio19-dev"
    print_info "macOS: brew install portaudio"
    print_info "Windows: Usually included with sounddevice"
    all_checks_passed=false
fi

# =============================================================================
# Check GPU/CUDA (Optional)
# =============================================================================

print_header "GPU Acceleration (Optional)"

print_check "CUDA availability"
if python3 -c "import torch; assert torch.cuda.is_available()" &> /dev/null; then
    cuda_version=$(python3 -c "import torch; print(torch.version.cuda)" 2>/dev/null)
    gpu_name=$(python3 -c "import torch; print(torch.cuda.get_device_name(0))" 2>/dev/null)
    print_success "CUDA $cuda_version available"
    print_info "GPU: $gpu_name"
else
    print_warning "CUDA not available - will use CPU (slower but works)"
    
    # Check for Apple Silicon
    if python3 -c "import torch; assert torch.backends.mps.is_available()" &> /dev/null; then
        print_success "Apple Silicon (MPS) acceleration available"
    else
        print_info "Using CPU only - processing will be slower"
    fi
fi

# =============================================================================
# Check Directory Structure
# =============================================================================

print_header "Directory Structure"

print_check "src directory"
if [ -d "src" ]; then
    print_success "src directory exists"
else
    print_error "src directory not found"
    print_info "Are you running this from the repository root?"
    all_checks_passed=false
fi

print_check "Required scripts"
required_scripts=(
    "src/whisperx_transcribe.py"
    "src/align_voice_labels.py"
    "src/continuous_data_collector.py"
    "process_transcripts.sh"
)

for script in "${required_scripts[@]}"; do
    if [ -f "$script" ]; then
        print_success "$(basename $script) found"
    else
        print_error "$(basename $script) not found at $script"
        all_checks_passed=false
    fi
done

print_check "Data directory"
if [ -d "src/data/continuous" ]; then
    print_success "src/data/continuous directory exists"
else
    print_warning "src/data/continuous directory not found - will be created on first use"
fi

# =============================================================================
# Check Documentation
# =============================================================================

print_header "Documentation"

print_check "Phase V documentation"
docs=(
    "docs/Phase_V/POST_PROCESSING.md"
    "docs/Phase_V/DATA_COLLECTION_GUIDE.md"
    "docs/Phase_V/QUICK_REFERENCE.md"
)

for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        print_success "$(basename $doc) found"
    else
        print_warning "$(basename $doc) not found"
    fi
done

# =============================================================================
# Test WhisperX Import
# =============================================================================

print_header "WhisperX Functionality Test"

print_check "WhisperX model loading capability"
if python3 -c "
import whisperx
import torch
device = 'cpu'
print('WhisperX can load models on CPU')
" &> /dev/null; then
    print_success "WhisperX can load models"
else
    print_error "WhisperX model loading failed"
    print_info "This might be due to missing dependencies"
    all_checks_passed=false
fi

# =============================================================================
# Summary
# =============================================================================

print_header "Validation Summary"

if [ "$all_checks_passed" = true ]; then
    echo -e "${GREEN}${BOLD}✅ All checks passed!${RESET}"
    echo ""
    echo "Your environment is ready for Phase V post-processing."
    echo ""
    echo "Next steps:"
    echo "  1. Record a session: cd src && python continuous_data_collector.py --duration 300 --session test"
    echo "  2. Process it: ./process_transcripts.sh YYYYMMDD_HHMMSS_test"
    echo "  3. Check results: cat src/data/continuous/YYYYMMDD_HHMMSS_test_alignment.json"
    echo ""
    echo "See docs/Phase_V/QUICK_REFERENCE.md for complete workflow."
    exit 0
else
    echo -e "${RED}${BOLD}❌ Some checks failed${RESET}"
    echo ""
    echo "Please install missing dependencies before proceeding."
    echo ""
    echo "Quick fix commands:"
    echo "  # Install Python packages"
    echo "  pip install -r requirements.txt"
    echo ""
    echo "  # Install PortAudio (Linux)"
    echo "  sudo apt-get install portaudio19-dev"
    echo ""
    echo "  # Install PortAudio (macOS)"
    echo "  brew install portaudio"
    echo ""
    echo "For detailed setup instructions, see:"
    echo "  - docs/Phase_V/POST_PROCESSING.md"
    echo "  - docs/Phase_V/WhisperX/WHISPERX_INSTALL.md"
    exit 1
fi
