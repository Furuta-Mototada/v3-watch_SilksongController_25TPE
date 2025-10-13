#!/usr/bin/env python3
"""
Data Collection Script for IMU Gesture Dataset
Phase II: High-Fidelity Data Acquisition from Pixel Watch

This script provides a guided, user-centric procedure for collecting
clean, comprehensive, and perfectly labeled IMU gesture data.
"""

import socket
import json
import time
import os
from datetime import datetime
from pathlib import Path
import network_utils


# ANSI color codes for terminal output
class Colors:
    """Terminal color codes for enhanced user experience."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_banner(title, color=Colors.OKBLUE):
    """Print a formatted banner for section headers."""
    print(f"\n{color}{'=' * 70}")
    print(f"{title.center(70)}")
    print(f"{'=' * 70}{Colors.ENDC}\n")


def print_instruction(message, color=Colors.OKCYAN):
    """Print an instruction message with formatting."""
    print(f"{color}{message}{Colors.ENDC}")


def print_success(message):
    """Print a success message."""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_warning(message):
    """Print a warning message."""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


def print_error(message):
    """Print an error message."""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def wait_for_user(prompt="Press [Enter] to continue..."):
    """Wait for user to press Enter."""
    input(f"{Colors.BOLD}{prompt}{Colors.ENDC}")


def load_config():
    """Load configuration from config.json file."""
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print_error("config.json not found. Please create one.")
        exit(1)


def setup_data_directory():
    """Create directory structure for collected data."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = Path("data_collection") / timestamp
    
    # Create directories for each stance
    stances = ["combat", "neutral", "travel"]
    gestures = {
        "combat": ["punch", "slash", "stab"],
        "neutral": ["jump", "hop", "crouch"],
        "travel": ["walk", "turn_left", "turn_right", "stop"]
    }
    
    for stance in stances:
        for gesture in gestures[stance]:
            (base_dir / stance / gesture).mkdir(parents=True, exist_ok=True)
    
    # Create metadata directory
    (base_dir / "metadata").mkdir(parents=True, exist_ok=True)
    
    return base_dir, timestamp


def save_metadata(base_dir, metadata):
    """Save collection session metadata."""
    metadata_file = base_dir / "metadata" / "session_info.json"
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=4)
    print_success(f"Metadata saved to {metadata_file}")


def explain_stances():
    """Explain the three user stances in detail."""
    print_banner("USER STANCES OVERVIEW", Colors.HEADER)
    
    print_instruction("This data collection uses THREE distinct stances:", Colors.BOLD)
    print()
    
    # Combat Stance
    print(f"{Colors.WARNING}1. COMBAT STANCE{Colors.ENDC}")
    print("   Purpose: For attack gestures (punch, slash, stab)")
    print("   Position: Hold watch arm as if holding a weapon")
    print("            - Watch face should be perpendicular to ground")
    print("            - Screen facing sideways (left for right-handed users)")
    print("            - Elbow bent at ~90 degrees")
    print("            - Ready to strike forward")
    print()
    
    # Neutral Stance
    print(f"{Colors.OKBLUE}2. NEUTRAL STANCE{Colors.ENDC}")
    print("   Purpose: For vertical movements (jump, hop, crouch)")
    print("   Position: Natural standing position")
    print("            - Watch face parallel to ground")
    print("            - Screen facing UP toward sky")
    print("            - Arm relaxed at side or bent naturally")
    print("            - Weight balanced on both feet")
    print()
    
    # Travel Stance
    print(f"{Colors.OKGREEN}3. TRAVEL STANCE{Colors.ENDC}")
    print("   Purpose: For locomotion (walk, turn, stop)")
    print("   Position: Natural walking position")
    print("            - Watch face parallel to ground")
    print("            - Screen facing UP or slightly inward")
    print("            - Arm swinging naturally while walking")
    print("            - Body facing direction of travel")
    print()
    
    wait_for_user()


def explain_data_collection_protocol():
    """Explain the overall data collection protocol."""
    print_banner("DATA COLLECTION PROTOCOL", Colors.HEADER)
    
    print("This session will collect data for multiple gestures across different stances.")
    print()
    print("For EACH gesture, you will:")
    print("  1. Receive stance instructions")
    print("  2. Position yourself correctly")
    print("  3. Wait for the countdown")
    print("  4. Perform the gesture when prompted")
    print("  5. Return to ready position")
    print()
    print("We will collect MULTIPLE samples of each gesture to ensure data quality.")
    print()
    print_instruction("Key Guidelines:", Colors.BOLD)
    print("  • Perform gestures NATURALLY - don't exaggerate")
    print("  • Maintain the specified stance throughout")
    print("  • Wait for the 'GO!' signal before moving")
    print("  • Execute gestures crisply and deliberately")
    print("  • Take breaks between samples if needed")
    print()
    
    wait_for_user()


def collect_sensor_data(sock, duration_sec, buffer_size=2048):
    """
    Collect raw sensor data for a specified duration.
    
    Args:
        sock: UDP socket for receiving data
        duration_sec: Duration to collect data in seconds
        buffer_size: UDP packet buffer size
    
    Returns:
        List of parsed JSON sensor packets
    """
    data_packets = []
    start_time = time.time()
    end_time = start_time + duration_sec
    
    print(f"  📊 Recording for {duration_sec} seconds...")
    
    packet_count = 0
    sensor_counts = {}
    
    while time.time() < end_time:
        remaining = end_time - time.time()
        print(f"\r  ⏱  Time remaining: {remaining:.1f}s | Packets: {packet_count}", end="", flush=True)
        
        try:
            data, _ = sock.recvfrom(buffer_size)
            parsed = json.loads(data.decode())
            
            # Add collection timestamp
            parsed['collection_timestamp'] = time.time()
            data_packets.append(parsed)
            
            packet_count += 1
            
            # Count sensor types
            sensor_type = parsed.get('sensor', 'unknown')
            sensor_counts[sensor_type] = sensor_counts.get(sensor_type, 0) + 1
            
        except (BlockingIOError, json.JSONDecodeError, KeyError) as e:
            time.sleep(0.001)  # Small delay to prevent busy waiting
    
    print()  # New line after the progress indicator
    print_success(f"Collected {packet_count} packets")
    
    # Print sensor distribution
    if sensor_counts:
        print("  📈 Sensor distribution:")
        for sensor, count in sorted(sensor_counts.items()):
            print(f"     - {sensor}: {count}")
    
    return data_packets


def save_gesture_data(base_dir, stance, gesture, sample_num, data_packets, metadata):
    """
    Save collected gesture data to file.
    
    Args:
        base_dir: Base directory for data collection
        stance: Stance name (combat, neutral, travel)
        gesture: Gesture name
        sample_num: Sample number
        data_packets: List of sensor data packets
        metadata: Additional metadata for this sample
    """
    filename = f"{gesture}_sample_{sample_num:03d}.json"
    filepath = base_dir / stance / gesture / filename
    
    output_data = {
        "metadata": metadata,
        "sensor_data": data_packets
    }
    
    with open(filepath, "w") as f:
        json.dump(output_data, f, indent=2)
    
    print_success(f"Saved to {filepath}")


def collect_gesture_samples(sock, base_dir, stance, gesture, num_samples=5, duration_sec=3.0):
    """
    Collect multiple samples of a specific gesture.
    
    Args:
        sock: UDP socket for receiving data
        base_dir: Base directory for data collection
        stance: Stance name
        gesture: Gesture name
        num_samples: Number of samples to collect
        duration_sec: Duration of each sample in seconds
    """
    print_banner(f"COLLECTING: {gesture.upper()} ({stance.upper()} Stance)", Colors.OKGREEN)
    
    # Provide gesture-specific instructions
    gesture_instructions = {
        "punch": "Perform a sharp, forward punch motion",
        "slash": "Execute a horizontal slashing motion across your body",
        "stab": "Make a quick, forward stabbing motion",
        "jump": "Perform a vertical jump motion (you may actually jump or simulate)",
        "hop": "Make a small, quick hop upward",
        "crouch": "Quickly lower into a crouch position",
        "walk": "Walk in place at a natural pace",
        "turn_left": "Turn your body 180° to the left while walking in place",
        "turn_right": "Turn your body 180° to the right while walking in place",
        "stop": "Come to a complete stop from walking"
    }
    
    instruction = gesture_instructions.get(gesture, "Perform the gesture naturally")
    print_instruction(f"Gesture: {instruction}")
    print()
    
    for i in range(num_samples):
        print(f"\n{Colors.BOLD}Sample {i + 1} of {num_samples}{Colors.ENDC}")
        wait_for_user(f"Press [Enter] when ready for sample {i + 1}...")
        
        # Countdown
        print("  Get ready...")
        time.sleep(1)
        print("  3...")
        time.sleep(1)
        print("  2...")
        time.sleep(1)
        print("  1...")
        time.sleep(1)
        print(f"  {Colors.OKGREEN}{Colors.BOLD}GO!{Colors.ENDC}")
        
        # Collect data
        data_packets = collect_sensor_data(sock, duration_sec)
        
        if len(data_packets) == 0:
            print_warning("No data received! Make sure the watch app is streaming.")
            retry = input("Retry this sample? (y/n): ").lower()
            if retry == 'y':
                i -= 1  # Redo this sample
                continue
        
        # Save data
        metadata = {
            "stance": stance,
            "gesture": gesture,
            "sample_number": i + 1,
            "duration_seconds": duration_sec,
            "timestamp": datetime.now().isoformat(),
            "packet_count": len(data_packets)
        }
        
        save_gesture_data(base_dir, stance, gesture, i + 1, data_packets, metadata)
        
        # Brief pause between samples
        if i < num_samples - 1:
            print()
            print("  Rest for a moment...")
            time.sleep(2)
    
    print_success(f"Completed all samples for {gesture}!")


def main():
    """Main function to orchestrate the data collection session."""
    
    # Print welcome banner
    print_banner("IMU GESTURE DATA COLLECTION - PHASE II", Colors.HEADER)
    print("Welcome to the guided data collection procedure.")
    print("This tool will help you create a high-quality IMU gesture dataset.")
    print()
    
    # Load configuration and setup network
    print("🔍 Loading configuration...")
    config = load_config()
    
    print("🔍 Auto-detecting IP address...")
    network_utils.update_config_ip()
    config = load_config()  # Reload with updated IP
    
    listen_ip = config["network"]["listen_ip"]
    listen_port = config["network"]["listen_port"]
    
    print_success(f"Will listen on {listen_ip}:{listen_port}")
    print()
    
    # Setup socket
    print("🔌 Setting up UDP socket...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((listen_ip, listen_port))
        sock.setblocking(False)
        print_success("Socket ready")
    except OSError as e:
        print_error(f"Could not bind to {listen_ip}:{listen_port}")
        print_error(f"Error: {e}")
        print()
        print("This usually means:")
        print("  • The port is already in use (close udp_listener.py if running)")
        print("  • Another process is using this port")
        sock.close()
        return
    
    # Create data directory structure
    print()
    print("📁 Creating data directory structure...")
    base_dir, timestamp = setup_data_directory()
    print_success(f"Data will be saved to: {base_dir}")
    
    # Explain the protocol
    explain_stances()
    explain_data_collection_protocol()
    
    # Session configuration
    print_banner("SESSION CONFIGURATION", Colors.OKBLUE)
    
    try:
        num_samples = int(input("Number of samples per gesture (default: 5): ") or "5")
        duration = float(input("Duration per sample in seconds (default: 3.0): ") or "3.0")
    except ValueError:
        print_warning("Invalid input, using defaults")
        num_samples = 5
        duration = 3.0
    
    print()
    print(f"Configuration: {num_samples} samples × {duration}s per gesture")
    wait_for_user()
    
    # Save session metadata
    session_metadata = {
        "session_timestamp": timestamp,
        "session_start": datetime.now().isoformat(),
        "listen_ip": listen_ip,
        "listen_port": listen_port,
        "samples_per_gesture": num_samples,
        "duration_per_sample": duration,
        "sensors_expected": [
            "rotation_vector",
            "linear_acceleration",
            "gravity"
        ]
    }
    
    # Define collection sequence
    collection_sequence = [
        # Combat stance gestures
        ("combat", ["punch", "slash", "stab"]),
        # Neutral stance gestures
        ("neutral", ["jump", "hop", "crouch"]),
        # Travel stance gestures
        ("travel", ["walk", "turn_left", "turn_right", "stop"])
    ]
    
    # Main data collection loop
    try:
        for stance, gestures in collection_sequence:
            print_banner(f"STANCE: {stance.upper()}", Colors.WARNING)
            
            # Stance-specific reminder
            if stance == "combat":
                print_instruction("⚔️  COMBAT STANCE: Hold watch arm as if wielding a weapon")
            elif stance == "neutral":
                print_instruction("🧍 NEUTRAL STANCE: Natural standing, watch face up")
            elif stance == "travel":
                print_instruction("🚶 TRAVEL STANCE: Natural walking position")
            
            wait_for_user()
            
            for gesture in gestures:
                collect_gesture_samples(
                    sock, base_dir, stance, gesture, 
                    num_samples=num_samples, 
                    duration_sec=duration
                )
                
                print()
                time.sleep(1)  # Brief pause between gestures
        
        # Update session metadata with completion time
        session_metadata["session_end"] = datetime.now().isoformat()
        save_metadata(base_dir, session_metadata)
        
        # Final summary
        print_banner("DATA COLLECTION COMPLETE!", Colors.OKGREEN)
        print(f"All data saved to: {base_dir}")
        print()
        print("Next steps:")
        print("  1. Review the collected data for quality")
        print("  2. Use this data to train gesture recognition models")
        print("  3. Analyze sensor patterns and signatures")
        print()
        print_success("Thank you for your participation!")
        
    except KeyboardInterrupt:
        print()
        print_warning("Data collection interrupted by user")
        session_metadata["session_end"] = datetime.now().isoformat()
        session_metadata["status"] = "interrupted"
        save_metadata(base_dir, session_metadata)
    
    finally:
        sock.close()
        print()
        print("🔌 Socket closed")


if __name__ == "__main__":
    main()
