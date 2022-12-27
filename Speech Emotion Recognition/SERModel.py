import os
import pytz
import tensorflow as tf
import tensorboard
from tensorflow.keras.layers import TimeDistributed
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

tz = pytz.timezone('Asia/Hong_Kong')

# ( (D + 2 * padding - K) / stride ) + 1

class SERModel:
  def __init__(self, modelName, experimentName, ySize=9, learning_rate=0.0001, decay=0.001):
    self.experimentName = datetime.now(tz=tz).strftime("%m-%d %Hh%Mm%Ss ") + experimentName

    self.logDir = os.path.join(os.getcwd(), "IEMOCAP_ModelLog", self.experimentName)
    self.resultDir = os.path.join(os.getcwd(), "IEMOCAP_TrainedModel", self.experimentName)
    
    self.ySize = ySize
    
    if (modelName.upper() == "cnnModelA".upper()):
      model = self.cnnModelA()
    elif (modelName.upper() == "cnnModelB".upper()):
      model = self.cnnModelB()
    elif (modelName.upper() == "cnnModelC".upper()):
      model = self.cnnModelC()
    elif (modelName.upper() == "cnnModelD".upper()):
      model = self.cnnModelD()
    elif (modelName.upper() == "cnnModelE".upper()):
      model = self.cnnModelE()
    elif (modelName.upper() == "cnnLstmModelA".upper()):
      model = self.cnnLstmModelA()
    elif (modelName.upper() == "cnnLstmModelB".upper()):
      model = self.cnnLstmModelB()
    elif (modelName.upper() == "cnnLstmModelC".upper()):
      model = self.cnnLstmModelC()
    elif (modelName.upper() == "cnnLstmModelD".upper()):
      model = self.cnnLstmModelD()
    else:
      model = None
      raise NameError("modelName does not exist. Should be cnnModel{A-E} or cnnLstmModel{A-D}")
    
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
  
  ###################################################################################################################
  #################################################### CNN Model ####################################################
  ###################################################################################################################
  
  # Baseline Model
  def cnnModelA(self):
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
  def cnnModelB(self):
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
  def cnnModelC(self):
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
  def cnnModelD(self):
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
  def cnnModelE(self):
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
  

  ####################################################################################################################
  ################################################## CNN LSTM Model ##################################################
  ####################################################################################################################
  
#   CNN LSTM Baseline from Article
#   def modelF(self):
#     model = tf.keras.Sequential([
#       tf.keras.layers.Conv2D(64, (3, 3), strides=(1, 1), activation='relu', input_shape=(256, 256, 1)), # 254, 254, 64
#       tf.keras.layers.BatchNormalization(axis=-1),
#       tf.keras.layers.MaxPooling2D((2, 2), strides=(2, 2)),                                             # 127, 127, 64
#       tf.keras.layers.Conv2D(64, (3, 3), strides=(1, 1), activation='relu'),                            # 125, 125, 64
#       tf.keras.layers.BatchNormalization(axis=-1),
#       tf.keras.layers.MaxPooling2D((4, 4), strides=(4, 4)),                                             # 31, 31, 64
#       tf.keras.layers.Conv2D(128, (3, 3), strides=(1, 1), activation='relu'),                           # 29, 29, 128
#       tf.keras.layers.BatchNormalization(axis=-1),
#       tf.keras.layers.MaxPooling2D((4, 4), strides=(4, 4)),                                             # 7, 7, 128
#       tf.keras.layers.Conv2D(128, (3, 3), strides=(1, 1), activation='relu'),                           # 5, 5, 128
#       tf.keras.layers.BatchNormalization(axis=-1),
#       tf.keras.layers.MaxPooling2D((4, 4), strides=(4, 4)),                                             # 1, 1, 128
#       tf.keras.layers.Reshape((1, 128)),
#       tf.keras.layers.LSTM(256, activation="tanh", return_sequences=True),
#       tf.keras.layers.Dense(self.ySize, activation='softmax')
#     ])
    
#     return model

  # CNN LSTM Baseline (From CNN Model A with BN in middle and Extra Conv2D at the end to reduce it to size of (1x1))
  def cnnLstmModelA(self):
    model = tf.keras.Sequential([
      tf.keras.layers.Conv2D(120, (11, 11), strides=(4, 4), activation='relu', input_shape=(256, 256, 1)), # 62, 62, 120
      tf.keras.layers.BatchNormalization(axis=-1),
      tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2)),                                                # 30, 30, 120
      tf.keras.layers.Conv2D(256, (5, 5), strides=(1, 1), activation='relu'),                              # 26, 26, 256
      tf.keras.layers.BatchNormalization(axis=-1),
      tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2)),                                                # 12, 12, 256
      tf.keras.layers.Conv2D(384, (3, 3), strides=(1, 1), activation='relu'),                              # 10, 10, 384
      tf.keras.layers.BatchNormalization(axis=-1),
      tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2)),                                                #  4,  4, 384
      tf.keras.layers.Conv2D(512, (4, 4), strides=(1, 1), activation='relu'),                              #  1,  1, 512
      tf.keras.layers.BatchNormalization(axis=-1),
      tf.keras.layers.Reshape((1, 512)),                                                                   #      1, 512
      tf.keras.layers.LSTM(256, activation="tanh", return_sequences=True),                                 #      1, 256
      tf.keras.layers.Dense(self.ySize, activation='softmax')                                              #      1, ySize
    ])
    
    return model

  # CNN LSTM Baseline 2 (From CNN Model A with BN in middle and extra LSTM)
  def cnnLstmModelB(self):
    model = tf.keras.Sequential([
      tf.keras.layers.Conv2D(120, (11, 11), strides=(4, 4), activation='relu', input_shape=(256, 256, 1)), # 62, 62, 120
      tf.keras.layers.BatchNormalization(axis=-1),
      tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2)),                                                # 30, 30, 120
      tf.keras.layers.Conv2D(256, (5, 5), strides=(1, 1), activation='relu'),                              # 26, 26, 256
      tf.keras.layers.BatchNormalization(axis=-1),
      tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2)),                                                # 12, 12, 256
      tf.keras.layers.Conv2D(384, (3, 3), strides=(1, 1), activation='relu'),                              # 10, 10, 384
      tf.keras.layers.BatchNormalization(axis=-1),
      tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2)),                                                #  4,  4, 384
      tf.keras.layers.Reshape((1, 6144)),                                                                  #      1, 6144
      tf.keras.layers.LSTM(1024, activation="tanh", return_sequences=True),                                #      1, 1024
      tf.keras.layers.LSTM(256),                                                                           #      1, 256
      tf.keras.layers.Dense(self.ySize, activation='softmax')                                              #      1, ySize
    ])
    
    return model

  # CNN LSTM Baseline 3 (From CNN Model A with BN in middle and extra LSTM and Dense)
  def cnnLstmModelC(self):
    model = tf.keras.Sequential([
      tf.keras.layers.Conv2D(120, (11, 11), strides=(4, 4), activation='relu', input_shape=(256, 256, 1)), # 62, 62, 120
      tf.keras.layers.BatchNormalization(axis=-1),
      tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2)),                                                # 30, 30, 120
      tf.keras.layers.Conv2D(256, (5, 5), strides=(1, 1), activation='relu'),                              # 26, 26, 256
      tf.keras.layers.BatchNormalization(axis=-1),
      tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2)),                                                # 12, 12, 256
      tf.keras.layers.Conv2D(384, (3, 3), strides=(1, 1), activation='relu'),                              # 10, 10, 384
      tf.keras.layers.BatchNormalization(axis=-1),
      tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2)),                                                #  4,  4, 384
      tf.keras.layers.Reshape((1, 6144)),                                                                  #      1, 6144
      tf.keras.layers.LSTM(2048, activation="tanh", return_sequences=True),                                #      1, 2048
      tf.keras.layers.LSTM(1024),                                                                          #      1, 1024
      tf.keras.layers.Dense(512, activation='relu'),                                                       #      1, 512
      tf.keras.layers.Dense(256, activation='relu'),                                                       #      1, 256
      tf.keras.layers.Dense(self.ySize, activation='softmax')                                              #      1, ySize
    ])
    
    return model

  #  Add Time Distributed
  def cnnLstmModelD(self):
    model = tf.keras.Sequential([
      TimeDistributed(tf.keras.layers.Conv2D(120, (11, 11), strides=(4, 4), activation='relu'), input_shape=(1, 256, 256, 1)), # 62, 62, 120
      TimeDistributed(tf.keras.layers.BatchNormalization(axis=-1)),
      TimeDistributed(tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2))),                        # 30, 30, 120
      TimeDistributed(tf.keras.layers.Conv2D(256, (5, 5), strides=(1, 1), activation='relu')),      # 26, 26, 256
      TimeDistributed(tf.keras.layers.BatchNormalization(axis=-1)),
      TimeDistributed(tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2))),                        # 12, 12, 256
      TimeDistributed(tf.keras.layers.Conv2D(384, (3, 3), strides=(1, 1), activation='relu')),      # 10, 10, 384
      TimeDistributed(tf.keras.layers.BatchNormalization(axis=-1)),
      TimeDistributed(tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2))),                        #  4,  4, 384
      TimeDistributed(tf.keras.layers.Flatten()),                                                   #      1, 6144
      # tf.keras.layers.Reshape((6144, 1)),                                          #      1, 6144
      tf.keras.layers.LSTM(1024, activation="tanh", return_sequences=False, input_shape=(1, 6144)),  #      1, 2048
      tf.keras.layers.LSTM(256),                                                                    #      1, 256
      # tf.keras.layers.Dense(256, activation='relu'),                                                       #      1, 256
      tf.keras.layers.Dense(self.ySize, activation='softmax')                                       #      1, ySize
    ])
    
    return model


  def summary(self, input_shape=()):
    if (input_shape != ()):
      self.model.build(input_shape)
    self.model.summary()
    
# ( (D + 2 * padding - K) / stride ) + 1
