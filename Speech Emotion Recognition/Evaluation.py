import os
import numpy as np
import matplotlib.pyplot as plt
import pytz
import seaborn as sns

import tensorflow as tf
from tensorflow.core.util import event_pb2
import tensorboard
from sklearn import metrics

import warnings
warnings.filterwarnings('ignore')

tz = pytz.timezone('Asia/Hong_Kong')

class Evaluation:
  def __init__(self, data, resultDir, logDir, model=None):
    if (model == None):
      print(f'Load model from {resultDir}')
      model = tf.keras.models.load_model(resultDir)
      print('')
    
    self.x_test = data.x_test
    self.y_test = data.y_test
    self.labels_name = data.labels_name
    self.resultDir = resultDir
    self.logDir = logDir
    
    print('Start prediction...')
    self.y_pred = np.argmax(model.predict(self.x_test), axis=1)
    
    print('')
    print('Prediction Completed')
    print(f'    Number of results: {len(self.y_pred)}')
    
  def evaluateAll(self, trainName, validName):
    self.showAccuracyAndLoss(trainName, validName)
    self.classificationReport()
    self.confusionMatrix()
  
  def evaluateAllHistory(self, history):
    self.showAccuracyAndLossHistory(history)
    self.classificationReport()
    self.confusionMatrix()

  def showAccuracyAndLoss(self, trainName, validName, accuracyTitle="", lossTitle="", start=0, titleFontSize=18):
    event_training = os.path.join(self.logDir, 'train', trainName)
    event_validation = os.path.join(self.logDir, 'validation', validName)
    
    if (accuracyTitle == ""):
      accuracyTitle = "Accuracy " + self.logDir.split('/')[-1]
    
    if (lossTitle == ""):
      lossTitle = "Loss " + self.logDir.split('/')[-1]

    training_accuracy = []
    training_loss = []
    validation_accuracy = []
    validation_loss = []
    epoch = []

    serialized_examples = tf.data.TFRecordDataset(event_training)
    for serialized_example in serialized_examples:
        event = event_pb2.Event.FromString(serialized_example.numpy())
        for value in event.summary.value:
            t = tf.make_ndarray(value.tensor)
            if (value.tag == 'epoch_accuracy'):
              training_accuracy.append(np.float32(t))
              epoch.append(event.step)
            elif (value.tag == 'epoch_loss'):
              training_loss.append(np.float32(t))



    serialized_examples = tf.data.TFRecordDataset(event_validation)
    for serialized_example in serialized_examples:
        event = event_pb2.Event.FromString(serialized_example.numpy())
        for value in event.summary.value:
            t = tf.make_ndarray(value.tensor)
            if (value.tag == 'epoch_accuracy'):
              validation_accuracy.append(np.float32(t))
            elif (value.tag == 'epoch_loss'):
              validation_loss.append(np.float32(t))


    plt.plot(epoch[start:], training_accuracy[start:], label = "Training")
    plt.plot(epoch[start:], validation_accuracy[start:], label = "Validation")
    plt.title(accuracyTitle, fontsize=titleFontSize)
    plt.xlabel('epochs', fontsize=14)
    plt.ylabel('accuracy', fontsize=14)
    plt.xticks(rotation=0, fontsize=12)
    plt.yticks(rotation=0, fontsize=12)
    plt.legend()
    plt.show()

    plt.plot(epoch[start:], training_loss[start:], label = "Training")
    plt.plot(epoch[start:], validation_loss[start:], label = "Validation")
    plt.title(lossTitle, fontsize=titleFontSize)
    plt.xlabel('epochs', fontsize=14)
    plt.ylabel('loss', fontsize=14)
    plt.xticks(rotation=0, fontsize=12)
    plt.yticks(rotation=0, fontsize=12)
    plt.legend()
    plt.show()

  def showAccuracyAndLossHistory(self, history, accuracyTitle="", lossTitle="", start=0, titleFontSize=18):
    if (accuracyTitle == ""):
      accuracyTitle = "Accuracy " + self.logDir.split('/')[-1]
    
    if (lossTitle == ""):
      lossTitle = "Loss " + self.logDir.split('/')[-1]
      
    epochRange = list(range(len(history.history['accuracy'])))[start:]
    
    plt.plot(epochRange, history.history['accuracy'][start:], label = "Training")
    plt.plot(epochRange, history.history['val_accuracy'][start:], label = "Validation")
    plt.title(accuracyTitle, fontsize=titleFontSize)
    plt.xlabel('epochs', fontsize=14)
    plt.ylabel('accuracy', fontsize=14)
    plt.xticks(rotation=0, fontsize=12)
    plt.yticks(rotation=0, fontsize=12)
    plt.legend()
    plt.show()

    plt.plot(epochRange, history.history['loss'][start:], label = "Training")
    plt.plot(epochRange, history.history['val_loss'][start:], label = "Validation")
    plt.title(lossTitle, fontsize=titleFontSize)
    plt.xlabel('epochs', fontsize=14)
    plt.ylabel('loss', fontsize=14)
    plt.xticks(rotation=0, fontsize=12)
    plt.yticks(rotation=0, fontsize=12)
    plt.legend()
    plt.show()

  def confusionMatrix(self, title="", titleFontSize=15):
    if (title == ""):
      title = "Confusion Matrix " + self.logDir.split('/')[-1]
    
    confusion_matrix = metrics.confusion_matrix(self.y_test, self.y_pred)
    confusion_matrix_percent = confusion_matrix.astype('float') / confusion_matrix.sum(axis=1)[:, np.newaxis]
    
    fig, ax = plt.subplots(figsize=(10,8))
    sns.heatmap(confusion_matrix_percent, annot=True, fmt='.2f', xticklabels=self.labels_name, yticklabels=self.labels_name, cmap="viridis")
    plt.title(title, fontsize=titleFontSize)
    plt.xticks(rotation=40, fontsize=13)
    plt.yticks(rotation=0, fontsize=13)
    plt.xlabel('Predicted', fontsize=13)
    plt.ylabel('True', fontsize=13)
    plt.show(block=False)


    # cm_display = metrics.ConfusionMatrixDisplay(confusion_matrix = confusion_matrix, display_labels=self.labels_name)

    # cm_display.plot()
    # plt.title(title, fontsize=titleFontSize)
    # plt.xticks(rotation=40)
    # plt.xlabel('Predicted')
    # plt.ylabel('True')
    # plt.show()
  
  def classificationReport(self):
    report = metrics.classification_report(self.y_test, self.y_pred)
    print(report)
  