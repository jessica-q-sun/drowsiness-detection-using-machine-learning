# -*- coding: utf-8 -*-
"""Data_Training.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15xkSc6m-D4CwIf2JGfPAkJ0D4PQg1_EH
"""

# load library
import tensorflow as tf
import numpy as np
import cv2
import math
import pandas as pd
from scipy.spatial import distance
from google.colab.patches import cv2_imshow
from mlxtend.image import extract_face_landmarks
from tensorflow import keras
from tensorflow.keras.layers import Dense, Flatten, Conv1D, MaxPool1D, Dropout, Activation
from tensorflow.keras import Model, datasets, layers, models
from sklearn import metrics
import matplotlib.pyplot as plt

# mount to google drive
from google.colab import drive
drive.mount('/content/drive/')

"""# **1. Extract frames and facial landmarks from videos**"""

# here's an example of a frame of an alert participant
vidcap = cv2.VideoCapture('drive/My Drive/DrowsinessVideos/1/0.mov')
vidcap.set(cv2.CAP_PROP_POS_MSEC, 0)
frame = vidcap.read()[1]
cv2_imshow(frame)

# here's an example of a frame of the same participant, but self identified as feeling drowsy
vidcap = cv2.VideoCapture('drive/My Drive/DrowsinessVideos/1/10.mov')
vidcap.set(cv2.CAP_PROP_POS_MSEC, 0)
frame = vidcap.read()[1]
cv2_imshow(frame)

def getFrame(sec):
    vidcap.set(cv2.CAP_PROP_POS_MSEC, sec*1000)
    return vidcap.read()[1]

data = []
labels = []
# change the number here to loop through each video
for i in [1]:
  for j in [0, 10] :
    vidcap = cv2.VideoCapture('drive/My Drive/DrowsinessVideos/' + str(i) +'/' + str(j) + '.mov')
    sec = 0
    frameRate = 1
    frame  = getFrame(sec)
    count = 0
    # extract 240 frames from each video
    while count < 240: 
      landmarks = extract_face_landmarks(frame)
      if sum(sum(landmarks)) != 0:
        data.append(landmarks)
        labels.append([j])
        count += 1
      sec = round(sec + frameRate, 2)
      frame = getFrame(sec)

data = np.array(data)
labels = np.array(labels)

data.shape

labels.shape

# save files to google drive
np.save(open('Data_1.npy', 'wb'),data)
np.save(open('Labels_1.npy', 'wb'),labels)

!cp Data_1.npy "drive/My Drive/DriverData/"
!cp Labels_1.npy "drive/My Drive/DriverData/"

"""# **2. Extract facial features**"""

# define key features to detect drowsiness
def pupil_diameter(data):
  left_eye_diameter = distance.euclidean(data[37], data[40])
  right_eye_diatmer = distance.euclidean(data[44], data[47])
  return (left_eye_diameter + right_eye_diatmer)/2

def eye_aspect_ratio(data):
  left_eye_D1 = distance.euclidean(data[37], data[41])
  left_eye_D2 = distance.euclidean(data[38], data[40])
  left_eye_D3 = distance.euclidean(data[36], data[41])
  left_eye_ratio = (left_eye_D1 + left_eye_D2) / (2 * left_eye_D3)
  right_eye_D1 = distance.euclidean(data[43], data[47])
  right_eye_D2 = distance.euclidean(data[44], data[46])
  right_eye_D3 = distance.euclidean(data[42], data[45])
  right_eye_ratio = (right_eye_D1 + right_eye_D2) / (2 * right_eye_D3)
  return (left_eye_ratio + right_eye_ratio)/2

def head_tilt_degree(data):
  left_eye_left_corner = data[36]
  left_eye_right_corner = data[39]
  left_eye_tilt_rad =  math.atan2(left_eye_left_corner[1]-left_eye_right_corner[1], left_eye_right_corner[0]-left_eye_left_corner[0])
  left_eye_tilt = abs(math.degrees(left_eye_tilt_rad))
  right_eye_left_corner = data[42]
  right_eye_right_corner = data[45]
  right_eye_tilt_rad =  math.atan2(right_eye_left_corner[1]-right_eye_right_corner[1], right_eye_right_corner[0]-right_eye_left_corner[0])
  right_eye_tilt = abs(math.degrees(right_eye_tilt_rad))
  return (left_eye_tilt + right_eye_tilt)/2

def mouth_aspect_ratio(data):
    mouth_height = distance.euclidean(data[51], data[57])
    mouth_width = distance.euclidean(data[48], data[54])
    return mouth_height / mouth_width

def nasal_flare(data):
  left_nasal = distance.euclidean(data[31], data[32])
  right_nasal = distance.euclidean(data[34], data[35])
  return (left_nasal + right_nasal)/2

def mouth_to_eye(data):
  mouth_to_left_eye = distance.euclidean(data[57], data[39])
  mouth_to_right_eye = distance.euclidean(data[57], data[4])
  return (mouth_to_left_eye + mouth_to_right_eye)/2

# extract features from facial landmarks
combined_data = pd.DataFrame()
for i in range(1,35):
  data_file = np.load('drive/My Drive/DriverData/Data_' + str(i) + '.npy')
  labels = np.load('drive/My Drive/DriverData/Labels_' + str(i) + '.npy')
  features = []
  for data in data_file:
    pupil = pupil_diameter(data)
    eye_ratio = eye_aspect_ratio(data)
    head_tilt = head_tilt_degree(data)
    mouth_ratio = mouth_aspect_ratio(data)
    nasal = nasal_flare(data)
    mouth_eye = mouth_to_eye(data)
    features.append([pupil,eye_ratio,head_tilt,mouth_ratio,nasal,mouth_eye])

  feature_df = pd.DataFrame(features)
  feature_df.columns = ["pupil","eye_ratio","head_tilt","mouth_ratio","nasal","mouth_eye"]
  label_df = pd.DataFrame(labels)
  label_df.columns = ['Drowsiness']
  combined_data_single_participant = pd.concat([feature_df,label_df], axis=1)
  combined_data_single_participant['Participant'] = i
  combined_data = combined_data.append(combined_data_single_participant, ignore_index=True)

"""# **3. Normalize features**"""

# extract the first three frames of participants in their alert states
alert = combined_data[combined_data["Drowsiness"]==0] 
alert_1 = alert.iloc[0::240, :]
alert_2 = alert.iloc[1::240, :]
alert_3 = alert.iloc[2::240, :]
alert_first3 = [alert_1,alert_2,alert_3]
df_alert_first3 = pd.concat(alert_first3)
df_alert_first3 = df_alert_first3.sort_index()

# compute mean and standard deviation for each participant
df_means = df_alert_first3.groupby("Participant")["pupil","eye_ratio","head_tilt","mouth_ratio","nasal","mouth_eye"].mean()
df_std = df_alert_first3.groupby("Participant")["pupil","eye_ratio","head_tilt","mouth_ratio","nasal","mouth_eye"].std()
df_means.columns = ["pupil_mean","eye_ratio_mean","head_tilt_mean","mouth_ratio_mean","nasal_mean","mouth_eye_mean"]
df_means["Participant"] = df_means.index
df_means.index.names = ['index']
df_std.columns = ["pupil_std","eye_ratio_std","head_tilt_std","mouth_ratio_std","nasal_std","mouth_eye_std"]
df_std["Participant"] = df_std.index
df_std.index.names = ['index']

# merge the orginical data, mean data and std data 
final_data_mid_step = pd.merge(combined_data, df_means, on="Participant")
final_data = pd.merge(final_data_mid_step,df_std,on="Participant")

# compute the normazlied value for each feature
final_data["pupil_N"] = (final_data["pupil"]-final_data["pupil_mean"])/ final_data["pupil_std"]
final_data["eye_ratio_N"] = (final_data["eye_ratio"]-final_data["eye_ratio_mean"])/ final_data["eye_ratio_std"]
final_data["head_tilt_N"] = (final_data["head_tilt"]-final_data["head_tilt_mean"])/ final_data["head_tilt_std"]
final_data["mouth_ratio_N"] = (final_data["mouth_ratio"]-final_data["mouth_ratio_mean"])/ final_data["mouth_ratio_std"]
final_data["nasal_N"] = (final_data["nasal"]-final_data["nasal_mean"])/ final_data["nasal_std"]
final_data["mouth_eye_N"] = (final_data["mouth_eye"]-final_data["mouth_eye_mean"])/ final_data["mouth_eye_std"]

# only keep x and y data
final_data = final_data[["Participant","pupil","eye_ratio","head_tilt","mouth_ratio","nasal","mouth_eye","pupil_N","eye_ratio_N","head_tilt_N","mouth_ratio_N","nasal_N","mouth_eye_N","Drowsiness"]]

final_data.to_csv('driver_final_data.csv',index=False)
!cp driver_final_data.csv "drive/My Drive/DriverData/"

"""# **4. CNN**
The code should run successfully from here, provided with the driver_final_data.csv.
"""

df = pd.read_csv('drive/My Drive/DriverData/driver_final_data.csv')

# change drowsiness index from 10 to 1 for the model
df.loc[df['Drowsiness'] == 10, 'Drowsiness'] = 1
df = df.drop(["Participant"],axis=1)

# train to test ratio 7:3
train_size = 24
test_size = 10
train_data = df[:train_size*480]
test_data = df[-test_size*480:]

# generate train and test data
X_train = train_data.drop('Drowsiness',axis=1)
y_train = train_data['Drowsiness']
X_test = test_data.drop(["Drowsiness"],axis=1)
y_test = test_data["Drowsiness"]

# shape features to fit model input shape
X_train_shaped = np.expand_dims(X_train, axis=2)
X_test_shaped = np.expand_dims(X_test, axis=2)

model = tf.keras.Sequential()

# First layer
model.add(tf.keras.layers.Conv1D(64, kernel_size = 3, activation = 'relu', input_shape = (12,1)))

# Second layer
model.add(tf.keras.layers.Conv1D(32, kernel_size = 3, activation = 'relu'))
model.add(tf.keras.layers.Flatten())

# Third layer
model.add(tf.keras.layers.Dense(64, activation='relu'))
model.add(tf.keras.layers.Dropout(0.2))
model.add(tf.keras.layers.Dense(32, activation='relu'))
model.add(tf.keras.layers.Dropout(0.2))
model.add(tf.keras.layers.Dense(1,activation = 'sigmoid'))

model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.00001),
              loss = 'binary_crossentropy',
              metrics = ['accuracy'])
history = model.fit(X_train_shaped, y_train, validation_data = (X_test_shaped,y_test), epochs = 100)

# Model summary
model.summary()

# Percentage increase during the first 15 epochs
(history.history['accuracy'][16] - history.history['accuracy'][0])/history.history['accuracy'][0]

# Percentage increase from 20 - 100 epochs
(history.history['accuracy'][99] - history.history['accuracy'][16])/history.history['accuracy'][16]

# Plot training and testing accuracy
plt.plot(history.history['accuracy'], label='accuracy')
plt.plot(history.history['val_accuracy'], label = 'val_accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.title("Training and testing accuracy")
plt.ylim([0.45, 1])
plt.legend(loc='lower right')

# Plot training and testing loss
plt.plot(history.history['loss'], label='loss')
plt.plot(history.history['val_loss'], label = 'val_loss')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.title("Training and testing lost")
#plt.ylim([0.45, 1])
plt.legend(loc='lower right')

print("Confusion matrix:")
prediction = model.predict_classes(X_test_shaped)
print(metrics.confusion_matrix(y_test, prediction))

#batch_size = 32
train_ds = tf.data.Dataset.from_tensor_slices((train_images, train_labels)).shuffle(10000).batch(batch_size)

model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.00001),
              loss = 'binary_crossentropy',
              metrics = ['accuracy'])

class MyModel(Model):
    def __init__(self):
        super(MyModel, self).__init__()
        # First layer
        self.conv1 = Conv1D(64, kernel_size = 3,  activation='relu')

        # Layer 2
        self.conv2 = Conv1D(32, kernel_size = 3, activation='relu') 
        self.flatten = Flatten()

        # Layer 4
        self.d1 = Dense(64, activation='relu')
        self.dropout1 = Dropout(0.2)
        self.d2 = Dense(32, activation='relu')
        self.dropout2 = Dropout(0.2)
        self.d3 = Dense(1, activation='sigmoid')
    def call(self, x):
        # Layer 1
        x = self.conv1(x)
        # Layer 2
        x = self.conv2(x)
        x = self.flatten(x)
        # Layer 4
        x = self.d1(x)
        x = self.dropout1(x)
        x = self.d2(x)
        x = self.dropout2(x)
        x = self.d3(x)
        return x
modeltf = MyModel()

loss_object = tf.keras.losses.BinaryCrossentropy()
optimizer = tf.keras.optimizers.Adam()

train_loss = tf.keras.metrics.Mean(name='train_loss')
train_accuracy = tf.keras.metrics.CategoricalAccuracy(name='train_accuracy')

@tf.function
def train_step(images, labels):
    with tf.GradientTape() as tape:
        predictions = modeltf(images)
        loss = loss_object(labels, predictions)
    gradients = tape.gradient(loss, modeltf.trainable_variables)
    optimizer.apply_gradients(zip(gradients, modeltf.trainable_variables))
    train_loss(loss)
    train_accuracy(labels, predictions)

EPOCHS = 15
for epoch in range(EPOCHS):
    for images, labels in train_ds:
        train_step(images, labels)   
    modeltf.save_weights('/content', save_format='tf')
    print('Epoch:',str(epoch+1),' Training Loss:',str(train_loss.result()),' Training Accuracy:',str(train_accuracy.result()*100))
    train_loss.reset_states()
    train_accuracy.reset_states()

modeltf.load_weights('/content')
predictions = []
for img in test_images:
  img = img.reshape(1,100,100,1)
  predictions.append(np.argmax(modeltf(img),axis=1))
predictions_array = np.array(predictions)
test_array = np.argmax(test_labels, axis = 1)

# Output confusion matrix and accuracy 
print("TF model, confusion matrix:")
print(metrics.confusion_matrix(test_array, predictions))
print("")
print("Accuracy of TF model is ", metrics.accuracy_score(test_array, predictions))