# Detecting Driver Drowsiness Using Machine Learning

Driver fatigue is one of the major causes of vehicle crashes. This project builds a neural network that detects signs of drowsiness and classifies the driver as alert or drowsy.<br/>
Utilized: Python, TensorFlow, openCV, scikit-learn, JavaScript

## Data

Data are collected from The University of Texas at Arlington Real-Life Drowsiness Dataset (UTA-RLDD): https://sites.google.com/view/utarldd/home. From the dataset, 16,320 frames featuring 34 participants with a diversity of race, gender, and facial features (glasses, facial hair, etc.) were extracted. Participants self recorded the videos at the time when they felt alert or drowsy. Next, facial marks and features, including pupil diameter, eye aspect ratio, head tilt angle, etc. were extracted and computed.

## Model

The CNN has three main layers and achieved an accuracy of 0.89 and validated accuracy of 0.72, which is a more than 15% improvement in prediction accuracy compared to the baseline model.

## System

The final system captures images from the front camera and detects driver drowsiness.

## Sources

Various sources and literature are incorporated in the project.

https://openaccess.thecvf.com/content_CVPRW_2019/papers/AMFG/Ghoddoosian_A_Realistic_Dataset_and_Baseline_Temporal_Model_for_Early_Drowsiness_CVPRW_2019_paper.pdf - Dataset on real life drowsiness detection

https://link.springer.com/article/10.1186/s40535-018-0054-9#:~:text=Videos%20are%20preprocessed%20and%20several,and%20head%20rotation%20(ROT).&text=A%20recent%20study%20used%20on,regions%20to%20detect%20driver%20drowsiness. Feature selection for driving fatigue

https://github.com/sandyying/APM-Drowsiness-Detection - Extract frames and face landmarks and build neural networks

https://towardsdatascience.com/drowsiness-detection-with-machine-learning-765a16ca208a Drowsiness detection with machine learning
