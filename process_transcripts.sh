#!/bin/bash

# =============================================================================
# Process Transcripts - WhisperX Transcription & Label Alignment Automation
# =============================================================================
#
# This script automates the post-processing workflow for continuous data
# collection sessions. It runs WhisperX for transcription with word-level
# timestamps, then aligns voice commands with sensor data to generate labels.
#
# Usage:
#   ./process_transcripts.sh SESSION_NAME [OPTIONS]
#   ./process_transcripts.sh --all [OPTIONS]
#
# Examples:
#   # Process single session
#   ./process_transcripts.sh 20251017_143022_game_01
#
#   # Process all sessions
#   ./process_transcripts.sh --all
#
#   # Use custom WhisperX model
#   ./process_transcripts.sh 20251017_143022_game_01 --model large-v2
#
#   # Enable diarization (requires HuggingFace token)
#   ./process_transcripts.sh 20251017_143022_game_01 --diarize --hf-token TOKEN
#
# =============================================================================

set -e  # Exit on error

# ANSI Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

# Default configuration
DATA_DIR="src/data/continuous"
WHISPERX_MODEL="large-v3"
MIN_CONFIDENCE=0.5
DIARIZE=false
HF_TOKEN=""
PROCESS_ALL=false
SESSION_NAME=""

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo ""
    echo "========================================================================"
    echo -e "${BOLD}${CYAN}$1${RESET}"
    echo "========================================================================"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${RESET}"
}

print_error() {
    echo -e "${RED}✗ ERROR: $1${RESET}"
}

print_warning() {
    echo -e "${YELLOW}⚠ WARNING: $1${RESET}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${RESET}"
}

usage() {
    cat << EOF
Usage: $0 SESSION_NAME [OPTIONS]
       $0 --all [OPTIONS]

Process audio transcripts using WhisperX and align with sensor data.

Arguments:
  SESSION_NAME              Name of the session to process (e.g., 20251017_143022_game_01)
  --all                     Process all sessions in data/continuous/

Options:
  --model MODEL             WhisperX model to use (default: large-v3)
                           Options: tiny, base, small, medium, large, large-v2, large-v3
  --min-confidence CONF     Minimum confidence threshold (default: 0.5)
  --diarize                 Enable speaker diarization
  --hf-token TOKEN          HuggingFace token for diarization models
  --data-dir DIR            Data directory (default: src/data/continuous)
  --help                    Show this help message

Examples:
  # Process single session with defaults
  $0 20251017_143022_game_01

  # Process all sessions
  $0 --all

  # Use smaller, faster model
  $0 20251017_143022_game_01 --model medium

  # Higher confidence threshold for precision
  $0 20251017_143022_game_01 --min-confidence 0.7

  # Enable diarization (multi-speaker)
  $0 20251017_143022_game_01 --diarize --hf-token YOUR_TOKEN

For more details, see: docs/Phase_V/POST_PROCESSING.md
EOF
    exit 1
}

# =============================================================================
# Argument Parsing
# =============================================================================

if [ $# -eq 0 ]; then
    print_error "No arguments provided"
    usage
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            PROCESS_ALL=true
            shift
            ;;
        --model)
            WHISPERX_MODEL="$2"
            shift 2
            ;;
        --min-confidence)
            MIN_CONFIDENCE="$2"
            shift 2
            ;;
        --diarize)
            DIARIZE=true
            shift
            ;;
        --hf-token)
            HF_TOKEN="$2"
            shift 2
            ;;
        --data-dir)
            DATA_DIR="$2"
            shift 2
            ;;
        --help)
            usage
            ;;
        -*)
            print_error "Unknown option: $1"
            usage
            ;;
        *)
            if [ -z "$SESSION_NAME" ]; then
                SESSION_NAME="$1"
            else
                print_error "Multiple session names provided: $SESSION_NAME and $1"
                usage
            fi
            shift
            ;;
    esac
done

# Validate arguments
if [ "$PROCESS_ALL" = false ] && [ -z "$SESSION_NAME" ]; then
    print_error "Either provide SESSION_NAME or use --all flag"
    usage
fi

if [ "$PROCESS_ALL" = true ] && [ -n "$SESSION_NAME" ]; then
    print_error "Cannot use both SESSION_NAME and --all flag"
    usage
fi

# =============================================================================
# Session Processing Function
# =============================================================================

process_session() {
    local session_name=$1
    local session_dir="${DATA_DIR}/${session_name}"
    
    print_header "Processing Session: ${session_name}"
    
    # Check if session directory exists
    if [ ! -d "$session_dir" ]; then
        print_error "Session directory not found: $session_dir"
        return 1
    fi
    
    # Check for required files
    local audio_file="${session_dir}/audio_16k.wav"
    if [ ! -f "$audio_file" ]; then
        print_warning "audio_16k.wav not found, trying audio.wav..."
        audio_file="${session_dir}/audio.wav"
        if [ ! -f "$audio_file" ]; then
            print_error "No audio file found in session directory"
            return 1
        fi
    fi
    
    if [ ! -f "${session_dir}/sensor_data.csv" ]; then
        print_error "sensor_data.csv not found in session directory"
        return 1
    fi
    
    if [ ! -f "${session_dir}/metadata.json" ]; then
        print_error "metadata.json not found in session directory"
        return 1
    fi
    
    print_success "Found required files"
    echo ""
    
    # =============================================================================
    # Step 1: Run WhisperX Transcription
    # =============================================================================
    
    print_info "Step 1/2: Running WhisperX transcription..."
    echo ""
    
    local whisperx_output="${session_dir}/${session_name}_whisperx.json"
    local whisperx_cmd="python src/whisperx_transcribe.py \
        --audio \"${audio_file}\" \
        --output \"${whisperx_output}\" \
        --model ${WHISPERX_MODEL}"
    
    if [ "$DIARIZE" = true ]; then
        whisperx_cmd="${whisperx_cmd} --diarize"
        if [ -n "$HF_TOKEN" ]; then
            whisperx_cmd="${whisperx_cmd} --hf-token ${HF_TOKEN}"
        else
            print_warning "Diarization enabled but no HuggingFace token provided"
            print_warning "Diarization may fail. Get token at: https://huggingface.co/settings/tokens"
        fi
    fi
    
    echo "Running: ${whisperx_cmd}"
    echo ""
    
    if eval $whisperx_cmd; then
        print_success "WhisperX transcription completed"
        echo ""
    else
        print_error "WhisperX transcription failed"
        return 1
    fi
    
    # Check if output file was created
    if [ ! -f "$whisperx_output" ]; then
        print_error "WhisperX output file not created: $whisperx_output"
        return 1
    fi
    
    # =============================================================================
    # Step 2: Align Voice Commands with Sensor Data
    # =============================================================================
    
    print_info "Step 2/2: Aligning voice commands with sensor data..."
    echo ""
    
    local align_cmd="python src/align_voice_labels.py \
        --session ${session_name} \
        --whisper \"${whisperx_output}\" \
        --output-dir ${DATA_DIR} \
        --min-confidence ${MIN_CONFIDENCE}"
    
    echo "Running: ${align_cmd}"
    echo ""
    
    if eval $align_cmd; then
        print_success "Label alignment completed"
        echo ""
    else
        print_error "Label alignment failed"
        return 1
    fi
    
    # =============================================================================
    # Summary
    # =============================================================================
    
    print_header "Processing Complete for ${session_name}"
    
    echo "Output files:"
    echo "  • Transcription:  ${whisperx_output}"
    echo "  • Summary:        ${session_dir}/${session_name}_whisperx_summary.txt"
    echo "  • Labels:         ${DATA_DIR}/${session_name}_labels.csv"
    echo "  • Alignment:      ${DATA_DIR}/${session_name}_alignment.json"
    echo ""
    
    # Display alignment statistics
    if [ -f "${DATA_DIR}/${session_name}_alignment.json" ]; then
        print_info "Alignment Statistics:"
        python3 -c "
import json
import sys
try:
    with open('${DATA_DIR}/${session_name}_alignment.json', 'r') as f:
        data = json.load(f)
    
    print(f\"  • Commands detected: {data.get('commands_detected', 'N/A')}\")
    print(f\"  • Total duration:    {data.get('total_duration', 'N/A'):.1f}s\")
    print(f\"  • Min confidence:    {data.get('min_confidence', 'N/A')}\")
    print('')
    print('  Gesture Distribution:')
    
    stats = data.get('gesture_stats', {})
    total_dur = data.get('total_duration', 1)
    
    for gesture in sorted(stats.keys()):
        gdata = stats[gesture]
        if gesture == 'walk':
            pct = gdata['total_duration'] / total_dur * 100
            print(f\"    - {gesture:8s}: {gdata['total_duration']:7.1f}s ({pct:5.1f}%)\")
        else:
            print(f\"    - {gesture:8s}: {gdata['count']:3d} events, {gdata['total_duration']:6.1f}s total\")
except Exception as e:
    print(f'Error reading alignment stats: {e}', file=sys.stderr)
"
        echo ""
    fi
    
    print_success "Session ${session_name} processed successfully!"
    echo ""
    
    return 0
}

# =============================================================================
# Main Execution
# =============================================================================

print_header "WhisperX Transcription & Label Alignment"

echo "Configuration:"
echo "  • Data directory:     ${DATA_DIR}"
echo "  • WhisperX model:     ${WHISPERX_MODEL}"
echo "  • Min confidence:     ${MIN_CONFIDENCE}"
echo "  • Diarization:        ${DIARIZE}"
if [ "$DIARIZE" = true ] && [ -n "$HF_TOKEN" ]; then
    echo "  • HF token:           [provided]"
fi
echo ""

# Check if Python is available
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    print_error "Python not found. Please install Python 3.8+"
    exit 1
fi

# Use python3 if available, otherwise python
if command -v python3 &> /dev/null; then
    alias python=python3
fi

# Check if src directory exists
if [ ! -d "src" ]; then
    print_error "src directory not found. Please run this script from the repository root."
    exit 1
fi

# Check if required Python scripts exist
if [ ! -f "src/whisperx_transcribe.py" ]; then
    print_error "src/whisperx_transcribe.py not found"
    exit 1
fi

if [ ! -f "src/align_voice_labels.py" ]; then
    print_error "src/align_voice_labels.py not found"
    exit 1
fi

# Process sessions
if [ "$PROCESS_ALL" = true ]; then
    print_info "Processing all sessions in ${DATA_DIR}/"
    echo ""
    
    # Find all session directories
    session_count=0
    success_count=0
    fail_count=0
    
    if [ ! -d "$DATA_DIR" ]; then
        print_error "Data directory not found: $DATA_DIR"
        exit 1
    fi
    
    for session_path in "${DATA_DIR}"/*/ ; do
        if [ -d "$session_path" ]; then
            session=$(basename "$session_path")
            ((session_count++))
            
            if process_session "$session"; then
                ((success_count++))
            else
                ((fail_count++))
                print_warning "Failed to process session: $session"
                echo ""
            fi
        fi
    done
    
    # Summary
    print_header "Batch Processing Summary"
    echo "  • Total sessions:     ${session_count}"
    echo "  • Successful:         ${success_count}"
    echo "  • Failed:             ${fail_count}"
    echo ""
    
    if [ $fail_count -eq 0 ]; then
        print_success "All sessions processed successfully!"
    else
        print_warning "Some sessions failed to process. Check logs above."
    fi
    
else
    # Process single session
    if process_session "$SESSION_NAME"; then
        exit 0
    else
        exit 1
    fi
fi

echo ""
print_info "Next steps:"
echo "  1. Review generated labels CSV files"
echo "  2. Validate alignment using visualization tools"
echo "  3. Use labeled data for CNN/LSTM training"
echo ""
print_info "For more information, see: docs/Phase_V/POST_PROCESSING.md"
echo ""
