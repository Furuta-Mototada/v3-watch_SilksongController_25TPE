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
RECORDING_DURATION_SEC = 2.5  # Duration to record each gesture
COUNTDOWN_SEC = 3  # Countdown before recording starts
SAMPLES_PER_GESTURE = 40  # Number of repetitions per gesture
NOISE_SAMPLES = 80  # Oversample NOISE for robustness (2x target gestures)

# Connection monitoring
CONNECTION_TIMEOUT_SEC = 2.0  # Time without data before connection lost

# ANSI Color codes for terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

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
# CRITICAL: This is a SIMPLIFIED 5-CLASS classification problem
# Classes: PUNCH, JUMP, TURN, WALK, and NOISE (the "Stray Catcher")
#
# Philosophy: We don't need to distinguish between "typing" and "drinking."
# We only need to know: "Is this one of the 4 sacred gestures? If not, ignore it."

GESTURES = {
    # ═══════════════════════════════════════════════════════════
    # TARGET GESTURE CLASS 1: PUNCH
    # ═══════════════════════════════════════════════════════════
    "punch": {
        "name": "Punch",
        "stance": "combat",
        "class_label": "PUNCH",
        "description": """
Execute a sharp, forward PUNCH motion:
  • From combat stance, thrust your fist forward
  • Motion should be crisp and deliberate
  • Return to combat stance after the punch
  • Think of striking a target in front of you
        """,
    },

    # ═══════════════════════════════════════════════════════════
    # TARGET GESTURE CLASS 2: JUMP
    # ═══════════════════════════════════════════════════════════
    "jump": {
        "name": "Jump",
        "stance": "neutral",
        "class_label": "JUMP",
        "description": """
Execute a sharp, upward HOP motion:
  • From neutral stance, make a quick upward hop
  • Keep the motion crisp and vertical
  • Land softly and return to neutral stance
  • Your body should leave the ground briefly
        """,
    },

    # ═══════════════════════════════════════════════════════════
    # TARGET GESTURE CLASS 3: TURN
    # ═══════════════════════════════════════════════════════════
    "turn": {
        "name": "Turn (180°)",
        "stance": "travel",
        "class_label": "TURN",
        "description": """
Execute a 180-degree body turn:
  • Start from travel stance, facing forward
  • Turn your entire body 180 degrees (either direction)
  • Keep your arm in travel position during the turn
  • Complete the turn smoothly but deliberately
        """,
    },

    # ═══════════════════════════════════════════════════════════
    # TARGET GESTURE CLASS 4: WALK
    # ═══════════════════════════════════════════════════════════
    "walk": {
        "name": "Walk",
        "stance": "travel",
        "class_label": "WALK",
        "description": """
Walk in place with natural arm swing:
  • From travel stance, begin walking in place
  • Let your arm swing naturally
  • Maintain a steady, comfortable rhythm
  • Continue for the full recording duration
        """,
    },

    # ═══════════════════════════════════════════════════════════
    # THE STRAY CATCHER: NOISE CLASS (Oversampled for robustness)
    # ═══════════════════════════════════════════════════════════
    # This single class contains EVERYTHING ELSE. The goal is VARIETY,
    # not exhaustive cataloging. Each sample will be a different type of
    # confounding movement from the list below.

    "noise": {
        "name": "NOISE (The Stray Catcher)",
        "stance": "neutral",
        "class_label": "NOISE",
        "description": """
Perform ANY confounding movement (NOT one of the 4 target gestures).
The script will randomly select from these categories:

CATEGORY 1 - Resting & Stillness:
  • Remain completely still (baseline "no motion")
  • Relaxed breathing, no arm movement

CATEGORY 2 - Daily Tasks:
  • Simulate typing on a keyboard (small wrist movements)
  • Lift watch hand to mouth (drinking motion)
  • Use watch hand as if holding/scrolling on phone
  • Adjust glasses or hair with watch hand

CATEGORY 3 - Involuntary Motions:
  • Cough or sneeze (sharp body jolt)
  • Shrug shoulders firmly
  • Stretch arm overhead or forward

CATEGORY 4 - Checking & Fidgeting:
  • Rotate wrist to check the time on watch (CRITICAL)
  • Small, random wrist rotations (fidgeting)
  • Scratching other arm or head with watch hand

CATEGORY 5 - False Starts:
  • Weak, incomplete punch (hesitant, not committed)
  • Partial jump (shift weight but don't hop)
  • Small turn (<90 degrees, not a full turn)

For EACH noise sample, the prompt will specify which type to perform.
The goal: teach the model to recognize and REJECT everything except
the 4 sacred gestures.
        """,
    },
}# ==================== DATA COLLECTION CLASS ====================

class DataCollector:
    """Manages the data collection session and file I/O."""

    def __init__(self):
        self.config = self.load_config()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"training_data/session_{self.session_id}"
        self.sock = None
        self.current_recording = []
        self.last_data_time = 0  # Track connection status
        self.connection_active = False

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
        print(f"║  {Colors.BOLD}{Colors.YELLOW}Please adopt: {stance['name'].upper():<50}{Colors.RESET} ║")
        print("╚" + "═" * 68 + "╝")
        print(f"{Colors.BLUE}{stance['description']}{Colors.RESET}")
        input(f"\n{Colors.BOLD}Press [Enter] when you have adopted this stance...{Colors.RESET}")

    def record_gesture(self, gesture_key, sample_num):
        """Record a single gesture execution."""
        gesture = GESTURES[gesture_key]

        print("\n" + "─" * 70)
        print(f"{Colors.BOLD}{Colors.BLUE}Recording: {gesture['name']} - Sample {sample_num}/{SAMPLES_PER_GESTURE}{Colors.RESET}")
        print("─" * 70)
        print(f"{Colors.YELLOW}{gesture['description']}{Colors.RESET}")

        input(f"\n{Colors.BOLD}Press [Enter] when ready to execute this gesture...{Colors.RESET}")

        # Countdown with color
        for i in range(COUNTDOWN_SEC, 0, -1):
            print(f"  {Colors.YELLOW}{i}...{Colors.RESET}")
            time.sleep(1)

        print(f"\n  {Colors.RED}{Colors.BOLD}🔴 RECORDING - EXECUTE GESTURE NOW!{Colors.RESET}")

        # Clear any buffered data and reset connection tracking
        self._flush_socket()
        self.last_data_time = time.time()  # Initialize connection tracking

        # Record data
        self.current_recording = []
        start_time = time.time()
        recording_end = start_time + RECORDING_DURATION_SEC
        last_status_update = 0
        data_points_received = 0

        while time.time() < recording_end:
            remaining = recording_end - time.time()

            # Update connection status every 0.1 seconds
            if time.time() - last_status_update > 0.1:
                connection_status = self._get_connection_status()
                data_rate = data_points_received / (time.time() - start_time) if (time.time() - start_time) > 0 else 0

                status_line = (
                    f"\r  ⏱️  {Colors.BOLD}Recording: {remaining:.1f}s{Colors.RESET} | "
                    f"{connection_status} | "
                    f"{Colors.BLUE}📊 {data_points_received} pts ({data_rate:.0f} pts/s){Colors.RESET}"
                )
                print(status_line, end="", flush=True)
                last_status_update = time.time()

            try:
                data, addr = self.sock.recvfrom(4096)
                parsed = json.loads(data.decode())
                sensor_type = parsed.get("sensor")

                if sensor_type in SENSORS_TO_COLLECT:
                    # Update connection timestamp
                    self.last_data_time = time.time()

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
                    data_points_received += 1

            except (BlockingIOError, json.JSONDecodeError, KeyError):
                pass

        print(f"\n  {Colors.GREEN}✓ Recording complete!{Colors.RESET}")

        # Check if we got data
        if len(self.current_recording) == 0:
            print(f"\n  {Colors.RED}⚠️  WARNING: No data recorded! Check your watch connection.{Colors.RESET}")
            return False

        print(f"  {Colors.GREEN}📊 Captured {len(self.current_recording)} data points{Colors.RESET}")

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

    def _get_connection_status(self):
        """Get current connection status with color coding."""
        if time.time() - self.last_data_time > CONNECTION_TIMEOUT_SEC:
            self.connection_active = False
            return f"{Colors.RED}❌ CONNECTION LOST{Colors.RESET}"
        else:
            self.connection_active = True
            return f"{Colors.GREEN}✓ CONNECTED{Colors.RESET}"

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

        print(f"  {Colors.GREEN}💾 Saved: {filename}{Colors.RESET}")

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
    title = f"{Colors.BOLD}{Colors.GREEN}SILKSONG CONTROLLER - PHASE II DATA COLLECTION{Colors.RESET}"
    subtitle = f"{Colors.BLUE}IMU Gesture Training Data Acquisition{Colors.RESET}"
    # Note: Can't center ANSI colored text easily, so print without centering
    print(f"║  {title}  ║")
    print(f"║  {subtitle}  ║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")

    # Calculate SIMPLIFIED dataset statistics
    target_gestures = ["punch", "jump", "turn", "walk"]
    noise_gesture = ["noise"]

    target_samples = len(target_gestures) * SAMPLES_PER_GESTURE
    noise_total = NOISE_SAMPLES
    total_samples = target_samples + noise_total
    total_gestures = len(target_gestures) + len(noise_gesture)

    welcome_message = f"""
{Colors.BOLD}Welcome to the SIMPLIFIED data collection procedure!{Colors.RESET}

This tool will help you collect high-quality IMU sensor data for training
a machine learning gesture recognition model.

{Colors.BOLD}{Colors.RED}═══ THE "STRAY CATCHER" PHILOSOPHY ═══{Colors.RESET}
This is a {Colors.BOLD}{Colors.YELLOW}5-CLASS{Colors.RESET} classification problem:
  {Colors.GREEN}1. PUNCH{Colors.RESET} - Forward striking motion
  {Colors.GREEN}2. JUMP{Colors.RESET} - Upward body hop
  {Colors.GREEN}3. TURN{Colors.RESET} - 180° body rotation
  {Colors.GREEN}4. WALK{Colors.RESET} - In-place walking motion
  {Colors.RED}5. NOISE{Colors.RESET} - {Colors.BOLD}EVERYTHING ELSE{Colors.RESET} (The Stray Catcher)

{Colors.RED}{Colors.BOLD}THE KEY INSIGHT:{Colors.RESET}
We DON'T need to teach the model the difference between "typing" and "drinking."
We ONLY need it to know: {Colors.BOLD}"Is this one of the 4 sacred gestures? If not, IGNORE IT."{Colors.RESET}

The NOISE class is a {Colors.YELLOW}single, diverse category{Colors.RESET} containing samples of:
  • Resting (complete stillness)
  • Daily tasks (typing, drinking, phone use)
  • Involuntary motions (coughs, sneezes, shrugs)
  • Checking the watch (CRITICAL confounding pattern)
  • False starts (weak punches, partial jumps)
  • Fidgeting and scratching

{Colors.BOLD}{Colors.BLUE}═══ WHAT TO EXPECT ═══{Colors.RESET}
  • You will collect {Colors.YELLOW}{total_gestures} gesture classes{Colors.RESET}
  • {Colors.GREEN}4 target gestures{Colors.RESET} × {SAMPLES_PER_GESTURE} samples each
  • {Colors.RED}1 NOISE class{Colors.RESET} × {NOISE_SAMPLES} samples (oversampled for robustness)
  • {Colors.GREEN}Clear, detailed instructions{Colors.RESET} will be provided before each recording
  • The entire process takes approximately {Colors.YELLOW}60-75 minutes{Colors.RESET}

{Colors.BOLD}{Colors.RED}═══ REQUIREMENTS ═══{Colors.RESET}
  • Your Wear OS watch must be {Colors.GREEN}connected and streaming{Colors.RESET} sensor data
  • Find a {Colors.BLUE}clear space{Colors.RESET} where you can move freely (at least 2m × 2m)
  • Have {Colors.BLUE}water nearby{Colors.RESET} - you'll be moving!
  • Ensure your watch is {Colors.GREEN}securely fastened{Colors.RESET} to your wrist
  • Wear {Colors.YELLOW}comfortable clothing{Colors.RESET} that allows free movement

{Colors.BOLD}{Colors.GREEN}═══ TIPS FOR QUALITY DATA ═══{Colors.RESET}
  • Execute target gestures {Colors.YELLOW}deliberately and consistently{Colors.RESET}
  • {Colors.BLUE}Return to the specified stance{Colors.RESET} between gestures
  • {Colors.YELLOW}Take breaks{Colors.RESET} if you feel fatigued - quality over speed!
  • For NOISE samples, {Colors.RED}be natural and varied{Colors.RESET} - variety is key!
  • Read each instruction {Colors.RED}carefully{Colors.RESET} before executing

{Colors.BOLD}{Colors.BLUE}═══ SIMPLIFIED DATASET BREAKDOWN ═══{Colors.RESET}
  {Colors.GREEN}TARGET Gestures:{Colors.RESET} {len(target_gestures)} types × {SAMPLES_PER_GESTURE} = {target_samples} samples
  {Colors.RED}NOISE (Stray Catcher):{Colors.RESET} 1 diverse class × {NOISE_SAMPLES} = {noise_total} samples
  ────────────────────────────────────────────────────────────────
  {Colors.YELLOW}{Colors.BOLD}► Total samples to collect: {total_samples}{Colors.RESET}
  {Colors.GREEN}{Colors.BOLD}► This is MANAGEABLE in a single focused session!{Colors.RESET}
    """

    print(welcome_message)
    input(f"\n{Colors.BOLD}{Colors.GREEN}Press [Enter] to begin setup...{Colors.RESET}")

    # Initialize collector
    collector = DataCollector()

    try:
        collector.setup()

        # Connection check with real-time monitoring
        print("\n" + "─" * 70)
        print(f"{Colors.BOLD}{Colors.YELLOW}CONNECTION CHECK{Colors.RESET}")
        print("─" * 70)
        print(f"{Colors.BLUE}Checking if watch is sending data...{Colors.RESET}")
        print(f"{Colors.YELLOW}Please make sure streaming is ON in your watch app.{Colors.RESET}")

        # Wait for first packet with visual feedback
        timeout = 15
        start_wait = time.time()
        received_data = False
        last_update = 0

        while time.time() - start_wait < timeout:
            elapsed = time.time() - start_wait
            remaining = timeout - elapsed

            # Update status every 0.5 seconds
            if time.time() - last_update > 0.5:
                print(f"\r{Colors.YELLOW}⏳ Waiting for data... {remaining:.1f}s remaining{Colors.RESET}", end="", flush=True)
                last_update = time.time()

            try:
                data, _ = collector.sock.recvfrom(4096)
                parsed = json.loads(data.decode())
                if parsed.get("sensor") in SENSORS_TO_COLLECT:
                    received_data = True
                    collector.last_data_time = time.time()  # Initialize connection tracking
                    break
            except (BlockingIOError, json.JSONDecodeError, KeyError):
                time.sleep(0.1)

        print()  # New line after status updates

        if not received_data:
            print(f"\n{Colors.RED}❌ ERROR: No sensor data received from watch!{Colors.RESET}")
            print(f"{Colors.YELLOW}Please ensure:{Colors.RESET}")
            print(f"  {Colors.BLUE}1. Watch app is open{Colors.RESET}")
            print(f"  {Colors.BLUE}2. Streaming toggle is ON{Colors.RESET}")
            print(f"  {Colors.BLUE}3. Both devices are on the same network{Colors.RESET}")
            return

        print(f"{Colors.GREEN}✓ Connection verified! Receiving sensor data.{Colors.RESET}")

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
                print(f"  {Colors.BOLD}{Colors.GREEN}GESTURE: {gesture['name'].upper()}{Colors.RESET}")
                print("═" * 70)

                # Collect multiple samples
                for sample_num in range(1, SAMPLES_PER_GESTURE + 1):
                    success = collector.record_gesture(gesture_key, sample_num)

                    if not success:
                        retry = input(f"\n  {Colors.YELLOW}Try recording this sample again? (y/n): {Colors.RESET}")
                        if retry.lower() == 'y':
                            success = collector.record_gesture(gesture_key, sample_num)

                    if success:
                        # Brief pause between samples
                        if sample_num < SAMPLES_PER_GESTURE:
                            print(f"\n  {Colors.BLUE}Take a moment to reset to stance...{Colors.RESET}")
                            time.sleep(2)

                gestures_completed.append(gesture_key)

                # Break between gestures
                print(f"\n  {Colors.GREEN}✓ Gesture complete! Take a short break if needed.{Colors.RESET}")
                cont = input(f"  {Colors.BOLD}Press [Enter] to continue to next gesture (or 'q' to quit)...{Colors.RESET}")
                if cont.lower() == 'q':
                    break

            # Break between stances
            if stance_key != "travel":  # Don't break after the last stance
                print("\n" + "═" * 70)
                print(f"  {Colors.BOLD}{Colors.GREEN}STANCE COMPLETE!{Colors.RESET}")
                print("═" * 70)
                print(f"  {Colors.YELLOW}Take a longer break. Stretch, have some water.{Colors.RESET}")
                input(f"  {Colors.BOLD}Press [Enter] when ready for the next stance...{Colors.RESET}")

        # Save session metadata
        collector.save_session_metadata(gestures_completed)

        # Final summary
        print("\n" + "╔" + "═" * 68 + "╗")
        print("║" + " " * 68 + "║")
        print("║" + f"  {Colors.BOLD}{Colors.GREEN}DATA COLLECTION COMPLETE!{Colors.RESET}".center(78) + "║")
        print("║" + " " * 68 + "║")
        print("╚" + "═" * 68 + "╝")

        print(f"\n{Colors.BOLD}📊 Session Summary:{Colors.RESET}")
        print(f"   {Colors.BLUE}• Session ID: {collector.session_id}{Colors.RESET}")
        print(f"   {Colors.BLUE}• Gestures collected: {len(gestures_completed)}{Colors.RESET}")
        print(f"   {Colors.BLUE}• Samples per gesture: {SAMPLES_PER_GESTURE}{Colors.RESET}")
        print(f"   {Colors.BLUE}• Output directory: {collector.output_dir}{Colors.RESET}")

        print(f"\n{Colors.GREEN}✨ Your training data is ready for the next phase: Model Training!{Colors.RESET}")
        print(f"   {Colors.YELLOW}All files have been saved to: {collector.output_dir}{Colors.RESET}")

    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Data collection interrupted by user.{Colors.RESET}")
        print(f"{Colors.BLUE}Partial data has been saved.{Colors.RESET}")

    except Exception as e:
        print(f"\n\n{Colors.RED}❌ ERROR: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()

    finally:
        collector.cleanup()
        print(f"\n{Colors.GREEN}✓ Cleanup complete. Thank you!{Colors.RESET}")


if __name__ == "__main__":
    main()
