# **Project Protocol: High-Fidelity sEMG Gesture Classification (v2.0)**

**Document Purpose:** This document serves as a comprehensive Standard Operating Procedure (SOP) for the design, execution, and analysis of a machine learning pipeline for classifying forearm muscle gestures using a single-channel surface electromyography (sEMG) sensor. It is intended to be followed meticulously to ensure scientific rigor and repeatability, while also serving as an educational guide for readers unfamiliar with the technologies involved.

---

## **Version 2.0 Upgrades**

This is the **enhanced version** of the protocol, incorporating improvements for real-world deployment:

### **Key Changes from v1.0:**

1. **3-Class Classification System** (was: 2-class)
   - **Classes:** Rest (0), Signal (1), **Noise (2)** ← NEW
   - **Purpose:** Dramatically improves robustness by teaching the model to reject false positives
   - **Examples of Noise:** Coughs, bicep flexes, head turns, grip adjustments, false starts

2. **Increased Sample Size** (was: 25 per class → now: 40 per class)
   - **Total Samples:** 120 (was 50)
   - **Data Collection Time:** ~60 minutes (was ~30 minutes)
   - **Benefit:** Better generalization, more robust hyperparameter tuning, captures natural variability

3. **Enhanced Data Collection Script**
   - **Color-coded prompts:** 🔵 Blue=Rest, 🔴 Red=Signal, 🟡 Yellow=Noise
   - **Pause mechanism:** Press 'p' + ENTER to pause between trials
   - **Pause logging:** All breaks are logged with timestamps
   - **Specific noise gestures:** Script provides detailed instructions for each noise trial

4. **Deployment Considerations**
   - **Debouncing logic:** Sliding window voting system (15/20 predictions needed)
   - **Confidence thresholds:** Only accept high-confidence predictions (>0.9)
   - **State machine:** Stable on/off transitions, no flickering
   - **Real-world testing:** Protocol for collecting data while cycling

### **Why These Changes Matter:**

The original 2-class system was academically sound but would struggle in real-world use. Any muscle movement (cough, bicep flex, etc.) would be forced into either "Rest" or "Signal" category, leading to false positives. The v2.0 3-class system explicitly learns to **reject** these confounding movements, making the bike turn signal reliable and safe for road use.

---

### **Phase I: Hardware Environment & System Integration**

**Objective:** To assemble and verify a complete, functional hardware system capable of acquiring raw biopotential data from a human subject and transmitting it to a computer for analysis.

**Lead Personnel:** Carl Vincent (Primary Investigator)

**Timeline:** This phase should be completed prior to any data acquisition attempts. Estimated time: 1-2 hours.

---

#### **1.1: Component Selection & Rationale**

This section details each electronic component selected for the system, explaining its function, the reason for its selection, and how it contributes to the overall project goal.

**1.1.1: The Microcontroller Unit (MCU) - The "Brain"**

* **What:** NodeMCU-32S Development Board, based on the Espressif ESP32 System-on-a-Chip.
* **Why:** The MCU is the central processing unit of our embedded system. It executes the firmware (our C++ code), reads data from the sensor, and communicates with the host computer. The ESP32 was chosen over simpler MCUs (like an Arduino Uno) for several key reasons:
    1. **High-Resolution ADC:** It features a 12-bit Analog-to-Digital Converter (ADC). An ADC is the component that converts a continuous analog voltage (from our sensor) into a discrete digital number. A 12-bit ADC can represent a voltage in 2¹² = 4096 steps (from 0 to 4095), offering 4 times the measurement precision of the 10-bit ADC (1024 steps) found in more basic boards. This higher precision is crucial for capturing the subtle details of a biopotential signal.
    2. **Processing Power:** Its 240MHz dual-core processor provides ample computational power to run not only data acquisition code but also, for future iterations, on-device machine learning models (inference).
    3. **Connectivity:** Integrated Wi-Fi and Bluetooth capabilities allow for Over-the-Air (OTA) firmware updates, which is invaluable for a wearable device and eliminates the need for a physical connection during iterative development.
* **How it Works:** The ESP32 will be programmed to continuously read the voltage level on one of its ADC input pins (`GPIO 34`) and transmit the resulting digital value over a serial communication link (USB) to the host computer.

**1.1.2: The Biopotential Sensor - The "Senses"**

* **What:** AD8232 Single-Lead Heart Rate Monitor Front End module.
* **Why:** Surface electromyography signals are extremely small (in the microvolt to millivolt range) and are buried in electrical noise from the body and the environment. It is impossible to connect an electrode directly to the MCU. The AD8232 is an Application-Specific Integrated Circuit (ASIC) designed for this exact purpose. It is a complete "analog front-end" that performs three critical signal conditioning tasks in one package:
    1. **Amplification:** It contains a high-gain, low-noise instrumentation amplifier that increases the amplitude of the tiny muscle signal by a factor of hundreds or thousands, making it large enough for the ESP32's ADC to measure accurately.
    2. **Filtering:** It includes active electronic filters designed to remove unwanted signals. It has a high-pass filter to remove low-frequency noise (like the drift caused by electrode movement) and a low-pass filter to remove high-frequency noise (like electrical hum from power lines). This process isolates the desired EMG signal, which typically resides in the 20-500Hz frequency band.
    3. **Buffering:** It provides a stable, low-impedance output signal that can be reliably read by the MCU's ADC.
* **How it Works:** The module takes the raw, noisy, microvolt-level signals from the three electrode inputs (`LO+`, `LO-`, `Reference`) and outputs a single, clean, amplified, and filtered analog voltage on its `OUTPUT` pin.

**1.1.3: The Prototyping Platform**

* **What:** Solderless Breadboard and Male-to-Male Jumper Wires.
* **Why:** These are standard tools for prototyping electronic circuits without permanent connections. The breadboard contains a grid of interconnected sockets that allow components to be plugged in and connected quickly. Jumper wires are used to create the electrical connections between the components on the breadboard.
* **How they Work:** The ESP32 and AD8232 will be mounted on the breadboard. Jumper wires will then be used to route power (`3V3`), ground (`GND`), and the signal (`OUTPUT`) between the two modules.

---

#### **1.2: System Assembly & Integration Procedure**

This section provides a step-by-step guide for the physical assembly of the hardware.

**1.2.1: Header Pin Soldering**

* **Prerequisite:** A soldering iron, solder, and safety glasses are required.
* **Procedure:**
    1. Gently snap a 5-pin segment from the provided male header strip.
    2. To ensure perfect alignment, insert the long ends of the 5-pin segment into a breadboard.
    3. Place the AD8232 module onto the short, exposed ends of the pins, using the breadboard as a stable jig.
    4. Carefully apply solder to each of the five joints, ensuring a clean, conductive connection between the pin and the circular pad on the circuit board. The pins to be soldered are `GND`, `3.3V`, `OUTPUT`, `LO-`, and `LO+`.
    5. Allow the module to cool completely before handling.

**1.2.2: Breadboard Mounting & Wiring**

* **Objective:** To create a stable, correctly wired hardware assembly.
* **Procedure:**
    1. Mount the NodeMCU-32S board onto the center of the breadboard, ensuring the pins on each side are on opposite sides of the central divide.
    2. Mount the now-soldered AD8232 module onto the breadboard adjacent to the ESP32.
    3. Using three jumper wires, make the following **critical connections**, referencing the official NodeMCU-32S pinout diagram to verify pin locations:
        * **Power Connection:** Connect the pin labeled **`3.3V`** on the AD8232 module to the pin labeled **`3V3`** on the ESP32 board. *Rationale: This provides the clean, regulated 3.3 volts required by the sensor, supplied directly from the ESP32's onboard voltage regulator.*
        * **Ground Connection:** Connect the pin labeled **`GND`** on the AD8232 module to a pin labeled **`GND`** on the ESP32 board. *Rationale: This establishes a common ground reference, which is essential for any electronic circuit to function correctly.*
        * **Signal Connection:** Connect the pin labeled **`OUTPUT`** on the AD8232 module to the pin labeled **`GPIO 34`** on the ESP32 board. *Rationale: This routes the final, conditioned analog signal from the sensor to the specific ADC input pin that our firmware will be programmed to read.*

---

#### **1.3: System Verification**

**Objective:** To confirm that the assembled hardware is functioning and communicating with the host computer.

**1.3.1: Connectivity Check**

* **Procedure:**
    1. Connect the assembled hardware to the host MacBook computer using a Micro-USB data cable.
    2. A red power indicator LED on the ESP32 board should illuminate, confirming it is receiving power.

**1.3.2: Initial Firmware Test ("Blink Test")**

* **Procedure:**
    1. Using a properly configured software environment (to be detailed in the next phase), deploy a simple "Blink" sketch to the ESP32.
    2. Upon successful upload, the onboard blue LED on the ESP32 should begin to blink.
* **Pass/Fail Criteria:** A blinking blue LED confirms the following: the USB driver is correct, the communication port is functional, the PlatformIO toolchain is correctly configured, and the ESP32 board itself is fully operational. The hardware integration phase is not complete until this test passes.
Excellent. With the hardware assembly and verification protocol firmly established, we now proceed to Phase I, Part 2: preparing the sophisticated software environment required to program, communicate with, and acquire data from our hardware.

---

### **Project Protocol: High-Fidelity sEMG Gesture Classification**

### **Phase I, Part 2: Software Environment & Toolchain Configuration**

**Objective:** To configure the host computer (a macOS MacBook Pro with an M2 processor) with a professional-grade, integrated development environment (IDE) capable of compiling C++ firmware, uploading it to the ESP32 microcontroller, and monitoring real-time serial data communication.

**Lead Personnel:** Carl Vincent (Primary Investigator)

**Rationale for Tool Selection:** While the standard Arduino IDE is functional for simple projects, it lacks the advanced features required for a rigorous, publication-quality project. We will use **Visual Studio Code (VS Code) with the PlatformIO extension**. This choice is deliberate and provides several key advantages:

* **Integrated Environment:** It allows for code editing, compiling, uploading, and data monitoring all within a single, powerful application.
* **Intelligent Code Completion:** Provides advanced code completion and error-checking, drastically reducing development time and bugs.
* **Dependency Management:** PlatformIO automatically manages project-specific libraries and board definitions, ensuring a clean, reproducible build environment.
* **Professional Standard:** This toolchain is widely used in the professional embedded systems industry, making the skills acquired directly transferable.

---

#### **1.4: Host Computer Software Installation & Configuration**

This section details the step-by-step installation of all required software on the host MacBook.

**1.4.1: Installation of Visual Studio Code (VS Code)**

* **What:** VS Code is a free, highly extensible source-code editor developed by Microsoft. It will serve as the foundation of our IDE.
* **Procedure:**
    1. Navigate to the official download page: [https://code.visualstudio.com/](https://code.visualstudio.com/).
    2. Download the "Apple Silicon" version of the installer to match the M2 processor architecture.
    3. Run the installer and move the VS Code application to the main `Applications` folder.

**1.4.2: Installation of the PlatformIO IDE Extension**

* **What:** PlatformIO is an open-source ecosystem for embedded development. Its IDE extension for VS Code provides the core functionality for compiling and uploading firmware.
* **Procedure:**
    1. Launch the VS Code application.
    2. Navigate to the **Extensions** view by clicking the square icon on the left-hand Activity Bar or by pressing `Shift+Cmd+X`.
    3. In the search bar, type `PlatformIO IDE`.
    4. Select the extension published by PlatformIO and click the **"Install"** button.
    5. Allow the installation to complete. This process may take several minutes as it also installs necessary dependencies, including the Python interpreter and compilers required by PlatformIO Core.

**1.4.3: Installation of the USB-to-Serial Driver**

* **What:** The NodeMCU-32S board uses a CH340 chip to handle USB communication. macOS does not have a native driver for this chip. A specific driver must be installed to allow the operating system to recognize the ESP32 and assign it a serial port.
* **Procedure:**
    1. Navigate to the verified driver source, for example, the one provided by SparkFun: [https://learn.sparkfun.com/tutorials/how-to-install-ch340-drivers/all](https://learn.sparkfun.com/tutorials/how-to-install-ch340-drivers/all).
    2. Download the latest macOS version of the driver.
    3. Run the `.pkg` installer, following the on-screen prompts. You may need to grant security permissions in macOS System Settings.
    4. **Crucially, perform a full restart of the MacBook.** The kernel extension will not be loaded until after a reboot.

---

#### **1.5: Project Creation and Configuration**

This section details the creation of the specific project environment within PlatformIO.

**1.5.1: Project Initialization**

* **Procedure:**
    1. After restarting, open VS Code. Navigate to the PlatformIO Home screen by clicking the alien/ant head icon on the Activity Bar.
    2. Click **"New Project"** to launch the Project Wizard.
    3. Configure the project with the following specific settings:
        * **Name:** `EMG-Gesture-Classifier` (or a similar descriptive name).
        * **Board:** `NodeMCU-32S`. This is a critical step, as it tells PlatformIO to use the correct pin mappings, memory layout, and toolchain for this specific hardware.
        * **Framework:** `Arduino`. This selection allows us to leverage the well-documented and easy-to-use Arduino Core for the ESP32, which simplifies tasks like reading analog pins and serial communication.
    4. Click **"Finish"**. PlatformIO will create a directory structure for the project.

**1.5.2: Configuration File (`platformio.ini`) Setup**

* **What:** The `platformio.ini` file is the central configuration file for the project. It tells PlatformIO how to build, upload, and monitor the firmware.
* **Procedure:**
    1. In the VS Code Explorer, locate and open the `platformio.ini` file at the root of your project directory.
    2. Add the following lines to the environment configuration to ensure a stable and predictable monitoring setup.

    ```ini
    [env:nodemcu-32s]
    platform = espressif32
    board = nodemcu-32s
    framework = arduino

    ; Set the communication speed for the Serial Monitor to 115200 bits per second.
    ; This must match the speed set in the firmware's Serial.begin() call.
    monitor_speed = 115200

    ; Explicitly define the port to use for monitoring. This prevents the monitor
    ; from guessing and connecting to the wrong port (e.g., Bluetooth).
    ; The port name must be updated to match the specific port assigned to the ESP32.
    monitor_port = /dev/cu.usbserial-XXXX
    ```

    *Note: The `XXXX` in `monitor_port` is a placeholder. The correct value will be determined in the verification step.*

---

#### **1.6: Software Environment Verification**

**Objective:** To confirm that the entire software toolchain is correctly configured and can successfully compile code, upload it to the target hardware, and receive serial data.

**1.6.1: Firmware Deployment Test ("Hello World")**

* **Procedure:**
    1. Navigate to the `src/main.cpp` file within the project directory.
    2. Enter a simple test firmware designed to send a repeating message over the serial port.

    ```cpp
    #include <Arduino.h>

    void setup() {
      // Initialize serial communication at 115200 bits per second (baud).
      Serial.begin(115200);
    }

    void loop() {
      // Print a test message every second.
      Serial.println("Hello World: Toolchain is operational.");
      delay(1000);
    }
    ```

    3. Connect the assembled hardware to the MacBook via USB.
    4. Use the **"Upload"** command in PlatformIO (the right-arrow icon → in the status bar).
    5. The first time this runs, PlatformIO will download the necessary toolchain and framework files, which may take several minutes. Subsequent uploads will be much faster.
    6. Observe the terminal output. A **"[SUCCESS]"** message indicates the firmware was compiled and uploaded correctly. Note the auto-detected upload port name (e.g., `/dev/cu.usbserial-110`) and update the `monitor_port` value in `platformio.ini` accordingly.

**1.6.2: Serial Monitor Verification**

* **Procedure:**
    1. After a successful upload, launch the PlatformIO **Serial Monitor** (the power-plug icon ⏚ in the status bar).
* **Pass/Fail Criteria:** The Serial Monitor window must display the message "Hello World: Toolchain is operational." printing once per second. This successful two-way communication (Upload to board, Monitor from board) confirms that the entire software environment is fully configured and operational. The system is now ready for the data acquisition phase.

Excellent. We have now fully prepared and verified both the hardware and software environments. The system is a confirmed, working unit.

We now proceed to Phase II, the most critical part of the experimental process: the structured acquisition of high-fidelity biopotential data. This phase is designed to be executed with the precision of a laboratory experiment to ensure the resulting dataset is clean, well-labeled, and scientifically sound.

---

### **Project Protocol: High-Fidelity sEMG Gesture Classification**

### **Phase II: Data Acquisition Protocol**

**Objective:** To systematically record raw sEMG data corresponding to specific, well-defined muscle states ("Rest" and "Signal") from a human subject. This protocol is designed to maximize signal quality, ensure repeatability, and create a dataset optimized for a machine learning classification task.

**Lead Personnel:** Carl Vincent (Primary Investigator and Subject)

**Timeline:** This entire phase should be completed in a single, uninterrupted session to ensure consistency. Estimated time: ~1 hour.

---

#### **2.1: Experimental Environment Setup**

**Objective:** To create a controlled environment that minimizes external noise and ensures subject comfort and consistency.

**2.1.1: Subject Preparation**

* **Procedure:**
    1. The subject (Carl Vincent) will be seated comfortably in a chair with the right arm resting on a flat, non-conductive surface (e.g., a wooden table).
    2. The right forearm should be in a neutral position, parallel to the body.

**2.1.2: Minimizing Electrical Noise**

* **Rationale:** Surface EMG signals are highly susceptible to electromagnetic interference (EMI), primarily 50/60Hz noise from mains power lines. To acquire the cleanest possible signal, all potential sources of EMI must be minimized.
* **Procedure:**
    1. The host MacBook Pro will be **disconnected from its AC power adapter** and will run on battery power for the duration of the data acquisition.
    2. The ESP32 hardware system will be disconnected from the MacBook's USB port and will be powered exclusively by a **portable USB power bank**. This creates an "air gap," electrically isolating the sensitive analog circuit from the noisy power system of the computer and the building.

**2.1.3: Skin Preparation Protocol**

* **Rationale:** The quality of the skin-electrode interface is the single most critical factor in sEMG data acquisition. Skin oils, hair, and dead skin cells create high impedance, which weakens the signal and introduces noise.
* **Procedure:**
    1. The target areas on the subject's right arm will be identified.
    2. These areas will be cleansed by washing with soap and water.
    3. Following washing, the areas will be wiped with an isopropyl alcohol pad to remove residual oils.
    4. The skin will be allowed to air dry completely before electrode application. This protocol is an adaptation of standard clinical practice for biopotential measurements.

---

#### **2.2: Electrode Placement Protocol**

**Objective:** To place the three sEMG electrodes in a standardized, anatomically-referenced configuration to optimally detect the signal from the **Extensor Digitorum** muscle group while minimizing crosstalk from other muscles.

**2.2.1: Anatomical Landmark Identification**

* **Procedure:**
    1. The subject will place their right forearm on the table, palm down.
    2. The subject will then perform a **wrist and finger extension** (lifting the hand and fingers towards the ceiling).
    3. This action will cause the **belly of the Extensor Digitorum muscle** to become prominent on the top (posterior) aspect of the forearm. This location is the primary target for electrode placement.

**2.2.2: Electrode Application**

* **Procedure:**
    1. **Reference Electrode (GREEN connector):** This electrode will be placed on an electrically neutral, bony landmark. The recommended location is the **lateral epicondyle of the humerus** (the distinct bony point on the outer side of the elbow).
    2. **Primary Signal Electrode (YELLOW connector / LO+):** This electrode will be placed directly over the center of the identified **Extensor Digitorum muscle belly**.
    3. **Secondary Signal Electrode (RED connector / LO-):** This electrode will be placed **2-3 cm distally** (towards the wrist) from the yellow electrode, ensuring its orientation is parallel to the presumed direction of the underlying muscle fibers (i.e., along the line from the elbow to the wrist). This bipolar configuration is crucial for differential amplification, a technique that rejects noise common to both electrodes.

---

#### **2.3: Data Acquisition Firmware & Software**

**Objective:** To use a coordinated software approach to guide the experiment and automate the recording of clean, labeled data.

**2.3.1: ESP32 Firmware**

* **Rationale:** The firmware for the data acquisition phase must be simple and efficient. Its sole purpose is to read the ADC as fast as possible and stream the raw integer values. All timing, labeling, and file management will be handled by the host computer.
* **Procedure:**
    1. The ESP32 will be programmed (via USB, prior to the experiment) with the following firmware.

    ```cpp
    #include <Arduino.h>
    const int sensorPin = 34; // ADC1_CH6

    void setup() {
      // Set a high baud rate to support rapid data transfer without buffering issues.
      Serial.begin(115200);
    }

    void loop() {
      // Continuously read the analog pin and print the raw 12-bit value.
      Serial.println(analogRead(sensorPin));
    }
    ```

**2.3.2: Host Computer "Lab Assistant" Script**

* **Rationale:** A Python script will be used to orchestrate the experiment. This automates the process, provides interactive instructions and countdowns to the subject, and ensures that data is saved to clearly labeled files, eliminating the risk of manual copy-paste errors.
* **Procedure:**
    1. The `data_collector.py` script (as detailed previously) will be executed from a terminal on the host MacBook. The script must be configured with the correct `SERIAL_PORT` for the ESP32.

---

#### **2.4: Guided Data Collection Procedure**

**Objective:** To execute the interactive data collection protocol.

**2.4.1: Maximum Voluntary Contraction (MVC) Test**

* **Rationale:** To establish a subject-specific baseline for signal normalization. All subsequent data will be analyzed relative to this personal maximum.
* **Procedure:** The Python script will first prompt the subject to perform a 5-second maximum-effort wrist and finger extension. The script will record the peak ADC value observed during this contraction and save it to `mvc_value.txt`.

**2.4.2: Randomized Snippet Recording**

* **Rationale:** To collect a balanced dataset of "Signal" and "Rest" states in a randomized order to prevent subject anticipation or rhythm bias.
* **Procedure:** The script will guide the subject through a series of 50 randomized trials (25 for each class).
  * **"Signal" Gesture:** On prompt, the subject will perform a controlled **wrist and finger extension**. The gesture will follow a precise 4.5-second pattern: a 1-second smooth ramp-up, a 1.5-second isometric hold at peak contraction, and a 2-second smooth ramp-down to the resting state. The script will record for this duration and save the data to the `label_1_signal` folder.
  * **"Rest" Gesture:** On prompt, the subject will maintain a relaxed, neutral grip on a cylindrical object (simulating a handlebar). The script will record for 5.5 seconds and save the data to the `label_0_rest` folder.

**2.4.3: Session Conclusion**

* **Outcome:** Upon completion of the script, the hardware can be powered down. The data acquisition phase is complete. The outcome is two folders (`label_0_rest`, `label_1_signal`) containing 50 total `.txt` files of raw, time-series data, and one `mvc_value.txt` file containing the normalization constant. This dataset is the verified input for Phase III.

Excellent. Having meticulously acquired a high-fidelity dataset, we now move to the final and most intellectually demanding phase: transforming that raw data into knowledge.

This phase details the entire computational pipeline, from data pre-processing and feature engineering to model training and evaluation. It also explicitly incorporates the structure for your final report, including the "Future Work" section where we will address Professor Watson's advanced CNN concept.

---

### **Project Protocol: High--Fidelity sEMG Gesture Classification**

### **Phase III: Data Analysis & Machine Learning Pipeline**

**Objective:** To design and execute a complete machine learning pipeline in a Python environment to train, validate, and test a classifier capable of distinguishing between "Rest" and "Signal" gestures based on the acquired sEMG data.

**Lead Personnel:** Carl Vincent (Primary Investigator)

**Primary Tool:** Jupyter Notebook (for interactive development, analysis, and visualization).

---

#### **3.1: Fundamental Machine Learning Concepts & Application**

**Objective:** To establish the theoretical framework for the classification task. This section is foundational and will form a key part of the final report's introduction and methodology.

**3.1.1: Supervised Learning & Classification**

* **Explanation:** This project employs a **supervised learning** approach. Supervised learning is a subfield of machine learning where the goal is to learn a mapping function that can map an input variable (X) to an output variable (y). We "supervise" the algorithm by providing it with a large set of labeled examples (our training data), where we already know the correct output for each input. In our case, the "input" is the processed EMG signal, and the "output" is the gesture label ('Rest' or 'Signal'). The specific task is **binary classification**, as we are predicting a discrete class label from one of two possible categories.

**3.1.2: The "No Free Lunch" Theorem & Model Selection**

* **Explanation:** The "No Free Lunch" theorem for machine learning states that no single model works best for every problem. The choice of model depends on the nature of the data, the complexity of the problem, and the goals of the project (e.g., accuracy vs. interpretability). For this project, a **Support Vector Machine (SVM)** is selected as the primary model.
* **Rationale for SVM:**
    1. **Effectiveness on High-Dimensional Data:** SVMs are highly effective in high-dimensional spaces, which is relevant when working with a rich set of engineered features.
    2. **Robustness:** They are generally robust to overfitting, especially with smaller, clean datasets.
    3. **Explainability:** The mathematical principles of SVMs (hyperplanes, margins, support vectors) are well-established and can be clearly articulated in a scientific report, fulfilling a key requirement of the assignment.

---

#### **3.2: Data Consolidation and Pre-processing**

**Objective:** To transform the raw, multi-file dataset into a single, clean, and normalized data structure suitable for feature engineering.

**3.2.1: Data Loading & Labeling**

* **Procedure:**
    1. A Python script within the Jupyter Notebook will be created.
    2. The script will iterate through the `label_0_rest` and `label_1_signal` directories.
    3. For each `.txt` snippet file, it will load the raw time-series data into memory.
    4. It will programmatically assign the correct label (`0` for files from the `rest` folder, `1` for files from the `signal` folder) to each snippet.
    5. All snippets will be consolidated into a single data structure, such as a Pandas DataFrame, with columns for the raw data, the snippet ID, and the assigned label.

**3.2.2: Signal Normalization**

* **Rationale:** The raw ADC values are arbitrary and can vary based on factors like skin impedance and electrode placement on a given day. **Normalization** is a critical pre-processing step that transforms the data onto a standardized scale. This makes the model more robust and its performance comparable across different sessions or subjects.

* **Why Normalization is Essential:**
    - **Skin impedance variability:** On a dry day, your skin has higher electrical resistance. On a humid day or after applying more electrode gel, resistance is lower. This changes the signal amplitude by 2-3x for the same muscle contraction.
    - **Electrode placement:** Moving an electrode even 1cm changes which muscle fibers it "sees," altering signal strength.
    - **Individual differences:** Your maximum muscle strength differs from another person's. Comparing raw values across people is meaningless.
    - **Without normalization:** A "rest" gesture on a good day might have higher raw values than a "signal" gesture on a bad day, breaking your classifier.
    - **With normalization:** Both gestures are expressed as % of your personal maximum, making them comparable regardless of external factors.

* **Maximum Voluntary Contraction (MVC) Explained:**
    - **What it is:** Your MVC is the strongest signal your muscle can produce when contracting as hard as possible.
    - **Why we measure it:** It establishes a personal baseline. If your MVC is 3847 ADC units, and a gesture produces 1923 units, that gesture is at 50% MVC.
    - **Standard practice:** Normalizing to %MVC is the gold standard in EMG research (recommended by SENIAM, the European guidelines for EMG research).
    - **Mathematical formula:**
      $$\text{Normalized Signal} = \frac{\text{Raw ADC Value}}{\text{MVC Value}} \times 100$$
    - **Example:** Raw value = 2500, MVC = 4000 → Normalized = (2500/4000) × 100 = 62.5% MVC

* **Procedure:**
    1. The script will load the `mvc_value.txt` file (e.g., contains "3847")
    2. Each raw `SignalValue` in the entire dataset will be divided by this MVC value
    3. The result is a normalized signal where each data point represents a percentage of the subject's Maximum Voluntary Contraction (%MVC)
    4. This transformation is applied to all 50 snippets uniformly, ensuring consistency

* **Practical Impact:**
    - **Before normalization:** "Rest" might range 1500-2500, "Signal" might range 2800-3800 (arbitrary units)
    - **After normalization:** "Rest" might range 40-65% MVC, "Signal" might range 73-98% MVC
    - The percentages are now meaningful, comparable, and robust to measurement conditions

---

#### **3.3: Feature Engineering**

**Objective:** To extract meaningful, quantitative features from the time-domain sEMG signal snippets. Raw time-series data is not suitable as a direct input for classical models like SVMs; we must first describe its characteristics.

**3.3.1: Feature Selection & Rationale**

* **Procedure:** A function will be written to process each normalized snippet (a vector of ~450 numbers) and output a single feature vector (a row of 5-6 numbers). This feature vector will serve as the input `X` for our SVM.
* **Why Feature Extraction?** Raw time-series EMG data (450 samples per snippet) cannot be directly fed into most classical machine learning models. We need to **compress** the signal into a smaller set of numbers that capture its essential characteristics. Think of it like describing a person: instead of listing every pixel in their photo, we describe key features (height, hair color, build). Similarly, we extract features that mathematically describe the EMG signal's shape, intensity, and complexity.

* **Initial Feature Set:** The following well-established time-domain features will be calculated for each snippet:

    1. **Mean Absolute Value (MAV):**
       - **Formula:** $\text{MAV} = \frac{1}{N}\sum_{i=1}^{N}|x_i|$
       - **What it measures:** The average magnitude of the signal, ignoring whether values are positive or negative.
       - **In your project:** MAV captures the overall muscle activation strength. A "Rest" gesture will have low MAV (relaxed muscle = small signal), while a "Signal" gesture will have high MAV (contracted muscle = large signal).
       - **Why it matters:** This is often the single most discriminative feature for EMG gesture classification.

    2. **Root Mean Square (RMS):**
       - **Formula:** $\text{RMS} = \sqrt{\frac{1}{N}\sum_{i=1}^{N}x_i^2}$
       - **What it measures:** Similar to MAV but squares values first, making it more sensitive to large spikes in the signal.
       - **In your project:** RMS emphasizes strong contractions. If you squeeze harder during "Signal" gestures, RMS will increase more dramatically than MAV.
       - **Why it matters:** RMS is related to signal power and is particularly good at detecting the intensity of muscle contraction.

    3. **Standard Deviation (SD):**
       - **Formula:** $\text{SD} = \sqrt{\frac{1}{N}\sum_{i=1}^{N}(x_i - \bar{x})^2}$
       - **What it measures:** How much the signal fluctuates around its mean value.
       - **In your project:** During "Rest," the signal is relatively steady (low SD). During "Signal," the muscle fibers fire asynchronously, creating more variability (higher SD).
       - **Why it matters:** SD captures the signal's "texture" or "busyness," which differs between gesture types.

    4. **Waveform Length (WL):**
       - **Formula:** $\text{WL} = \sum_{i=1}^{N-1}|x_{i+1} - x_i|$
       - **What it measures:** The cumulative distance traveled by the signal if you traced it point-to-point.
       - **In your project:** A smooth, gentle contraction has low WL (smooth curve). A trembling or forceful contraction has high WL (jagged curve with many small oscillations).
       - **Why it matters:** WL is sensitive to signal complexity and frequency content without requiring Fourier transforms.

    5. **Zero Crossings (ZC):**
       - **Formula:** $\text{ZC} = \sum_{i=1}^{N-1} \mathbb{1}[\text{sign}(x_i) \neq \text{sign}(x_{i+1})]$
       - **What it measures:** How many times the signal crosses its mean value (zero after mean-centering).
       - **In your project:** More crossings suggest higher frequency content. Different muscle contraction patterns produce different frequencies, which ZC can capture.
       - **Why it matters:** This is a simple time-domain proxy for frequency information, useful for distinguishing gesture dynamics.

* **Practical Example:** Imagine a "Rest" snippet might produce features like `[MAV=15, RMS=18, SD=8, WL=450, ZC=120]`, while a "Signal" snippet might produce `[MAV=65, RMS=82, SD=22, WL=1850, ZC=95]`. The SVM learns to separate these feature vectors into two classes.

* **Citation:** The selection of these features is based on their proven effectiveness in EMG-based gesture classification, as documented in numerous studies. A foundational review is provided by: Phinyomark, A., Phukpattaranont, P., & Limsakul, C. (2012). Feature extraction for EMG signal classification. *In Electronics, Computer, Telecommunications and Information Technology (ECTI-CON), 2012-9th International Conference on (pp. 1-4).* IEEE.

---

#### **3.4: Model Training and Evaluation**

**Objective:** To train the SVM model and rigorously evaluate its performance.

**3.4.1: Data Splitting Strategy**

* **Rationale:** To get an unbiased estimate of the model's performance on new, unseen data, we must use a proper validation strategy. A simple random split is inappropriate for time-series snippets.

* **Why is Random Split Inappropriate?**
    - **Temporal correlation risk:** Although our snippets are already separated trials, a completely random split could accidentally put very similar consecutive samples in both training and test sets if they were collected close together in time.
    - **Overfitting to sampling artifacts:** If there's any systematic drift in the data collection session (e.g., electrode impedance gradually changing, fatigue accumulating), a random split might not detect this because it tests on interspersed samples rather than held-out blocks.
    - **Real-world deployment mismatch:** In practice, your model will classify new gesture trials performed at a different time. Block validation better simulates this by testing on contiguous groups of trials.
    - **Statistical independence:** To properly estimate generalization error, test samples should be as independent as possible from training samples. Block-based splitting ensures entire "chunks" of the experiment are held out.

* **Procedure:** A **Blocked Cross-Validation** (or K-Fold Cross-Validation) approach will be used:
    1. The dataset of 50 snippets will be divided into `k` folds (e.g., 5 folds of 10 snippets each)
    2. The division respects the structure of the data collection—snippets are grouped into blocks
    3. In each iteration:
       - Training: The model is trained on `k-1` folds (e.g., 40 snippets)
       - Testing: The model is tested on the remaining held-out fold (e.g., 10 snippets)
    4. This process is repeated `k` times, rotating which fold is held out
    5. Every snippet is used in the test set exactly once across all iterations
    6. Final performance is the average of the `k` test scores

* **Why This is Better:**
    - **Maximizes data usage:** Every sample is used for both training and testing (just never at the same time)
    - **Reduces variance:** Averaging across multiple splits gives a more stable performance estimate than a single train-test split
    - **Detects overfitting:** If performance is high on training folds but low on test folds, you know the model isn't generalizing well
    - **Provides confidence intervals:** The variation across folds tells you how robust your model is

* **Example:** With 50 samples and 5-fold CV:
    - Fold 1: Train on samples 11-50, test on samples 1-10
    - Fold 2: Train on samples 1-10 + 21-50, test on samples 11-20
    - Fold 3: Train on samples 1-20 + 31-50, test on samples 21-30
    - Fold 4: Train on samples 1-30 + 41-50, test on samples 31-40
    - Fold 5: Train on samples 1-40, test on samples 41-50
    - **Final accuracy** = average of 5 test accuracies

**3.4.2: Model Training**

* **Procedure:** An SVM classifier from the Python `scikit-learn` library will be initialized, typically with a Radial Basis Function (RBF) kernel. The model's `fit()` method will be called on the feature vectors and labels from the training folds.

* **Understanding Support Vector Machines (SVM):**
    - **Core Concept:** An SVM finds the optimal **hyperplane** (a decision boundary) that separates two classes in feature space. Imagine plotting your 5 features in 5D space—some points are "Rest" gestures, others are "Signal" gestures. The SVM finds the flat surface (hyperplane) that best divides these two clouds of points.
    - **Maximum Margin:** The SVM doesn't just find any dividing line—it finds the one with the **maximum margin**, meaning the widest possible gap between the two classes. This makes the classifier more robust to new, unseen data.
    - **Support Vectors:** These are the data points closest to the decision boundary. They are the "critical" examples that define where the boundary is. Remove any other point, and the boundary stays the same; remove a support vector, and the boundary shifts.

* **What is the RBF (Radial Basis Function) Kernel?**
    - **The Problem:** Real-world data is often not linearly separable. You can't draw a straight line (or flat hyperplane) to perfectly separate the classes. Think of concentric circles—no straight line can separate the inner circle from the outer ring.
    - **The Solution:** The RBF kernel is a mathematical trick that **implicitly maps** your data into a much higher-dimensional space where it becomes linearly separable. It's like lifting 2D data into 3D so that a plane can now separate what a line couldn't.
    - **How it works:** The RBF kernel measures similarity using a Gaussian (bell curve) function:
      $$K(x, x') = \exp\left(-\gamma \|x - x'\|^2\right)$$
      where $\gamma$ (gamma) controls how far the influence of a single training example reaches. Low gamma = far reach (smooth boundary), high gamma = close reach (complex, wiggly boundary).
    - **In your project:** The RBF kernel allows the SVM to learn complex, non-linear decision boundaries. If "Rest" and "Signal" feature vectors form complicated patterns in 5D feature space (they likely do), the RBF kernel can adapt to capture those patterns.
    - **Practical implication:** You don't need to manually engineer the non-linear relationships—the RBF kernel handles it automatically. This is why SVM with RBF is powerful for EMG classification.

* **Training Process:**
    1. The SVM receives feature vectors (5 numbers per sample) and labels (0 or 1)
    2. It finds the hyperplane in the RBF-transformed space that maximally separates the two classes
    3. The trained model stores the support vectors and their weights
    4. To classify new data, the model compares the new feature vector to the support vectors using the RBF kernel

**3.4.3: Performance Evaluation**

* **Procedure:** The trained model will be used to predict labels for the held-out test folds. The predictions will be compared against the true labels to calculate the following metrics:
  * **Accuracy:** The overall percentage of correct predictions.
  * **Precision:** Of the gestures the model *predicted* as "Signal," how many were actually "Signal."
  * **Recall:** Of all the actual "Signal" gestures, how many did the model correctly identify.
  * **F1-Score:** The harmonic mean of precision and recall, providing a single score that balances both.
  * **Confusion Matrix:** A table that visualizes the model's performance, showing true positives, true negatives, false positives, and false negatives.

---

#### **3.5: Reporting and Future Work**

**Objective:** To document the project's findings and outline future directions.

**3.5.1: Final Report**

* **Procedure:** The final report will detail each of the phases described in this SOP. It will include visualizations of the raw signal, explanations of the engineered features, the final performance metrics of the SVM, and a discussion of the results.

**3.5.2: Future Work Section & Integration of Professor Watson's Advice**

* **Procedure:** This dedicated section will propose next steps for the project, demonstrating foresight and a deeper understanding of the field.
* **Content:**
    > As an alternative to the manual feature engineering approach employed in this study, a more advanced methodology could utilize a deep learning model for automatic feature extraction. Following the advice provided by Professor Watson (Personal Communication, October 2025), a future iteration of this project would involve transforming each raw sEMG snippet into a 2D representation, such as a **spectrogram**, via a Short-Time Fourier Transform (STFT). This spectrogram, which visualizes the signal's frequency content over time, could then be used as the input to a pre-trained 2D Convolutional Neural Network (CNN). By fine-tuning the final layers of the CNN, the model could learn to automatically identify the most salient visual patterns in the spectrograms that correspond to the 'Signal' and 'Rest' classes. This approach could potentially capture more complex, non-linear features than the handcrafted statistical features, potentially leading to higher classification accuracy and robustness, forming a promising direction for the planned capstone project.
    Of course. We have now defined the entire experimental and analytical process. The final, critical phase is to transform your results and hard work into a high-quality academic submission that satisfies the requirements of your assignment and stands as a potential publication-level document.

_____

### **Project Protocol: High-Fidelity sEMG Gesture Classification**

### **Phase IV: Dissemination and Reporting**

**Objective:** To structure, document, and present the project's methodology, results, and conclusions in a clear, professional, and scientifically rigorous format suitable for academic evaluation and potential publication.

**Lead Personnel:** Carl Vincent (Primary Investigator)

**Timeline:** To be completed after the successful execution of Phases I, II, and III.

---

#### **4.1: The Final Report: Structure and Content**

**Objective:** To create a comprehensive written document that details every aspect of the project, following the structure of a formal scientific paper. The detailed protocols from Phases I-III will form the core of this document.

**Roundtable Discussion: Crafting a Publication-Quality Report**

**Moderator:** "Dr. Chen, Carl needs to turn his project into a final report. How does he structure the detailed SOP we've built into a compelling academic paper?"

**AI/ML Specialist (Dr. Chen):** "Excellent question. The rigorous SOP we've designed is, in fact, the skeleton of a perfect methodology section. The report should follow a standard scientific structure, which will allow him to present his work logically and professionally.

**Here is the recommended report structure:**

**1. Abstract:**

* **Content:** A concise, single-paragraph summary of the entire project. It must state the problem, the approach, the key result, and the conclusion. (e.g., "This project developed a real-time, single-channel sEMG gesture classifier... An SVM trained on five engineered features achieved 9X.X% accuracy... demonstrating the feasibility of the approach for hands-free human-computer interaction.")

**2. Introduction:**

* **Content:** This section sets the stage. It should answer:
  * **The Problem:** What is the real-world problem you're solving? (e.g., The need for a hands-free signaling system for cyclists to improve safety).
  * **The Proposed Solution:** What is your specific technical approach? (e.g., A wearable sEMG sensor on the forearm to detect a specific, non-interfering muscle gesture).
  * **The Goal:** What is the objective of this paper? (e.g., To document the design and evaluate the performance of a complete machine learning pipeline for this task).

**3. Methodology:**

* **Content:** This is the most detailed section and is where you will **directly adapt and elaborate on our SOP**. Each phase becomes a subsection.
  * **3.1 Hardware System:** Detail the components (NodeMCU-32S, AD8232), explaining the rationale for each choice as we discussed in Phase I. Include a photograph of your final assembled hardware.
  * **3.2 Software Environment:** Briefly describe your development environment (VS Code with PlatformIO) and the firmware's function (high-speed data streaming).
  * **3.3 Data Acquisition Protocol:** This is critical. Describe the entire Phase II protocol in detail: the subject prep, the anatomical basis for electrode placement (citing the SENIAM standard), the MVC test for normalization, and the randomized, snippet-based recording procedure.
  * **3.4 Feature Engineering:** Explain the time-domain features you calculated (MAV, RMS, etc.) and why they are relevant for describing EMG signals.
  * **3.5 Machine Learning Model:** State that you selected an SVM and explain *why* (robustness, explainability). Describe your Blocked Cross-Validation strategy for testing.

**4. Results:**

* **Content:** This section presents only the objective findings, without interpretation.
  * Show a plot of the raw, normalized EMG signal for a "Rest" snippet versus a "Signal" snippet.
  * Present a table with your final model performance metrics (Accuracy, Precision, Recall, F1-Score).
  * Include a visualization of the final Confusion Matrix.

**5. Discussion:**

* **Content:** This is where you interpret your results.
  * What do the results mean? (e.g., "The high accuracy of 9X.X% demonstrates that an SVM trained on these features can reliably distinguish the wrist extension gesture from a resting state.").
  * What were the limitations of your study? (e.g., Single subject, limited number of gestures, controlled lab environment).
  * Discuss any challenges you faced and how you overcame them.

**6. Conclusion & Future Work:**

* **Content:** Briefly summarize the project's success. Then, dedicate a significant paragraph to **Future Work**, where you will integrate Professor Watson's advice.
    > *"Building upon the success of this project, the next logical step for the planned capstone is to explore more advanced feature extraction techniques. Following the advice of Professor Watson (Personal Communication, October 2025), a future iteration would involve transforming the raw sEMG snippets into spectrograms via an STFT. These 2D representations could then be used to fine-tune a pre-trained Convolutional Neural Network (CNN) for classification. This deep learning approach could potentially capture more complex signal characteristics and would be evaluated against the performance of the classical SVM pipeline established in this work."*

---

#### **4.2: The Presentation & Live Demonstration**

**Objective:** To present the project to an audience in a clear, concise, and compelling narrative, culminating in a live demonstration.

**Roundtable Discussion: Delivering a Powerful Presentation**

**Moderator:** "Dr. Sharma, beyond the written report, Carl needs to present his work. What is the key to an effective technical presentation?"

**HCI Researcher (Dr. Sharma):** "A presentation is not a reading of your paper; it is a **story**. The most powerful presentations follow a simple narrative arc. For this project, the story is 'The Journey of a Signal.'

**Here is your presentation structure:**

1. **The Hook (The Problem):** Start with a picture of a cyclist in traffic. "Every day, cyclists face a choice: signal with your hand, or keep your hand on the brake. What if we could do both?" This immediately makes the project relatable and important.

2. **The Cast of Characters (The Hardware):** Show a single, clean slide with a high-quality photo of your final assembled hardware. Briefly introduce the "brain" (ESP32) and the "senses" (AD8232).

3. **The Obstacle Course (The Challenge):** Show a plot of the raw EMG signal. "This is what your body's electricity looks like—it's tiny, noisy, and chaotic. How can a computer make sense of this?" This sets up the need for your solution.

4. **The Training Montage (The ML Pipeline):** Use a simple flowchart diagram to show your pipeline: `Raw Signal -> Feature Engineering -> SVM Model -> Decision`. Explain in one sentence what each step does.

5. **The Climax (THE LIVE DEMO):** This is the most important part of your presentation.
    * Have your electrodes on and the system running.
    * Share your screen showing the PlatformIO Serial Monitor.
    * **Narrate your actions:** "As you can see, the numbers are stable while I'm in a resting grip. Now, I will perform the signal gesture—opening my palm."
    * **The Payoff:** The audience will see the numbers jump in the monitor, and the LED on your board will light up. "The model has correctly classified the gesture." This provides undeniable proof that your system works.

6. **The Resolution (The Results):** Show the slide with your final Accuracy score and Confusion Matrix. "The live demo isn't a fluke. After rigorous testing using cross-validation, the model achieved an accuracy of 9X.X%."

7. **The Sequel (Future Work):** Briefly mention your plan for the capstone: a two-channel system and exploring CNNs. This shows you have a long-term vision.

---

#### **4.3: Code & Data Reproducibility**

**Objective:** To package your code and data in a professional format that allows for verification and sharing.

**Roundtable Discussion: The Importance of a Clean Repository**

**Moderator:** "Dr. Li, what is the final step for packaging the technical artifacts?"

**Electrical Engineer (Dr. Li):** "The final step is to create a clean, public **GitHub repository**. A link to a well-documented repository in your report is a massive sign of competence.

**Your repository must contain:**

1. **A `/firmware` folder:** Containing your complete PlatformIO project (`main.cpp`, `platformio.ini`).
2. **A `/data_analysis` folder:** Containing your Jupyter Notebook (`.ipynb` file) and the Python "Lab Assistant" script.
3. **A `/data` folder:** Containing the **raw `.txt` snippet files** you collected. Do not commit the large, final CSV, as it can be regenerated by your notebook.
4. **A `README.md` file:** This is the front page of your project. It must clearly explain:
    * What the project is.
    * What hardware is required.
    * How to set up the software environment.
    * How to run the data collection and analysis scripts to reproduce your results.

This completes the project loop, making your work transparent, verifiable, and professional."
