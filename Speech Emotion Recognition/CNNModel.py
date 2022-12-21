import os
import pytz
import tensorflow as tf
import tensorboard
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

tz = pytz.timezone('Asia/Hong_Kong')

class CNNModel:
  def __init__(self, modelName, experimentName, ySize=9, learning_rate=0.0001, decay=0.001):
    self.experimentName = datetime.now(tz=tz).strftime("%m-%d %Hh%Mm%Ss ") + experimentName

    self.logDir = os.path.join(os.getcwd(), "IEMOCAP_ModelLog", self.experimentName)
    self.resultDir = os.path.join(os.getcwd(), "IEMOCAP_TrainedModel", self.experimentName)
    
    self.ySize = ySize
    
    if (modelName == "modelA"):
      model = self.modelA()
    elif (modelName == "modelB"):
      model = self.modelB()
    elif (modelName == "modelC"):
      model = self.modelC()
    elif (modelName == "modelD"):
      model = self.modelD()
    elif (modelName == "modelE"):
      model = self.modelE()
    else:
      model = None
      raise NameError("modelName does not exist. Should be modelA, modelB, modelC, modelD, or modelE")
    
    self.tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=self.logDir)
    
    optimizer= tf.keras.optimizers.Adam(learning_rate=learning_rate, decay=decay)

    model.compile(optimizer=optimizer,
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])
    
    self.model = model
    
    # Information Log
    print('')
    print("########################################################")
    print("################### Training Section ###################")
    print("########################################################")
    print('')
    print("Model Information:")
    print(f"    Model Choice     : {modelName}")
    print(f"    Experiment Name  : {self.experimentName}")
    print(f"    Log Directory    : {self.logDir}")
    print(f"    Result Directory : {self.resultDir}")
    print(f"    Optimizer        : Adam")
    print(f"      Learning Rate  : {learning_rate}")
    print(f"      Decay          : {decay}")
    print(f"    Loss             : Sparse Categorical Crossentropy")
    print(f"    Metrics          : Accuracy")
    print('')
    
  
  def fit(self, x_train, y_train, epochs, validation_percent, batch_size=128, shuffle=True):
    print("Model Information:")
    print(f"    Epochs        : {epochs}")
    print(f"    x_train shape : {x_train.shape}")
    print(f"    y_train shape : {y_train.shape}")
    print(f"    Validation %  : {validation_percent}")
    print(f"    Batch size    : {batch_size}")
    print(f"    Shuffle       : {shuffle}")

    print('')
    print('Start training...')
    history = self.model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, validation_split=validation_percent, callbacks=[self.tensorboard_callback], shuffle=shuffle)
    self.model.save(self.resultDir)
    
    print('')
    print('Training Completed')
    print(f'    Result Model saved in : {self.resultDir}')
    print(f'    Model Log saved in    : {self.logDir}')
    
    return history
  
  # Baseline Model
  def modelA(self):
    model = tf.keras.Sequential([
      tf.keras.layers.Conv2D(120, (11, 11), strides=(4, 4), activation='relu', input_shape=(256, 256, 1)),
      tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2)),
      tf.keras.layers.Conv2D(256, (5, 5), strides=(1, 1), activation='relu'),
      tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2)),
      tf.keras.layers.Conv2D(384, (3, 3), strides=(1, 1), activation='relu'),
      tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2)),
      tf.keras.layers.Flatten(),
      tf.keras.layers.Dense(2048, activation='relu'),
      tf.keras.layers.Dropout(0.5),
      tf.keras.layers.Dense(2048, activation='relu'),
      tf.keras.layers.Dropout(0.5),
      tf.keras.layers.Dense(self.ySize, activation='softmax')
    ])
    
    return model
  
  # Removed last layer of Conv2D and MaxPooling2D
  def modelB(self):
    model = tf.keras.Sequential([
      tf.keras.layers.Conv2D(120, (11, 11), strides=(4, 4), activation='relu', input_shape=(256, 256, 1)),
      tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2)),
      tf.keras.layers.Conv2D(256, (5, 5), strides=(1, 1), activation='relu'),
      tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2)),
      tf.keras.layers.Flatten(),
      tf.keras.layers.Dense(2048, activation='relu'),
      tf.keras.layers.Dropout(0.5),
      tf.keras.layers.Dense(2048, activation='relu'),
      tf.keras.layers.Dropout(0.5),
      tf.keras.layers.Dense(self.ySize, activation='softmax')
    ])
    
    return model
  
  # More Dropout
  def modelC(self):
    model = tf.keras.Sequential([
      tf.keras.layers.Conv2D(120, (11, 11), strides=(4, 4), activation='relu', input_shape=(256, 256, 1)),
      tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2)),
      tf.keras.layers.Conv2D(256, (5, 5), strides=(1, 1), activation='relu'),
      tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2)),
      tf.keras.layers.Conv2D(384, (3, 3), strides=(1, 1), activation='relu'),
      tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2)),
      tf.keras.layers.Flatten(),
      tf.keras.layers.Dense(2048, activation='relu'),
      tf.keras.layers.Dropout(0.35),
      tf.keras.layers.Dense(2048, activation='relu'),
      tf.keras.layers.Dropout(0.35),
      tf.keras.layers.Dense(self.ySize, activation='softmax')
    ])
    
    return model
  
  # L1 Regularization
  def modelD(self):
    model = tf.keras.Sequential([
      tf.keras.layers.Conv2D(120, (11, 11), strides=(4, 4), activation='relu', input_shape=(256, 256, 1)),
      tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2)),
      tf.keras.layers.Conv2D(256, (5, 5), strides=(1, 1), activation='relu'),
      tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2)),
      tf.keras.layers.Conv2D(384, (3, 3), strides=(1, 1), activation='relu'),
      tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2)),
      tf.keras.layers.Flatten(),
      tf.keras.layers.Dense(2048, activation='relu', kernel_regularizer='l1'),
      tf.keras.layers.Dropout(0.5),
      tf.keras.layers.Dense(2048, activation='relu', kernel_regularizer='l1'),
      tf.keras.layers.Dropout(0.5),
      tf.keras.layers.Dense(self.ySize, activation='softmax')
    ])
    
    return model
  
  # Add 1 Dense and Dropout each
  def modelE(self):
    model = tf.keras.Sequential([
      tf.keras.layers.Conv2D(120, (11, 11), strides=(4, 4), activation='relu', input_shape=(256, 256, 1)),
      tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2)),
      tf.keras.layers.Conv2D(256, (5, 5), strides=(1, 1), activation='relu'),
      tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2)),
      tf.keras.layers.Conv2D(384, (3, 3), strides=(1, 1), activation='relu'),
      tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2)),
      tf.keras.layers.Flatten(),
      tf.keras.layers.Dense(2048, activation='relu'),
      tf.keras.layers.Dropout(0.5),
      tf.keras.layers.Dense(2048, activation='relu'),
      tf.keras.layers.Dropout(0.5),
      tf.keras.layers.Dense(1024, activation='relu'),
      tf.keras.layers.Dropout(0.5),
      tf.keras.layers.Dense(self.ySize, activation='softmax')
    ])
    
    return model

  def summary(self):
    self.model.summary()
    
    