import os
import numpy as np
import tensorflow as tf
from flask import Flask, request, render_template

app = Flask(__name__)

modelName = ""
modelDir = os.path.join(os.getcwd(), "models", modelName)
model = tf.keras.models.load_model(modelDir)

@app.route('/')
def home():
  return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
  float_features = [float(x) for x in request.form.values()]
  features = [np.array(float_features)]
  
  # self.y_pred = np.argmax(model.predict(self.x_test), axis=1)