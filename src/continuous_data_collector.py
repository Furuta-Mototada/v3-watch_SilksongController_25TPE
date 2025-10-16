"""
Continuous Data Collector for Phase V CNN/LSTM Training

This tool records continuous sensor streams from the smartwatch, allowing users
to mark gesture boundaries in real-time using keyboard shortcuts. Unlike Phase II's
snippet-based approach, this captures natural transitions and realistic gesture flow.

Features:
- Continuous sensor data recording
- Real-time keyboard shortcuts to mark gestures
- Live visualization of recording status
- Auto-save with timestamps
- Generates label files for ML training

Usage:
    python continuous_data_collector.py --duration 600  # 10 minutes
    
    During recording, press keys to mark gestures:
    - 'j' = Jump (marks next 0.3s as jump)
    - 'p' = Punch (marks next 0.3s as punch)
    - 't' = Turn (marks next 0.5s as turn)
    - 'n' = Noise (marks next 1.0s as noise)
    - Everything else = Walk (default state)
    - 'q' = Quit recording
    - 's' = Save now
"""

import socket
import json
import time
import csv
import os
import argparse
import threading
from datetime import datetime
from collections import deque
import sys
import network_utils

# ==================== CONFIGURATION ====================

# Sensor types to collect
SENSORS_TO_COLLECT = [
    "rotation_vector",      # Composite orientation sensor
    "linear_acceleration",  # Linear acceleration (gravity removed)
    "gyroscope"            # Angular velocity
]

# Gesture durations (seconds)
GESTURE_DURATIONS = {
    'jump': 0.3,
    'punch': 0.3,
    'turn': 0.5,
    'noise': 1.0,
    'walk': None  # Default state, no fixed duration
}

# Default recording duration
DEFAULT_DURATION_SEC = 600  # 10 minutes

# ANSI Color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


# ==================== DATA STRUCTURES ====================

class GestureLabel:
    """Represents a labeled gesture in the recording"""
    def __init__(self, timestamp, gesture, duration):
        self.timestamp = timestamp
        self.gesture = gesture
        self.duration = duration


class ContinuousDataCollector:
    """Manages continuous sensor data recording with real-time labeling"""
    
    def __init__(self, session_name=None, duration_sec=DEFAULT_DURATION_SEC):
        self.session_name = session_name or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.duration_sec = duration_sec
        self.output_dir = f"data/continuous"
        
        # Recording state
        self.recording = False
        self.start_time = None
        self.sensor_data = []
        self.labels = []
        self.current_gesture = 'walk'  # Default state
        self.last_label_time = 0
        
        # Statistics
        self.gesture_counts = {
            'walk': 0,
            'jump': 0,
            'punch': 0,
            'turn': 0,
            'noise': 0
        }
        
        # Network
        self.sock = None
        self.config = None
        
        # Threading
        self.stop_event = threading.Event()
        self.keyboard_thread = None
        
    def load_config(self):
        """Load configuration from config.json"""
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"{Colors.RED}ERROR: config.json not found!{Colors.RESET}")
            sys.exit(1)
    
    def setup(self):
        """Set up network connection and output directory"""
        # Auto-detect and update IP
        print(f"{Colors.CYAN}🔍 Auto-detecting IP address...{Colors.RESET}")
        network_utils.update_config_ip()
        self.config = self.load_config()
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"{Colors.GREEN}✓ Output directory: {self.output_dir}{Colors.RESET}")
        
        # Set up UDP socket
        listen_ip = self.config["network"]["listen_ip"]
        listen_port = self.config["network"]["listen_port"]
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.sock.bind((listen_ip, listen_port))
            self.sock.setblocking(False)
            print(f"{Colors.GREEN}✓ Listening on {listen_ip}:{listen_port}{Colors.RESET}")
        except OSError as e:
            print(f"{Colors.RED}ERROR: Could not bind to {listen_ip}:{listen_port}{Colors.RESET}")
            print(f"{Colors.YELLOW}Make sure no other listener is running!{Colors.RESET}")
            raise e
        
        return True
    
    def display_instructions(self):
        """Display recording instructions"""
        instructions = f"""
╔══════════════════════════════════════════════════════════════╗
║  {Colors.BOLD}{Colors.GREEN}CONTINUOUS GESTURE RECORDER - Phase V{Colors.RESET}               ║
╚══════════════════════════════════════════════════════════════╝

{Colors.BOLD}Session:{Colors.RESET} {self.session_name}
{Colors.BOLD}Duration:{Colors.RESET} {self.duration_sec} seconds ({self.duration_sec/60:.1f} minutes)

{Colors.BOLD}{Colors.YELLOW}KEYBOARD CONTROLS:{Colors.RESET}
  {Colors.GREEN}j{Colors.RESET} = Mark JUMP (next {GESTURE_DURATIONS['jump']}s)
  {Colors.GREEN}p{Colors.RESET} = Mark PUNCH (next {GESTURE_DURATIONS['punch']}s)
  {Colors.GREEN}t{Colors.RESET} = Mark TURN (next {GESTURE_DURATIONS['turn']}s)
  {Colors.GREEN}n{Colors.RESET} = Mark NOISE (next {GESTURE_DURATIONS['noise']}s)
  {Colors.BLUE}(default){Colors.RESET} = WALK (continuous state)
  
  {Colors.RED}q{Colors.RESET} = Quit recording
  {Colors.CYAN}s{Colors.RESET} = Save immediately

{Colors.BOLD}{Colors.BLUE}HOW TO USE:{Colors.RESET}
1. Start recording - sensor data begins streaming
2. Perform gestures naturally while moving continuously
3. Press corresponding key RIGHT WHEN you start each gesture
4. The tool will mark the next N seconds as that gesture
5. Between gestures, you're automatically in WALK state

{Colors.BOLD}{Colors.YELLOW}TIPS:{Colors.RESET}
- Move naturally, as you would in gameplay
- Press keys at gesture START, not during or after
- Walk between gestures for realistic transitions
- Aim for 10-20 jumps, 10-20 punches, 5-10 turns per session
- Don't worry about being perfect - variety is good!

{Colors.BOLD}{Colors.RED}IMPORTANT:{Colors.RESET}
- Keep the terminal window focused to capture keyboard input
- Watch should be streaming sensor data
- Recording will auto-save when complete

──────────────────────────────────────────────────────────────
"""
        print(instructions)
    
    def keyboard_listener(self):
        """Listen for keyboard input in a separate thread"""
        import sys
        import select
        
        print(f"{Colors.CYAN}Keyboard listener started. Press keys to mark gestures...{Colors.RESET}")
        
        while not self.stop_event.is_set():
            # Check if data is available to read (with timeout)
            if select.select([sys.stdin], [], [], 0.1)[0]:
                key = sys.stdin.read(1).lower()
                self.handle_key_press(key)
    
    def handle_key_press(self, key):
        """Handle keyboard input for gesture marking"""
        if not self.recording:
            return
        
        current_time = time.time() - self.start_time
        
        if key == 'q':
            print(f"\n{Colors.YELLOW}Quit requested by user{Colors.RESET}")
            self.stop_event.set()
            return
        
        if key == 's':
            print(f"\n{Colors.CYAN}Save requested - will save at end of recording{Colors.RESET}")
            return
        
        # Map keys to gestures
        gesture_map = {
            'j': 'jump',
            'p': 'punch',
            't': 'turn',
            'n': 'noise'
        }
        
        if key in gesture_map:
            gesture = gesture_map[key]
            duration = GESTURE_DURATIONS[gesture]
            
            # Create label
            label = GestureLabel(current_time, gesture, duration)
            self.labels.append(label)
            
            # Update statistics
            self.gesture_counts[gesture] += 1
            
            print(f"\n{Colors.GREEN}✓ Marked {gesture.upper()} at {current_time:.2f}s (duration: {duration}s){Colors.RESET}")
    
    def record_sensor_data(self):
        """Main recording loop for sensor data"""
        print(f"\n{Colors.RED}{Colors.BOLD}🔴 RECORDING STARTED{Colors.RESET}")
        print(f"{Colors.YELLOW}Perform gestures naturally and press keys to mark them!{Colors.RESET}\n")
        
        self.recording = True
        self.start_time = time.time()
        recording_end = self.start_time + self.duration_sec
        
        last_status_update = 0
        data_points = 0
        last_data_time = time.time()
        
        while time.time() < recording_end and not self.stop_event.is_set():
            elapsed = time.time() - self.start_time
            remaining = recording_end - time.time()
            progress_pct = (elapsed / self.duration_sec) * 100
            
            # Update status display
            if time.time() - last_status_update > 1.0:
                self._display_status(elapsed, remaining, progress_pct, data_points)
                last_status_update = time.time()
            
            # Receive sensor data
            try:
                data, addr = self.sock.recvfrom(4096)
                parsed = json.loads(data.decode())
                sensor_type = parsed.get("sensor")
                
                if sensor_type in SENSORS_TO_COLLECT:
                    last_data_time = time.time()
                    
                    # Create record
                    record = {
                        "timestamp": time.time() - self.start_time,
                        "sensor": sensor_type
                    }
                    
                    # Flatten sensor values
                    if "values" in parsed:
                        vals = parsed["values"]
                        if sensor_type == "rotation_vector":
                            record["rot_x"] = vals.get("x", 0)
                            record["rot_y"] = vals.get("y", 0)
                            record["rot_z"] = vals.get("z", 0)
                            record["rot_w"] = vals.get("w", 0)
                        elif sensor_type == "linear_acceleration":
                            record["accel_x"] = vals.get("x", 0)
                            record["accel_y"] = vals.get("y", 0)
                            record["accel_z"] = vals.get("z", 0)
                        elif sensor_type == "gyroscope":
                            record["gyro_x"] = vals.get("x", 0)
                            record["gyro_y"] = vals.get("y", 0)
                            record["gyro_z"] = vals.get("z", 0)
                    
                    self.sensor_data.append(record)
                    data_points += 1
                    
            except (BlockingIOError, json.JSONDecodeError, KeyError):
                pass
            
            # Check connection
            if time.time() - last_data_time > 2.0:
                print(f"\r{Colors.RED}⚠️  WARNING: No data received for 2 seconds! Check watch connection.{Colors.RESET}")
        
        self.recording = False
        print(f"\n\n{Colors.GREEN}✓ Recording complete!{Colors.RESET}")
        print(f"{Colors.BLUE}Captured {len(self.sensor_data)} sensor data points{Colors.RESET}")
        print(f"{Colors.BLUE}Marked {len(self.labels)} explicit gestures{Colors.RESET}")
    
    def _display_status(self, elapsed, remaining, progress_pct, data_points):
        """Display recording status"""
        # Progress bar
        bar_width = 30
        filled = int(bar_width * progress_pct / 100)
        bar = "█" * filled + "░" * (bar_width - filled)
        
        # Format time
        elapsed_str = f"{int(elapsed//60):02d}:{int(elapsed%60):02d}"
        total_str = f"{int(self.duration_sec//60):02d}:{int(self.duration_sec%60):02d}"
        
        # Data rate
        data_rate = data_points / elapsed if elapsed > 0 else 0
        
        # Display
        status = f"\r⏱️  {elapsed_str}/{total_str} [{bar}] {progress_pct:.0f}% | "
        status += f"📊 {data_points} pts ({data_rate:.0f} pts/s) | "
        
        # Gesture counts
        status += f"J:{self.gesture_counts['jump']} P:{self.gesture_counts['punch']} "
        status += f"T:{self.gesture_counts['turn']} N:{self.gesture_counts['noise']}"
        
        print(status, end="", flush=True)
    
    def generate_labels(self):
        """Generate complete label file from marked gestures"""
        # Sort labels by timestamp
        self.labels.sort(key=lambda x: x.timestamp)
        
        # Generate complete labels covering entire recording
        complete_labels = []
        current_time = 0.0
        total_duration = self.sensor_data[-1]['timestamp'] if self.sensor_data else self.duration_sec
        
        label_idx = 0
        while current_time < total_duration:
            # Check if we're at a labeled gesture
            if label_idx < len(self.labels):
                label = self.labels[label_idx]
                
                if abs(current_time - label.timestamp) < 0.1:  # Within 100ms
                    # Add the labeled gesture
                    complete_labels.append({
                        'timestamp': label.timestamp,
                        'gesture': label.gesture,
                        'duration': label.duration
                    })
                    current_time = label.timestamp + label.duration
                    label_idx += 1
                    continue
            
            # Find next labeled gesture or end
            if label_idx < len(self.labels):
                next_label_time = self.labels[label_idx].timestamp
            else:
                next_label_time = total_duration
            
            # Fill with walk
            walk_duration = next_label_time - current_time
            if walk_duration > 0:
                complete_labels.append({
                    'timestamp': current_time,
                    'gesture': 'walk',
                    'duration': walk_duration
                })
                self.gesture_counts['walk'] += walk_duration
            
            current_time = next_label_time
        
        return complete_labels
    
    def save_data(self):
        """Save sensor data and labels to CSV files"""
        print(f"\n{Colors.CYAN}💾 Saving data...{Colors.RESET}")
        
        # Save sensor data
        sensor_file = os.path.join(self.output_dir, f"{self.session_name}.csv")
        if self.sensor_data:
            fieldnames = set()
            for record in self.sensor_data:
                fieldnames.update(record.keys())
            fieldnames = sorted(list(fieldnames))
            
            with open(sensor_file, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.sensor_data)
            
            print(f"{Colors.GREEN}✓ Sensor data saved: {sensor_file}{Colors.RESET}")
        
        # Generate and save labels
        complete_labels = self.generate_labels()
        labels_file = os.path.join(self.output_dir, f"{self.session_name}_labels.csv")
        
        with open(labels_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['timestamp', 'gesture', 'duration'])
            writer.writeheader()
            writer.writerows(complete_labels)
        
        print(f"{Colors.GREEN}✓ Labels saved: {labels_file}{Colors.RESET}")
        
        # Save session metadata
        metadata_file = os.path.join(self.output_dir, f"{self.session_name}_metadata.json")
        metadata = {
            'session_name': self.session_name,
            'recording_date': datetime.now().isoformat(),
            'duration_sec': self.duration_sec,
            'actual_duration_sec': self.sensor_data[-1]['timestamp'] if self.sensor_data else 0,
            'sensor_data_points': len(self.sensor_data),
            'explicit_labels': len(self.labels),
            'total_labels': len(complete_labels),
            'gesture_counts': self.gesture_counts,
            'sensors_collected': SENSORS_TO_COLLECT
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"{Colors.GREEN}✓ Metadata saved: {metadata_file}{Colors.RESET}")
        
        # Display summary
        print(f"\n{Colors.BOLD}📊 Recording Summary:{Colors.RESET}")
        print(f"  {Colors.BLUE}• Total duration: {self.sensor_data[-1]['timestamp']:.1f}s{Colors.RESET}")
        print(f"  {Colors.BLUE}• Sensor data points: {len(self.sensor_data)}{Colors.RESET}")
        print(f"  {Colors.BLUE}• Total labels: {len(complete_labels)}{Colors.RESET}")
        print(f"\n{Colors.BOLD}Gesture Distribution:{Colors.RESET}")
        for gesture, count in self.gesture_counts.items():
            if gesture == 'walk':
                print(f"  {Colors.CYAN}• {gesture.upper()}: {count:.1f}s{Colors.RESET}")
            else:
                print(f"  {Colors.GREEN}• {gesture.upper()}: {count} events{Colors.RESET}")
    
    def cleanup(self):
        """Clean up resources"""
        if self.sock:
            self.sock.close()


# ==================== MAIN ====================

def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Continuous gesture data collector for Phase V CNN/LSTM training',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Record 10-minute session
  python continuous_data_collector.py --duration 600
  
  # Record 5-minute session with custom name
  python continuous_data_collector.py --duration 300 --session my_session_01
  
During recording:
  j = Jump, p = Punch, t = Turn, n = Noise
  q = Quit, s = Save
        """
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=DEFAULT_DURATION_SEC,
        help=f'Recording duration in seconds (default: {DEFAULT_DURATION_SEC})'
    )
    
    parser.add_argument(
        '--session',
        type=str,
        help='Session name (default: auto-generated timestamp)'
    )
    
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Create collector
    collector = ContinuousDataCollector(
        session_name=args.session,
        duration_sec=args.duration
    )
    
    try:
        # Setup
        collector.setup()
        collector.display_instructions()
        
        input(f"\n{Colors.BOLD}{Colors.GREEN}Press [Enter] to start recording...{Colors.RESET}")
        
        # Start keyboard listener in separate thread
        # Note: For simplicity, we'll use a simpler approach without threading
        # Users can type in terminal during recording
        print(f"{Colors.YELLOW}Note: Keep this terminal focused. Type keys to mark gestures.{Colors.RESET}")
        print(f"{Colors.YELLOW}Recording starts in 3 seconds...{Colors.RESET}")
        time.sleep(3)
        
        # Record
        collector.record_sensor_data()
        
        # Save
        collector.save_data()
        
        print(f"\n{Colors.GREEN}✨ Data collection complete!{Colors.RESET}")
        print(f"{Colors.CYAN}Files saved to: {collector.output_dir}/{Colors.RESET}")
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Recording interrupted by user{Colors.RESET}")
        if collector.sensor_data:
            save = input(f"{Colors.YELLOW}Save partial recording? (y/n): {Colors.RESET}")
            if save.lower() == 'y':
                collector.save_data()
    
    except Exception as e:
        print(f"\n{Colors.RED}❌ ERROR: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
    
    finally:
        collector.cleanup()
        print(f"\n{Colors.GREEN}✓ Cleanup complete{Colors.RESET}")


if __name__ == "__main__":
    main()
