import os
import json
import numpy as np
import tensorflow as tf
from flask import Flask, request, render_template

from DataProcessing import DataProcessing


app = Flask(__name__)

modelName = "12-24 22h45m59s (Experiment 13) CNN Model B (200 Epochs) (IEMOCAP EmoDB) (Data Aug 3A) (5 Emotions with Merge and Split 4 Ignore 2) (00001 lr 0001 decay)"
labelsToInclude = ['Anger', 'Frustration', 'Happiness', 'Neutral', 'Sadness']
splitDuration = 4
ignoreDuration = 2

# Load Model
print('Loading Model...')
modelDir = os.path.join(os.getcwd(), "models", modelName)
model = tf.keras.models.load_model(modelDir)
print('Model Loading Completed!\n')

@app.route('/')
def home():
  return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
  data = request.get_json()
  # print(data['sampling_rates'])
  # print(data['audio_data'][0])
  x_test = data['audio_data'][0]
  
  # Load Data
  dataModel = DataProcessing(labelsToInclude=labelsToInclude, splitDuration=splitDuration, ignoreDuration=ignoreDuration)
  dataModel.loadAndExtractTestData()
  dataModel.processData()
  
  
  return render_template('index.html', prediction_text='successful')
  # self.y_pred = np.argmax(model.predict(self.x_test), axis=1)

if __name__ == "__main__":
  app.run()