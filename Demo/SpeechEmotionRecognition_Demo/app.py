import os
import shutil
import json
import numpy as np
import tensorflow as tf
from flask import Flask, request, render_template

from DataProcessing import DataProcessing

UPLOAD_DIR = os.path.join('static', 'data')

app = Flask(__name__)
app.config['UPLOAD_DIR'] = UPLOAD_DIR

modelName = "12-24 22h45m59s (Experiment 13) CNN Model B (200 Epochs) (IEMOCAP EmoDB) (Data Aug 3A) (5 Emotions with Merge and Split 4 Ignore 2) (00001 lr 0001 decay)"
labelsToInclude = ['Anger', 'Frustration', 'Happiness', 'Neutral', 'Sadness']
splitDuration = 4
ignoreDuration = 2

# Load Model
print('Loading Model...')
modelDir = os.path.join(os.getcwd(), "models", modelName)
model = tf.keras.models.load_model(modelDir)
print('Model Loading Completed!\n')

@app.errorhandler(413)
def too_large(e):
    return "File is too large", 413

@app.route('/')
def home():
  return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
  # 1). Empty upload directory
  for filename in os.listdir(app.config['UPLOAD_DIR']):
    file_path = os.path.join(app.config['UPLOAD_DIR'], filename)
    try:
      if os.path.isfile(file_path) or os.path.islink(file_path):
        os.unlink(file_path)
      elif os.path.isdir(file_path):
        app.config['UPLOAD_DIR'].rmtree(file_path)
    except Exception as e:
      errMsg = 'Delete previous audio data in backend failed! ' + e
      print('Failed: ' + errMsg)
      return {'data': [], 'status': 'failed', 'errMsg': errMsg}
  
  # 2). Get audio files and save in backend
  if (len(request.files) != 0):
    print(request.files)
    for filename in request.files:
      try:
        file = request.files[filename]
        file.save(os.path.join(app.config['UPLOAD_DIR'], file.filename))
      except Exception as e:
        errMsg = 'Save audio file in backend failed! ' + e
        print('Failed: ' + errMsg)
        return {'data': [], 'status': 'failed', 'errMsg': errMsg}
  else:
    warnMsg = 'No audio data to predict!'
    print('Warning: ' + warnMsg)
    return {'data': [], 'status': 'warning', 'errMsg': warnMsg}

  # 3). Load and Process data
  try:
    dataModel = DataProcessing(labelsToInclude=labelsToInclude, splitDuration=splitDuration, ignoreDuration=ignoreDuration)
    dataModel.loadAndExtractTestData(app.config['UPLOAD_DIR'])
    dataModel.processData()
  except Exception as e:
    errMsg = 'Data Processing Failed! ' + e
    print('Failed: ' + errMsg)
    return {'data': [], 'status': 'failed', 'errMsg': errMsg}
  
  # 4). Model Prediction
  try:
    y_pred = np.argmax(model.predict(dataModel.x_test), axis=1)
  except Exception as e:
    errMsg = 'Emotion Prediction from Model Failed! ' + e
    print('Failed: ' + errMsg)
    return {'data': [], 'status': 'failed', 'errMsg': errMsg}
  
  print('Result Predicted!')
  
  # 5). Pack and return
  predicted_data_list = []
  for i, pred in enumerate(y_pred):
    predicted_label = labelsToInclude[pred]
    recording_name = dataModel.recording_names[i]
  
    predicted_data_list.append({
      'name': recording_name[0],
      'section': recording_name[1],
      'emotion': predicted_label
    })  
  
  return {'data': predicted_data_list, 'status': 'ok', 'errMsg': ''}

  

if __name__ == "__main__":
  app.run()