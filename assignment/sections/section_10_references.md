# Section 10: References

## Academic Publications

1. **Bao, L., & Intille, S. S. (2004).** "Activity recognition from user-annotated acceleration data." *Pervasive Computing: Second International Conference, PERVASIVE 2004*, 1-17. Springer.
   - Foundational work on time-domain feature extraction for IMU-based activity recognition

2. **Chawla, N. V., Bowyer, K. W., Hall, L. O., & Kegelmeyer, W. P. (2002).** "SMOTE: Synthetic Minority Over-sampling Technique." *Journal of Artificial Intelligence Research*, 16, 321-357.
   - SMOTE algorithm for handling imbalanced classification datasets

3. **Cortes, C., & Vapnik, V. (1995).** "Support-vector networks." *Machine Learning*, 20(3), 273-297.
   - Original SVM formulation and maximum-margin classification theory

4. **Goodfellow, I., Bengio, Y., & Courville, A. (2016).** *Deep Learning.* MIT Press.
   - Comprehensive textbook on neural networks, CNNs, and RNNs
   - Chapters 6.2 (Convolutional Networks), 10.1 (Recurrent Neural Networks)

5. **Hastie, T., Tibshirani, R., & Friedman, J. (2009).** *The Elements of Statistical Learning: Data Mining, Inference, and Prediction* (2nd ed.). Springer.
   - Chapter 7: Model Assessment and Selection (cross-validation, bias-variance trade-off)

6. **Hochreiter, S., & Schmidhuber, J. (1997).** "Long short-term memory." *Neural Computation*, 9(8), 1735-1780.
   - Original LSTM paper solving vanishing gradient problem in RNNs

7. **Kingma, D. P., & Ba, J. (2014).** "Adam: A method for stochastic optimization." *arXiv preprint arXiv:1412.6980*.
   - Adam optimizer algorithm (adaptive moment estimation)

8. **McNemar, Q. (1947).** "Note on the sampling error of the difference between correlated proportions or percentages." *Psychometrika*, 12(2), 153-157.
   - McNemar's test for paired classifier statistical comparison

9. **Paradiso, J., Abler, C., Hsiao, K., & Reynolds, M. (1997).** "The Magic Carpet: Physical Sensing for Immersive Environments." *CHI '97 Extended Abstracts on Human Factors in Computing Systems*, 277-278.
   - Early accelerometer-based gesture recognition at MIT Media Lab

10. **Platt, J. (1998).** "Sequential Minimal Optimization: A Fast Algorithm for Training Support Vector Machines." *Microsoft Research Technical Report MSR-TR-98-14*.
    - SMO algorithm for efficient SVM training

11. **Powers, D. M. (2011).** "Evaluation: From Precision, Recall and F-Measure to ROC, Informedness, Markedness and Correlation." *Journal of Machine Learning Technologies*, 2(1), 37-63.
    - Comprehensive review of classification metrics

12. **Prechelt, L. (1998).** "Early Stopping—But When?" In *Neural Networks: Tricks of the Trade* (pp. 55-69). Springer.
    - Theory and practice of early stopping for neural network regularization

13. **Radford, A., Kim, J. W., Xu, T., Brockman, G., McLeavey, C., & Sutskever, I. (2022).** "Robust Speech Recognition via Large-Scale Weak Supervision." *arXiv preprint arXiv:2212.04356*.
    - Whisper model for speech recognition

14. **Stevens, W. R. (1998).** *UNIX Network Programming, Volume 1: The Sockets Networking API* (3rd ed.). Addison-Wesley.
    - Comprehensive guide to socket programming and UDP communication

15. **Wang, Z., Yan, W., & Oates, T. (2019).** "Deep Learning for Sensor-based Activity Recognition: A Survey." *Pattern Recognition Letters*, 119, 3-11.
    - Survey of deep learning methods for IMU-based activity recognition

16. **Welch, B. L. (1947).** "The generalization of 'Student's' problem when several different population variances are involved." *Biometrika*, 34(1-2), 28-35.
    - Welch's t-test for statistical significance testing

---

## Software Libraries and Frameworks

17. **Android Sensor API Documentation.** https://developer.android.com/guide/topics/sensors/sensors_motion
    - Official Android documentation for motion sensors (accelerometer, gyroscope)

18. **imbalanced-learn (imblearn).** https://imbalanced-learn.org/
    - Python library for handling imbalanced datasets (SMOTE implementation)

19. **Joblib Documentation.** https://joblib.readthedocs.io/
    - Python library for model persistence (saving/loading pickled models)

20. **Matplotlib Documentation.** https://matplotlib.org/
    - Python plotting library for data visualization

21. **NumPy Documentation.** https://numpy.org/doc/
    - Fundamental Python library for numerical computing

22. **pandas Documentation.** https://pandas.pydata.org/docs/
    - Python data manipulation library (DataFrames, merge_asof for temporal alignment)

23. **pynput Documentation.** https://pynput.readthedocs.io/
    - Python library for controlling and monitoring input devices (keyboard simulation)

24. **Python asyncio Documentation.** https://docs.python.org/3/library/asyncio.html
    - Asynchronous I/O framework for non-blocking UDP socket handling

25. **scikit-learn Documentation.** https://scikit-learn.org/stable/
    - Machine learning library in Python
    - SVM: https://scikit-learn.org/stable/modules/svm.html
    - StandardScaler: https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html
    - GridSearchCV: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html
    - GroupKFold: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html
    - Metrics: https://scikit-learn.org/stable/modules/model_evaluation.html

26. **SciPy Documentation.** https://docs.scipy.org/doc/scipy/
    - Scientific computing library (FFT, statistical functions)
    - FFT: https://docs.scipy.org/doc/scipy/reference/fft.html
    - Statistics: https://docs.scipy.org/doc/scipy/reference/stats.html

27. **seaborn Documentation.** https://seaborn.pydata.org/
    - Statistical data visualization library (heatmaps, confusion matrices)

28. **TensorFlow Keras API.** https://www.tensorflow.org/api_docs/python/tf/keras
    - High-level neural network API
    - Layers: https://www.tensorflow.org/api_docs/python/tf/keras/layers
    - Callbacks: https://www.tensorflow.org/api_docs/python/tf/keras/callbacks
    - Optimizers: https://www.tensorflow.org/api_docs/python/tf/keras/optimizers

29. **WhisperX (Bain et al., 2023).** https://github.com/m-bain/whisperX
    - Time-accurate speech transcription with word-level timestamps
    - Paper: Bain, M., Huh, J., Han, T., & Zisserman, A. (2023). "WhisperX: Time-Accurate Speech Transcription of Long-Form Audio." *arXiv preprint arXiv:2303.00747*.

30. **Zeroconf (Python-zeroconf).** https://github.com/jstasiak/python-zeroconf
    - Pure Python implementation of multicast DNS service discovery (Bonjour/Avahi)

---

## Standards and Protocols

31. **Network Service Discovery (NSD) Protocol - RFC 6763.** https://datatracker.ietf.org/doc/html/rfc6763
    - DNS-Based Service Discovery standard used for automatic device discovery

32. **SENIAM (Surface EMG for Non-Invasive Assessment of Muscles).** http://www.seniam.org/
    - European recommendations for biosensor placement and signal processing

---

## Commercial Systems (Comparison Benchmarks)

33. **Apple Watch Gesture Control.** https://support.apple.com/guide/watch/use-quick-actions-apd5e3e5c4f9/watchos
    - Commercial smartwatch gesture recognition system

34. **Google Pixel Watch Documentation.** https://support.google.com/googlepixelwatch/
    - Official documentation for Pixel Watch sensors and capabilities

35. **Myo Gesture Control Armband (Thalmic Labs, 2016).** https://support.getmyo.com/ [Archived]
    - EMG-based gesture recognition armband (discontinued 2018)

36. **Nintendo Wii Remote (2006).** https://en.wikipedia.org/wiki/Wii_Remote
    - Early consumer product with 3-axis accelerometer gesture recognition

37. **Xbox Kinect (2010).** https://en.wikipedia.org/wiki/Kinect
    - Computer vision-based full-body gesture tracking system

---

## Course Materials and Assignment Context

38. **CS156 - Machine Learning, Professor Watson.** Minerva University, Fall 2025.
    - Assignment brief: "Pipeline - First Draft"
    - Learning objectives: MLCode, MLExplanation, MLMath, MLFlexibility

39. **Watson Preferred Assignment Standards.** Internal course document.
    - Based on live grading session and example evaluation rubric

---

## Project-Specific Resources

40. **Silksong Controller GitHub Repository.** https://github.com/Furuta-Mototada/v3-watch_SilksongController_25TPE
    - Source code, data collection scripts, model training notebooks

41. **Android Wear OS Application (MainActivity.kt).** Project repository: `Android/app/src/main/java/com/cvk/silksongcontroller/`
    - Custom Kotlin application for sensor streaming via UDP

42. **CNN-LSTM Training Notebook.** Project repository: `notebooks/watson_Colab_CNN_LSTM_Training.ipynb`
    - Google Colab notebook for deep learning model training

43. **Data Collection Scripts.**
    - `src/continuous_data_collector.py`: Voice-labeled data collection
    - `src/data_collector.py`: Manual guided data collection
    - `docs/Phase_V/process_transcripts.sh`: WhisperX post-processing pipeline

44. **Phase Documentation.**
    - `docs/Phase_IV/ML_DEPLOYMENT_GUIDE.md`: SVM deployment guide
    - `docs/Phase_V/CNN_LSTM_ARCHITECTURE.md`: Deep learning architecture design
    - `docs/Phase_V/DATA_COLLECTION_GUIDE.md`: Voice-labeling methodology

---

## Data and Model Artifacts

45. **Trained Models** (Project repository: `main/models/`):
    - `gesture_classifier_binary.pkl`: Binary SVM (walk/idle)
    - `gesture_classifier_multiclass.pkl`: Multiclass SVM (8 gestures)
    - `cnn_lstm_best.h5`: CNN-LSTM model (deployed version)
    - `feature_scaler_*.pkl`: StandardScaler objects for normalization
    - `feature_names_*.pkl`: Feature ordering for model compatibility

46. **Confusion Matrices** (Project repository: `main/models/`):
    - `binary_confusion_matrix.png`: SVM binary classification results
    - `multiclass_confusion_matrix.png`: CNN-LSTM multiclass results

---

## Total References: 46

**Categories**:
- Academic papers: 16
- Software libraries: 14
- Standards/protocols: 2
- Commercial systems: 5
- Course materials: 2
- Project-specific: 7

---

## Citation Style

References follow a hybrid format combining:
- **Academic papers**: Author-date (APA style) with full citation details
- **Software documentation**: Official documentation URLs with access dates implied (current as of October 2025)
- **Project artifacts**: Repository paths for reproducibility

All references are directly cited in Sections 1-9 where relevant, with specific equation derivations, code implementations, or methodological details attributed to their original sources.

---

## Data Availability Statement

**Training data**: Available in project repository under `main/data/` (anonymized sensor streams, no personally identifiable information).

**Trained models**: Available in project repository under `main/models/` for reproducibility.

**Code**: Fully open-source under MIT license in project GitHub repository.

**Voice recordings**: Not included in repository (contain personal audio) but methodology is fully documented for replication.

---

## Acknowledgments

- **Professor Watson** for CS156 course structure and assignment guidance
- **Google Colab** for free T4 GPU access (deep learning training)
- **WhisperX authors** for open-source speech recognition tool
- **Scikit-learn and TensorFlow teams** for robust ML frameworks
- **Hollow Knight: Silksong** (Team Cherry) for inspiring this project [Still waiting for release!]
