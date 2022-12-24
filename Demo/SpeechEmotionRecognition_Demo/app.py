import os
import numpy as np
import tensorflow as tf
from flask import Flask, request, render_template

app = Flask(__name__)

modelName = "12-24 22h45m59s (Experiment 13) CNN Model B (200 Epochs) (IEMOCAP EmoDB) (Data Aug 3A) (5 Emotions with Merge and Split 4 Ignore 2) (00001 lr 0001 decay)"
modelDir = os.path.join(os.getcwd(), "models", modelName)
model = tf.keras.models.load_model(modelDir)

@app.route('/')
def home():
  return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
  testing1 = request.form.get('testing1')
  
  return render_template('index.html', prediction_text=testing1)
  # self.y_pred = np.argmax(model.predict(self.x_test), axis=1)

if __name__ == "__main__":
  app.run()