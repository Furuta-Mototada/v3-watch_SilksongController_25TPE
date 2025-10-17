# CS156 Assignment Checklist - Watson Preferred Standards

Based on the Watson Preferred examination of the example assignment, this checklist ensures your CS156 assignment meets all evaluation criteria.

---

## ✅ ML Explanation (Target: 3/5 baseline, 4-5 for excellence)

### Core Requirements
- [ ] **Clear problem statement** - What are you trying to solve? Why does it matter?
- [ ] **Step-by-step process** - No skipping steps; show your thinking
- [ ] **Model justification** - Why this model instead of alternatives?
- [ ] **Design decisions explained** - Document choices made and rejected approaches
- [ ] **Process reflection** - Show how you iterated and refined your approach

### Visual Communication
- [ ] **Data visualizations** - "Pictures worth a thousand words"
  - [ ] Raw data examples (e.g., signal plots for both classes)
  - [ ] Exploratory data analysis (distributions, patterns)
  - [ ] Model performance visualizations (confusion matrices, metrics)
- [ ] **Clear captions** - Every figure explains what you're seeing

### For This Project Specifically
- [ ] Explain why SVM over other classifiers
- [ ] Show examples of "Rest" vs "Signal" gestures visually
- [ ] Explain the feature extraction rationale (MAV, RMS, etc.)
- [ ] Document why you chose these specific EMG features

---

## 💻 ML Code (Target: 3/5 baseline, 4-5 for excellence)

### Basic Quality
- [ ] **Code runs without errors** - Test every cell before submission
- [ ] **Code does what you say it does** - Explanation matches implementation
- [ ] **Readable and documented** - Comments where needed, clear variable names
- [ ] **Produces expected results** - Output matches your analysis

### Advanced Quality (for 4-5 scores)
- [ ] **Implementation from scratch** - Key algorithms written manually
  - [ ] Compare scratch implementation vs library (show they match)
  - [ ] Demonstrate understanding of underlying mathematics
- [ ] **Heavy computational lifting** - Complex pipeline, multiple comparisons
- [ ] **Well-structured functions** - Reusable, modular code
- [ ] **Interactive visualizations** - Advanced plotting, dashboards

### For This Project
- [ ] Data loading code is clear and correct
- [ ] Feature extraction function is well-documented
- [ ] Cross-validation properly implemented
- [ ] Consider: Implement one feature (e.g., MAV) from scratch to compare

---

## 📐 ML Math (Target: 3/5 baseline, 4-5 for excellence)

### Essential Elements
- [ ] **Equations included** - Use LaTeX/Markdown math notation
- [ ] **Loss function explained** - Show the actual equation used
- [ ] **Variables defined** - What does each symbol mean?
- [ ] **Mathematical derivations** - How does the model compute predictions?

### Advanced Elements (for 4-5 scores)
- [ ] **Backpropagation steps** - If applicable, show weight updates
- [ ] **Residual calculations** - Show how error is computed
- [ ] **Pseudo-algorithms** - Flowchart of mathematical steps

### For This Project
- [ ] Write out SVM decision boundary equation: $f(x) = w^T x + b$
- [ ] Show feature extraction equations:
  - [ ] MAV: $\text{MAV} = \frac{1}{N}\sum_{i=1}^{N}|x_i|$
  - [ ] RMS: $\text{RMS} = \sqrt{\frac{1}{N}\sum_{i=1}^{N}x_i^2}$
  - [ ] Waveform Length: $\text{WL} = \sum_{i=1}^{N-1}|x_{i+1} - x_i|$
- [ ] Explain classification metrics (precision, recall, F1)
- [ ] Show confusion matrix interpretation

---

## 🔄 ML Flexibility (Target: 3/5 minimum, 4-5 for excellence)

### **REQUIREMENT: Use techniques NOT covered in class**

This is **mandatory** - you must go beyond class material.

### What Counts as Flexibility
- [ ] **Models not yet covered** - Check syllabus to see what's coming
  - For early assignments: Anything from later units counts
  - For later assignments: External research required
- [ ] **Loss functions not discussed** - Categorical cross-entropy, custom losses
- [ ] **Metrics beyond basics** - ROC curves, AUC, Cohen's Kappa
- [ ] **Advanced preprocessing** - Techniques specific to your data type

### For This Project (EMG Data)
- [ ] EMG-specific features (zero crossings, slope sign changes)
- [ ] Signal processing techniques (if not covered: filtering, windowing)
- [ ] Advanced normalization (MVC normalization is good!)
- [ ] Hyperparameter tuning with grid search
- [ ] Compare multiple kernel types for SVM (RBF, polynomial, sigmoid)

### How to Document Flexibility
- [ ] **Cite what you used** - Reference papers, documentation
- [ ] **Explain why you chose it** - What problem does it solve?
- [ ] **Show how it works** - Write the equation or algorithm
- [ ] **Compare to baseline** - How much did it improve results?

---

## 📊 Data Quality Requirements

### Dataset Characteristics
- [ ] **Balanced classes** - Equal or near-equal samples per class ✓ (25 each)
- [ ] **Sufficient sample size** - Enough data for meaningful training/testing ✓
- [ ] **Proper labeling** - Clear, unambiguous class assignments ✓
- [ ] **Data provenance documented** - How, when, where data was collected ✓

### Data Quality Indicators
- [ ] **Exploratory Data Analysis (EDA)** - Show data distributions
  - [ ] Signal amplitude ranges
  - [ ] Sample lengths consistency
  - [ ] MVC value reasonableness check
- [ ] **Statistical validation** - T-tests showing classes are distinguishable
- [ ] **Outlier detection** - Identify and handle anomalous samples

---

## 📝 Report Structure & Presentation

### Word Count Guidance
- Target: ~1000-1500 words of prose
- Note: Code, equations, and figures don't count heavily toward limit
- Quality over quantity - be concise but complete

### Essential Sections
1. **Introduction/Problem Statement** (clear and compelling) ✓
2. **Data Explanation** (what, how, why) ✓
3. **Methodology** (your pipeline, step-by-step)
4. **Results** (metrics, visualizations, interpretation)
5. **Discussion** (what worked, what didn't, why)
6. **Future Work** (what's next)
7. **References** (cite everything)

### Presentation Quality
- [ ] **Clean formatting** - Consistent style throughout
- [ ] **Section headers** - Logical flow and organization
- [ ] **No orphaned code** - Every code block has context
- [ ] **Professional tone** - Scientific writing style
- [ ] **Proofread** - No typos or grammatical errors

---

## 🎯 Common Pitfalls to Avoid

### From Ingrid's Assignment Example

❌ **Don't:**
- Use packages without explaining what they do
- Include 9 confusion matrices without explanation
- Skip mathematical documentation
- Assume reader knows techniques you're using
- Present results without interpretation

✅ **Do:**
- Document package functions you rely on
- Aggregate results into clear summaries
- Write out equations for all key techniques
- Explain everything, even "obvious" choices
- Always interpret your results

### Additional Warnings

❌ **Don't:**
- Use LLMs without safety net (no math = no credit)
- Only use library implementations (no learning demonstrated)
- Skip comparison with simpler baselines
- Ignore poor results (discuss failures!)
- Submit without testing every code cell

---

## 📋 Pre-Submission Checklist

### Final Verification

- [ ] **Run all code top-to-bottom** - Fresh kernel, no errors
- [ ] **Check all visualizations render** - Figures show up correctly
- [ ] **Verify math renders** - LaTeX equations display properly
- [ ] **Read it out loud** - Does explanation flow logically?
- [ ] **Check references** - All citations included
- [ ] **File organization** - Data, code, outputs properly structured
- [ ] **GitHub repository** - Clean, documented, runnable

### For This EMG Project

- [ ] `data_collector.py` is documented and ready to use
- [ ] `emg_data/` folder structure is correct
- [ ] Notebook loads data successfully
- [ ] All 50 samples collected (25 rest, 25 signal)
- [ ] MVC value saved and used for normalization
- [ ] Feature extraction working correctly
- [ ] Cross-validation results are reasonable
- [ ] Visualizations clearly show class separation

---

## 💯 Excellence Indicators (Aiming for 4-5 Scores)

### What Makes an Assignment Stand Out

1. **Novel comparisons** - Compare multiple approaches systematically
2. **Deep implementation** - Write something from scratch
3. **Thorough analysis** - Explore edge cases, failure modes
4. **Clear communication** - Could a peer reproduce your work?
5. **Scientific rigor** - Follow research best practices
6. **Creative applications** - Personal, interesting problem

### For This Project

Your EMG bike signal project has built-in excellence potential:
- ✓ **Personal relevance** - Real problem you face
- ✓ **Unique dataset** - Your own biosignals
- ✓ **Hardware integration** - Full-stack implementation
- ✓ **Scientific protocol** - Clinical-grade methodology
- ✓ **Future scalability** - Clear path to deployment

**Make the most of it:**
- Compare SVM to other classifiers (Logistic Regression, Decision Tree)
- Implement one feature extractor from scratch
- Show robust cross-validation strategy
- Discuss real-world deployment challenges
- Connect to broader HCI and wearable computing literature

---

## 🎓 Key Takeaway from Watson Preferred Session

> "Don't worry about winning everything. You got plenty of time for that. You got many races to run. Just make sure this one is a nice, solid one that you're proud of."
>
> — Professor Watson

**Translation:** Aim for consistent 3s across all four objectives as your baseline. Excellence (4-5 scores) should come from depth in areas you're passionate about, not from trying to maximize everything.

For this first assignment, focus on:
1. ✅ Rock-solid fundamentals (no missing pieces)
2. ✅ Clear, complete explanations
3. ✅ One or two areas of depth/flexibility
4. ✅ Professional presentation

The data collection script (`data_collector.py`) you now have provides the foundation. Use it to capture high-quality data, then focus your energy on thorough analysis and clear communication.

**You've got this! 🚴‍♂️⚡**

#### OCT 17 FEEDBACK TA
"Great work on completing all the extension questions so far!

Nice start to your assignment! I can see many ways to develop this project and I like the use of GroupKFold to avoid overfitting. I'd recommend adding baseline models such as RSME/ Logistic Regression to show model improvement.

I'd also add a short "how it works” section for each model - what function/decision rule it learns, the objective/loss it minimizes (and how it’s optimized), and how key hyperparameters control regularization - the math behind it."
4#cs156-MLDevelopment
Carl Vincent Kho - General - N/A