# Section 10: References

## Python Libraries and Frameworks

1. **scikit-learn** - Machine learning library
   - SVC (Support Vector Classifier): https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html
   - StandardScaler: https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html
   - train_test_split: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html
   - classification_report: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html
   - confusion_matrix: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html
   - Model persistence: https://scikit-learn.org/stable/model_persistence.html

2. **NumPy** - Numerical computing
   - Official documentation: https://numpy.org/doc/
   - Array operations: https://numpy.org/doc/stable/reference/arrays.html

3. **pandas** - Data manipulation
   - Official documentation: https://pandas.pydata.org/docs/
   - read_csv: https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
   - DataFrame: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html

4. **SciPy** - Scientific computing
   - FFT module: https://docs.scipy.org/doc/scipy/reference/fft.html
   - Statistics module: https://docs.scipy.org/doc/scipy/reference/stats.html
   - rfft: https://docs.scipy.org/doc/scipy/reference/generated/scipy.fft.rfft.html
   - skew: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.skew.html
   - kurtosis: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kurtosis.html

5. **matplotlib** - Plotting and visualization
   - Official documentation: https://matplotlib.org/stable/index.html
   - pyplot: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.html

6. **seaborn** - Statistical visualization
   - Official documentation: https://seaborn.pydata.org/
   - heatmap: https://seaborn.pydata.org/generated/seaborn.heatmap.html

7. **joblib** - Model persistence
   - Official documentation: https://joblib.readthedocs.io/
   - Dump/load: https://joblib.readthedocs.io/en/latest/persistence.html

8. **pynput** - Input device control
   - Official documentation: https://pynput.readthedocs.io/
   - Keyboard control: https://pynput.readthedocs.io/en/latest/keyboard.html

9. **pathlib** - File system paths
   - Official documentation: https://docs.python.org/3/library/pathlib.html

10. **asyncio** - Asynchronous I/O
    - Official documentation: https://docs.python.org/3/library/asyncio.html

11. **zeroconf** - Network service discovery
    - GitHub repository: https://github.com/jstasiak/python-zeroconf

## Academic Papers and Technical Documents

12. **Cortes, C., & Vapnik, V. (1995).** "Support-vector networks." *Machine Learning*, 20(3), 273-297.
    - Original SVM paper introducing support vector machines

13. **Android Sensor Documentation**
    - Motion sensors: https://developer.android.com/guide/topics/sensors/sensors_motion
    - Sensor event reference: https://developer.android.com/reference/android/hardware/SensorEvent

## Machine Learning Concepts

14. **Confusion Matrix** - Visualization of classification performance
    - Wikipedia: https://en.wikipedia.org/wiki/Confusion_matrix

15. **F1 Score** - Harmonic mean of precision and recall
    - Wikipedia: https://en.wikipedia.org/wiki/F-score

16. **Cross-validation** - Model evaluation technique
    - scikit-learn guide: https://scikit-learn.org/stable/modules/cross_validation.html

17. **Feature scaling** - Data preprocessing for machine learning
    - scikit-learn preprocessing: https://scikit-learn.org/stable/modules/preprocessing.html

18. **RBF Kernel** - Radial basis function for SVM
    - scikit-learn SVM kernels: https://scikit-learn.org/stable/modules/svm.html#kernel-functions

## Signal Processing

19. **Fast Fourier Transform (FFT)** - Frequency domain analysis
    - SciPy FFT guide: https://docs.scipy.org/doc/scipy/tutorial/fft.html
    - Wikipedia: https://en.wikipedia.org/wiki/Fast_Fourier_transform

20. **Statistical moments** - Skewness and kurtosis
    - SciPy stats: https://docs.scipy.org/doc/scipy/reference/stats.html

## Hardware and Protocols

21. **IMU (Inertial Measurement Unit)** - Motion sensing
    - Wikipedia: https://en.wikipedia.org/wiki/Inertial_measurement_unit

22. **UDP (User Datagram Protocol)** - Network communication
    - Python socket: https://docs.python.org/3/library/socket.html
    - Wikipedia: https://en.wikipedia.org/wiki/User_Datagram_Protocol

23. **Network Service Discovery (NSD)** - mDNS/DNS-SD
    - Android NSD guide: https://developer.android.com/training/connect-devices-wirelessly/nsd

## Project-Specific Resources

24. **Main directory structure**: `/home/runner/work/v3-watch_SilksongController_25TPE/v3-watch_SilksongController_25TPE/main/`
    - Training script: `notebooks/SVM_Local_Training.py`
    - Real-time controller: `src/udp_listener_dashboard.py`
    - Trained models: `models/*.pkl`
    - Training data: `data/button_collected/*.csv`

25. **Configuration**: `main/config.json`
    - Network settings (IP, port)
    - Keyboard mappings

## Total References: 25

Categories:
- Python libraries: 11
- Academic papers: 2
- ML concepts: 5
- Signal processing: 2
- Hardware/protocols: 3
- Project files: 2
