import os
import numpy as np
import tensorflow as tf
from DataProcessing import DataProcessing


modelName = "12-24 22h45m59s (Experiment 13) CNN Model B (200 Epochs) (IEMOCAP EmoDB) (Data Aug 3A) (5 Emotions with Merge and Split 4 Ignore 2) (00001 lr 0001 decay)"
labelsToInclude = ['Neutral', 'Frustration', 'Anger', 'Sadness', 'Happiness']
splitDuration = 4
ignoreDuration = 2

# Load Model
print('Loading Model...')
modelDir = os.path.join(os.getcwd(), "models", modelName)
model = tf.keras.models.load_model(modelDir)
print('Model Loading Completed!\n')

# Load Data
dataModel = DataProcessing(labelsToInclude=labelsToInclude, splitDuration=splitDuration, ignoreDuration=ignoreDuration)
dataModel.loadAndExtractTestData()
dataModel.processData()

y_pred = np.argmax(model.predict(dataModel.x_test), axis=1)

print('Prediction Result:')
for i, pred in enumerate(y_pred):
  predicted_label = labelsToInclude[y_pred[pred]]
  recording_name = dataModel.recording_names[i]
  
  print(f"{recording_name[0]:25} {recording_name[1]} ---> {predicted_label}")
