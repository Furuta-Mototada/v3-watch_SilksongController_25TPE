"""
Data Collection Script for IMU Gesture Recognition Training Data

This script guides users through a structured data collection process for 
capturing high-fidelity IMU sensor data from the Wear OS smartwatch. The collected
data will be used to train machine learning models for gesture recognition.

Phase II: Guided Data Collection Procedure
- Defines clear user stances
- Provides unambiguous gesture execution instructions
- Records labeled time-series sensor data
- Exports data in ML-ready format (CSV)
"""

import socket
import json
import time
import csv
import os
from datetime import datetime
from collections import deque
import network_utils


# ==================== CONFIGURATION ====================

# Sensor types we'll collect
SENSORS_TO_COLLECT = [
    "rotation_vector",      # Composite orientation sensor
    "linear_acceleration",  # Linear acceleration (gravity removed)
    "gyroscope"            # Angular velocity
]

# Data collection parameters
RECORDING_DURATION_SEC = 3.0  # Duration to record each gesture
COUNTDOWN_SEC = 3  # Countdown before recording starts
SAMPLES_PER_GESTURE = 5  # Number of repetitions per gesture

# ==================== STANCE DEFINITIONS ====================

STANCES = {
    "combat": {
        "name": "Combat Stance",
        "description": """
╔════════════════════════════════════════════════════════════════╗
║                        COMBAT STANCE                           ║
╚════════════════════════════════════════════════════════════════╝

Hold your arm as if wielding a weapon:
  • Forearm extended forward, elbow at ~90 degrees
  • Watch face oriented SIDEWAYS (not facing up or down)
  • Arm at shoulder height or slightly below
  • Comfortable position that you can hold for 1-2 minutes

This is the stance for ATTACK gestures.
        """,
    },
    "neutral": {
        "name": "Neutral Stance", 
        "description": """
╔════════════════════════════════════════════════════════════════╗
║                        NEUTRAL STANCE                          ║
╚════════════════════════════════════════════════════════════════╝

Hold your arm in a natural, relaxed position:
  • Arm down at your side OR slightly bent
  • Watch face oriented UP (towards the sky)
  • Relaxed, natural position
  • Easy to maintain without fatigue

This is the stance for JUMP gestures.
        """,
    },
    "travel": {
        "name": "Travel Stance",
        "description": """
╔════════════════════════════════════════════════════════════════╗
║                        TRAVEL STANCE                           ║
╚════════════════════════════════════════════════════════════════╝

Hold your arm in a walking/running position:
  • Arm swinging naturally as if walking
  • Watch face can be in any comfortable orientation
  • Position that allows natural arm movement
  • Comfortable for sustained motion

This is the stance for WALK and TURN gestures.
        """,
    }
}

# ==================== GESTURE DEFINITIONS ====================

GESTURES = {
    "punch_forward": {
        "name": "Punch Forward",
        "stance": "combat",
        "description": """
Execute a sharp, forward PUNCH motion:
  • From combat stance, thrust your fist forward
  • Motion should be crisp and deliberate
  • Return to combat stance after the punch
  • Think of striking a target in front of you
        """,
    },
    "punch_upward": {
        "name": "Punch Upward",
        "stance": "combat",
        "description": """
Execute an upward UPPERCUT punch motion:
  • From combat stance, drive your fist upward
  • Motion should be sharp and vertical
  • Return to combat stance after the punch
  • Think of striking upward at an opponent's chin
        """,
    },
    "jump_quick": {
        "name": "Quick Jump",
        "stance": "neutral",
        "description": """
Execute a quick, sharp HOP motion:
  • From neutral stance, make a small, quick upward hop
  • Keep the motion crisp and vertical
  • Land softly and return to neutral stance
  • Think of a light, responsive jump action
        """,
    },
    "jump_sustained": {
        "name": "Sustained Jump",
        "stance": "neutral",
        "description": """
Execute a deliberate, upward JUMP motion:
  • From neutral stance, make a full upward jump
  • Hold your arm up briefly at the peak
  • Land and return to neutral stance
  • Think of reaching for something overhead
        """,
    },
    "walk_in_place": {
        "name": "Walk In Place",
        "stance": "travel",
        "description": """
Walk in place with natural arm swing:
  • From travel stance, begin walking in place
  • Let your arm swing naturally
  • Maintain a steady, comfortable rhythm
  • Continue for the full recording duration
        """,
    },
    "turn_left": {
        "name": "Turn Left (Body)",
        "stance": "travel",
        "description": """
Execute a 180-degree body turn to the LEFT:
  • Start from travel stance, facing forward
  • Turn your entire body 180 degrees to the LEFT
  • Keep your arm in travel position during the turn
  • Complete the turn smoothly but deliberately
        """,
    },
    "turn_right": {
        "name": "Turn Right (Body)",
        "stance": "travel",
        "description": """
Execute a 180-degree body turn to the RIGHT:
  • Start from travel stance, facing forward
  • Turn your entire body 180 degrees to the RIGHT
  • Keep your arm in travel position during the turn
  • Complete the turn smoothly but deliberately
        """,
    },
    "rest": {
        "name": "Rest (No Motion)",
        "stance": "neutral",
        "description": """
Remain completely STILL:
  • From neutral stance, keep arm completely motionless
  • Do not move your watch hand at all
  • Breathe normally but avoid arm movement
  • This captures baseline "no gesture" data
        """,
    },
}

# ==================== DATA COLLECTION CLASS ====================

class DataCollector:
    """Manages the data collection session and file I/O."""
    
    def __init__(self):
        self.config = self.load_config()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"training_data/session_{self.session_id}"
        self.sock = None
        self.current_recording = []
        
    def load_config(self):
        """Load configuration from config.json."""
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("ERROR: config.json not found!")
            exit(1)
    
    def setup(self):
        """Set up network connection and output directory."""
        # Auto-detect and update IP
        print("🔍 Auto-detecting IP address...")
        network_utils.update_config_ip()
        self.config = self.load_config()
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"✓ Output directory created: {self.output_dir}")
        
        # Set up UDP socket
        listen_ip = self.config["network"]["listen_ip"]
        listen_port = self.config["network"]["listen_port"]
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.sock.bind((listen_ip, listen_port))
            self.sock.setblocking(False)
            print(f"✓ Listening on {listen_ip}:{listen_port}")
        except OSError as e:
            print(f"\nERROR: Could not bind to {listen_ip}:{listen_port}")
            print("Make sure udp_listener.py is NOT running!")
            raise e
        
        return True
    
    def display_instructions(self, message):
        """Display instructions and wait for user acknowledgment."""
        print("\n" + "=" * 70)
        print(message)
        print("=" * 70)
        input("\nPress [Enter] when ready to continue...")
    
    def display_stance(self, stance_key):
        """Display stance definition."""
        stance = STANCES[stance_key]
        print("\n" + "╔" + "═" * 68 + "╗")
        print(f"║  Please adopt: {stance['name'].upper():<50} ║")
        print("╚" + "═" * 68 + "╝")
        print(stance["description"])
        input("\nPress [Enter] when you have adopted this stance...")
    
    def record_gesture(self, gesture_key, sample_num):
        """Record a single gesture execution."""
        gesture = GESTURES[gesture_key]
        
        print("\n" + "─" * 70)
        print(f"Recording: {gesture['name']} - Sample {sample_num}/{SAMPLES_PER_GESTURE}")
        print("─" * 70)
        print(gesture["description"])
        
        input("\nPress [Enter] when ready to execute this gesture...")
        
        # Countdown
        for i in range(COUNTDOWN_SEC, 0, -1):
            print(f"  {i}...")
            time.sleep(1)
        
        print("\n  🔴 RECORDING - EXECUTE GESTURE NOW!")
        
        # Clear any buffered data
        self._flush_socket()
        
        # Record data
        self.current_recording = []
        start_time = time.time()
        recording_end = start_time + RECORDING_DURATION_SEC
        
        while time.time() < recording_end:
            remaining = recording_end - time.time()
            print(f"\r  ⏱️  Recording... {remaining:.1f}s remaining", end="", flush=True)
            
            try:
                data, addr = self.sock.recvfrom(4096)
                parsed = json.loads(data.decode())
                sensor_type = parsed.get("sensor")
                
                if sensor_type in SENSORS_TO_COLLECT:
                    # Add timestamp and label
                    record = {
                        "timestamp": time.time() - start_time,
                        "sensor": sensor_type,
                        "gesture": gesture_key,
                        "stance": gesture["stance"],
                        "sample": sample_num,
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
                    
                    self.current_recording.append(record)
                    
            except (BlockingIOError, json.JSONDecodeError, KeyError):
                pass
        
        print("\n  ✓ Recording complete!")
        
        # Check if we got data
        if len(self.current_recording) == 0:
            print("\n  ⚠️  WARNING: No data recorded! Check your watch connection.")
            return False
        
        print(f"  📊 Captured {len(self.current_recording)} data points")
        
        # Save to CSV
        self._save_recording(gesture_key, sample_num)
        
        return True
    
    def _flush_socket(self):
        """Clear any buffered data from the socket."""
        try:
            while True:
                self.sock.recvfrom(4096)
        except BlockingIOError:
            pass
    
    def _save_recording(self, gesture_key, sample_num):
        """Save the current recording to a CSV file."""
        filename = f"{gesture_key}_sample{sample_num:02d}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        if len(self.current_recording) == 0:
            return
        
        # Determine all possible fields
        fieldnames = set()
        for record in self.current_recording:
            fieldnames.update(record.keys())
        
        fieldnames = sorted(list(fieldnames))
        
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.current_recording)
        
        print(f"  💾 Saved: {filename}")
    
    def save_session_metadata(self, gestures_completed):
        """Save metadata about this collection session."""
        metadata = {
            "session_id": self.session_id,
            "date": datetime.now().isoformat(),
            "recording_duration_sec": RECORDING_DURATION_SEC,
            "samples_per_gesture": SAMPLES_PER_GESTURE,
            "sensors_collected": SENSORS_TO_COLLECT,
            "gestures_completed": gestures_completed,
            "config": self.config
        }
        
        filepath = os.path.join(self.output_dir, "session_metadata.json")
        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n💾 Session metadata saved: {filepath}")
    
    def cleanup(self):
        """Clean up resources."""
        if self.sock:
            self.sock.close()


# ==================== MAIN COLLECTION FLOW ====================

def main():
    """Main data collection workflow."""
    
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  SILKSONG CONTROLLER - PHASE II DATA COLLECTION".center(68) + "║")
    print("║" + "  IMU Gesture Training Data Acquisition".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    
    welcome_message = """
Welcome to the guided data collection procedure!

This tool will help you collect high-quality IMU sensor data for training
a machine learning gesture recognition model.

WHAT TO EXPECT:
  • You will be guided through different physical stances
  • For each stance, you'll perform specific gestures
  • Each gesture will be repeated 5 times
  • Clear instructions will be provided before each recording
  • The entire process takes approximately 20-30 minutes

REQUIREMENTS:
  • Your Wear OS watch must be connected and streaming sensor data
  • Find a clear space where you can move freely
  • Have water nearby - you'll be moving!
  • Ensure your watch is securely fastened to your wrist

TIPS FOR QUALITY DATA:
  • Execute gestures deliberately and consistently
  • Return to the specified stance between gestures
  • Take breaks if you feel fatigued
  • If you make a mistake, that's okay - we'll record multiple samples
    """
    
    print(welcome_message)
    input("\nPress [Enter] to begin setup...")
    
    # Initialize collector
    collector = DataCollector()
    
    try:
        collector.setup()
        
        # Connection check
        print("\n" + "─" * 70)
        print("CONNECTION CHECK")
        print("─" * 70)
        print("Checking if watch is sending data...")
        print("Please make sure streaming is ON in your watch app.")
        
        # Wait for first packet
        timeout = 15
        start_wait = time.time()
        received_data = False
        
        while time.time() - start_wait < timeout:
            try:
                data, _ = collector.sock.recvfrom(4096)
                parsed = json.loads(data.decode())
                if parsed.get("sensor") in SENSORS_TO_COLLECT:
                    received_data = True
                    break
            except (BlockingIOError, json.JSONDecodeError, KeyError):
                time.sleep(0.1)
        
        if not received_data:
            print("\n❌ ERROR: No sensor data received from watch!")
            print("Please ensure:")
            print("  1. Watch app is open")
            print("  2. Streaming toggle is ON")
            print("  3. Both devices are on the same network")
            return
        
        print("✓ Connection verified! Receiving sensor data.")
        
        # Flush buffer before starting
        collector._flush_socket()
        
        # Main collection loop - organized by stance
        gestures_by_stance = {}
        for gesture_key, gesture in GESTURES.items():
            stance = gesture["stance"]
            if stance not in gestures_by_stance:
                gestures_by_stance[stance] = []
            gestures_by_stance[stance].append(gesture_key)
        
        gestures_completed = []
        
        for stance_key in ["combat", "neutral", "travel"]:
            if stance_key not in gestures_by_stance:
                continue
            
            # Display stance
            collector.display_stance(stance_key)
            
            # Collect all gestures for this stance
            for gesture_key in gestures_by_stance[stance_key]:
                gesture = GESTURES[gesture_key]
                
                print("\n" + "═" * 70)
                print(f"  GESTURE: {gesture['name'].upper()}")
                print("═" * 70)
                
                # Collect multiple samples
                for sample_num in range(1, SAMPLES_PER_GESTURE + 1):
                    success = collector.record_gesture(gesture_key, sample_num)
                    
                    if not success:
                        retry = input("\n  Try recording this sample again? (y/n): ")
                        if retry.lower() == 'y':
                            success = collector.record_gesture(gesture_key, sample_num)
                    
                    if success:
                        # Brief pause between samples
                        if sample_num < SAMPLES_PER_GESTURE:
                            print("\n  Take a moment to reset to stance...")
                            time.sleep(2)
                
                gestures_completed.append(gesture_key)
                
                # Break between gestures
                print("\n  ✓ Gesture complete! Take a short break if needed.")
                cont = input("  Press [Enter] to continue to next gesture (or 'q' to quit)...")
                if cont.lower() == 'q':
                    break
            
            # Break between stances
            if stance_key != "travel":  # Don't break after the last stance
                print("\n" + "═" * 70)
                print("  STANCE COMPLETE!")
                print("═" * 70)
                print("  Take a longer break. Stretch, have some water.")
                input("  Press [Enter] when ready for the next stance...")
        
        # Save session metadata
        collector.save_session_metadata(gestures_completed)
        
        # Final summary
        print("\n" + "╔" + "═" * 68 + "╗")
        print("║" + " " * 68 + "║")
        print("║" + "  DATA COLLECTION COMPLETE!".center(68) + "║")
        print("║" + " " * 68 + "║")
        print("╚" + "═" * 68 + "╝")
        
        print(f"\n📊 Session Summary:")
        print(f"   • Session ID: {collector.session_id}")
        print(f"   • Gestures collected: {len(gestures_completed)}")
        print(f"   • Samples per gesture: {SAMPLES_PER_GESTURE}")
        print(f"   • Output directory: {collector.output_dir}")
        
        print("\n✨ Your training data is ready for the next phase: Model Training!")
        print(f"   All files have been saved to: {collector.output_dir}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Data collection interrupted by user.")
        print("Partial data has been saved.")
    
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        collector.cleanup()
        print("\n✓ Cleanup complete. Thank you!")


if __name__ == "__main__":
    main()
