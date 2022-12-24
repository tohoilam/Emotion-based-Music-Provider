import os
import numpy as np
import tensorflow as tf

modelName = ""
modelDir = os.path.join(os.getcwd(), "models", modelName)
model = tf.keras.models.load_model(modelDir)