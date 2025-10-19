# Alternative Data Collection: Button Grid Android App

**Status**: Brainstorming Phase  
**Created**: October 18, 2025  
**Context**: Addressing messy voice-labeled data and exploring more controlled data collection methods

## Current Situation

### The Problem
Our Phase V voice-controlled data collection approach has revealed significant challenges:

1. **Data Quality Issues**: Voice labels are noisy and imprecise
   - Coordination between mouth (speaking) and body (performing gestures) is difficult
   - Walk vs. non-walk binary classification is messy in practice
   - Action boundaries are unclear when transcribed from audio
   - WhisperX post-processing helps but doesn't solve fundamental collection issues

2. **Organic vs. Controlled Trade-off**
   - Current approach: Organic gameplay but imprecise labeling
   - Need: More controlled labeling without losing natural motion data

3. **Educational Context**
   - This is a **first draft pipeline** for a machine learning course
   - Emphasis should be on demonstrating fundamentals, not over-engineering
   - Second and final draft iterations will come later
   - Need clean, explainable results for academic evaluation

### Current Data Status
We have collected sessions using voice commands but acknowledge:
- The raw data is extremely messy
- Action vs. walk vs. non-walk classification boundaries are unclear
- May not be suitable for clean first draft demonstration

## Expert Panel Discussion

### Participants
1. **Prof. Andrew Ng** - Machine Learning fundamentals, practical AI deployment
2. **Prof. Fei-Fei Li** - Computer vision, human-centric AI, data quality
3. **Prof. Michael I. Jordan** - Statistical machine learning, experimental design
4. **Don Norman** - Human-computer interaction, design thinking
5. **Eric Ries** - Lean methodology, rapid iteration, MVP development

---

### Prof. Andrew Ng
*Core Principles: Start simple, iterate with data, focus on the data-centric AI approach*

**Probing Question:** 
"What is the minimum viable dataset that would demonstrate your ML pipeline works, and how can you collect it in the most reproducible way possible?"

**Framework: Data-Centric AI**
Rather than focusing on model architecture, focus on systematic data improvement. The button grid approach exemplifies this - you're not changing the sensor hardware or ML algorithm, you're improving label quality through better data collection UX.

**How I'd Approach This:**

*Obvious Solution:*
1. **Button Grid for Discrete Actions**
   - 2x4 grid (8 buttons total) on phone held in right hand
   - Each button = one action type (walk, punch, jump, turn_left, turn_right, dash, idle, noise)
   - Press and hold = record that action
   - Release = stop recording
   - Each press-release = one labeled CSV file with timestamps

*Non-Obvious Solution:*
2. **Stratified Recording Sessions**
   - Don't collect "natural gameplay" - collect specific action libraries
   - Session 1: Only walking variations (slow walk, fast walk, uphill, downhill)
   - Session 2: Only combat (punch combos, different intensities)
   - Session 3: Transitions between states
   - This creates balanced datasets by design, not by post-processing

**Why This Works:**
- You're a student with limited time - spend it on clean data, not cleaning messy data
- First draft should demonstrate understanding of pipeline: collection → features → training → deployment
- The button grid is reproducible - anyone can replicate your methodology

---

### Prof. Fei-Fei Li
*Core Principles: Human-centered AI, ImageNet-style systematic data collection, quality over quantity*

**Probing Question:**
"How might your data collection methodology itself become a contribution to the field of wearable gesture recognition research?"

**Framework: Systematic Data Construction**
ImageNet succeeded not just through scale, but through systematic curation. Your button grid approach is creating a "protocol" for reproducible gesture datasets from smartwatches.

**How I'd Approach This:**

*Obvious Solution:*
1. **Visual Feedback System**
   - Phone screen shows current button state with color coding
   - Real-time sensor visualization (like an oscilloscope)
   - Countdown timer before recording starts (3-2-1-GO)
   - Post-action review: "Did that feel right? Keep/Discard"
   - This adds human-in-the-loop quality control

*Non-Obvious Solution:*
2. **Multi-Person Dataset Collection**
   - Your button grid app could be shared with classmates
   - Each person collects 10 minutes per gesture
   - You now have person-independent models (stronger for generalization)
   - First draft: your data only
   - Future drafts: demonstrate transfer learning with others' data

**Research Contribution:**
Document your data collection protocol thoroughly:
- Physical setup (how to hold watch, phone position)
- Environmental conditions (sitting, standing, walking in place)
- Number of repetitions per gesture
- This becomes part of your "methods" section and could help others

---

### Prof. Michael I. Jordan
*Core Principles: Statistical rigor, experimental design, understanding uncertainty*

**Probing Question:**
"What confounding variables in your current data collection make it impossible to isolate whether your model is learning gestures versus learning something else?"

**Framework: Controlled Experiments**
Your voice-based approach introduces confounding variables:
- Speaking changes breathing patterns → affects torso movement → sensed by watch
- Coordination lag between speech and action
- Fatigue effects over long sessions

The button grid removes these confounds.

**How I'd Approach This:**

*Obvious Solution:*
1. **A/B Testing Framework**
   - Collect same gesture set with voice labels AND button grid
   - Train two separate models
   - Compare: accuracy, confusion matrices, failure modes
   - This becomes your "results" section: empirical proof that collection method matters

*Non-Obvious Solution:*
2. **Hierarchical Data Structure**
   - Don't just label "punch" - label "punch_light", "punch_medium", "punch_heavy"
   - Button long-press duration = intensity proxy
   - Model 1 (coarse): 4 classes (walk, punch, jump, idle)
   - Model 2 (fine): 8+ classes with intensity
   - Show that your pipeline can handle different granularities

**Statistical Rigor:**
- Pre-register your experiment plan (write it before collecting data)
- Define success metrics upfront: "First draft successful if >70% accuracy on 4-class problem"
- This prevents p-hacking and demonstrates scientific thinking

---

### Don Norman
*Core Principles: User-centered design, affordances, feedback, human error is design failure*

**Probing Question:**
"What would make your data collection so intuitive that you could do it while focusing 80% attention on your actual movements, not the interface?"

**Framework: Affordances and Signifiers**
Your button grid must provide clear signifiers of state and strong affordances for interaction.

**How I'd Approach This:**

*Obvious Solution:*
1. **Haptic + Visual + Audio Feedback**
   - Button press → phone vibrates once (action started)
   - Button release → phone vibrates twice (action recorded)
   - Screen background color matches current action
   - Optional: spoken confirmation "Punch recorded" (for eyes-free use)
   - Error states are impossible by design (can't press two buttons simultaneously)

*Non-Obvious Solution:*
2. **Physical Grip Design**
   - Design for one-handed phone operation in right hand
   - Watch on left wrist (standard wear)
   - Buttons arranged for thumb operation
   - Large hit targets (80x80 dp minimum)
   - Consider: External Bluetooth button (like a presentation clicker)
   - Nintendo Switch Joy-Con as inspiration - physical, tactile, reliable

**Design Iterations:**
1. First prototype: Simple grid, test with yourself
2. Second iteration: Add feedback mechanisms
3. Third iteration: Optimize for "flow state" - you forget the interface exists

---

### Eric Ries
*Core Principles: Build-Measure-Learn, MVP, validated learning, pivot or persevere*

**Probing Question:**
"What is the riskiest assumption in your project, and what's the cheapest experiment to validate it?"

**Framework: Lean Methodology**
Riskiest assumption: "Motion data from a smartwatch CAN reliably distinguish gameplay gestures"

**How I'd Approach This:**

*Obvious Solution:*
1. **Minimum Viable Data Collection (MVDC)**
   - Don't build the full button grid app yet
   - Use existing Android app with UDP
   - Manually label data files AFTER collection
   - Rename files: `20251018_140523.csv` → `20251018_140523_punch.csv`
   - Train model with 20 samples per gesture
   - If accuracy >60%, then invest time in button grid app

*Non-Obvious Solution:*
2. **The Concierge MVP**
   - You already have the watch streaming data
   - Have a friend sit next to you with a laptop
   - You perform gesture, friend presses key to label it
   - Friend's laptop saves label + timestamp
   - Merge with sensor data post-hoc
   - Tests the full pipeline in 1 hour, before writing any new code

**Pivot/Persevere Decision:**
After MVDC experiment:
- **If model fails (<50% accuracy)**: Pivot → Maybe smartwatch isn't the right sensor (try phone in pocket instead)
- **If model succeeds (>60%)**: Persevere → Build proper button grid data collection app
- **If model excellent (>80%)**: Pivot → Skip button grid, current method is good enough

**Timeline Optimization:**
- Week 1: MVDC experiment (manual labeling)
- Week 2: If successful, build button grid app
- Week 3: Collect clean dataset
- Week 4: Train and evaluate
- **For first draft**: Just demonstrate MVDC results

---

## Proposed Solution: Button Grid App Specification

### Technical Design

**Layout: 2x4 Grid (Two columns, four rows)**
```
┌─────────────┬─────────────┐
│   WALK      │   IDLE      │  ← Row 1: Primary states
├─────────────┼─────────────┤
│   PUNCH     │   JUMP      │  ← Row 2: Combat actions
├─────────────┼─────────────┤
│  TURN_LEFT  │  TURN_RIGHT │  ← Row 3: Direction
├─────────────┼─────────────┤
│   DASH      │   NOISE     │  ← Row 4: Special + baseline
└─────────────┴─────────────┘
```

**Interaction Model:**
1. Press and hold button → Start recording that action + timestamp
2. Release button → Stop recording + timestamp
3. Each press-release cycle creates one training sample
4. File naming: `YYYYMMDD_HHMMSS_ACTION_DURATION.csv`

**UDP Protocol Extension:**
```json
{
  "type": "label_event",
  "action": "punch",
  "event": "start" | "end",
  "timestamp_ms": 1729267234567
}
```

Watch app doesn't change - phone app sends label events to Python controller via UDP.

### Implementation Phases

**Phase 1: MVP (This Week)**
- Repurpose existing Android app
- Add simple label event sending
- Manual file organization

**Phase 2: Button Grid UI (Next Sprint)**
- 2x4 button grid layout
- Hold-to-record interaction
- Visual state feedback

**Phase 3: Polish (Future)**
- Haptic feedback
- Audio confirmations
- Session management
- Statistics dashboard

### Data Collection Protocol

**Per-Gesture Requirements:**
- Minimum: 30 samples (30 press-release cycles)
- Recommended: 50 samples for robust training
- Duration: 2-5 seconds per sample
- Total time: ~15 minutes for all 8 gestures

**Recording Guidelines:**
1. **WALK**: Natural walking motion in place
2. **IDLE**: Standing still, minimal movement
3. **PUNCH**: Forward punching motion with right arm
4. **JUMP**: Jumping in place (watch arm swings)
5. **TURN_LEFT/RIGHT**: Turning body 90 degrees
6. **DASH**: Quick forward lunge
7. **NOISE**: Random movements (negative class)

### Advantages Over Voice Labeling

✅ **Precision**: Button press/release gives exact time boundaries  
✅ **Coordination**: No conflict between speaking and moving  
✅ **Repeatability**: Anyone can follow the protocol  
✅ **Real-time**: No post-processing needed  
✅ **Deterministic**: No transcription errors or ambiguity  
✅ **Balanced**: Collect equal samples per class by design  

### Disadvantages

❌ **Less Organic**: Not "natural gameplay" data  
❌ **Two-Handed**: Requires phone in one hand  
❌ **Context Switch**: Mental overhead of pressing buttons  
❌ **Artificial**: Lab-like conditions vs. real-world use  

## Recommendations

### For First Draft (Due Soon)
**Recommended Approach: Hybrid**

1. **Use existing voice-labeled data for initial demonstration**
   - Shows you completed Phase V
   - Demonstrates end-to-end pipeline
   - Acknowledge data quality issues in write-up

2. **Implement MVP button grid (manual labeling)**
   - Collect 20 samples per gesture (2 hours total)
   - Train second model
   - Compare results in discussion section

3. **Document design thinking**
   - Include this brainstorming document
   - Show iteration from voice → button grid
   - Discuss trade-offs (organic vs. controlled)

### For Second Draft (Future)
- Full button grid Android app with UI
- Larger, balanced dataset (100+ samples per gesture)
- Multi-person data collection
- Cross-validation across different contexts

### For Final Draft (Future)
- Real-world deployment testing
- Actual Hollow Knight: Silksong gameplay integration
- Confusion matrix analysis of failure modes
- Transfer learning from other users' data

## Next Steps

**Immediate Actions:**
1. ✅ Document this brainstorming (this file)
2. ⏳ Decide: Voice data vs. Button grid for first draft
3. ⏳ If button grid: Implement manual labeling MVP (4 hours)
4. ⏳ If voice data: Clean up existing sessions and retrain

**Decision Framework:**
- If submission is <1 week away → Use voice data, acknowledge limitations
- If submission is >2 weeks away → Try button grid MVP, compare approaches
- If time allows → Do both, make comparison the core of results section

## Related Documentation
- Phase V voice collection: `docs/Phase_V/README.md`
- WhisperX post-processing: `docs/Phase_V/WhisperX/WHISPERX_GUIDE.md`
- Data collection: `src/continuous_data_collector.py`
- Android app: `Android/app/src/main/java/com/cvk/silksongcontroller/MainActivity.kt`

---

**Note**: This document represents design thinking and iteration - not all ideas will be implemented. The goal is to explore options and make informed decisions for the academic pipeline project.
