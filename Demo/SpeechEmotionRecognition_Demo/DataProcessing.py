import os
import numpy as np
import tensorflow as tf
from pydub import AudioSegment, effects
import librosa
import noisereduce as nr
import cv2

class DataProcessing:
  def __init__(self, labelsToInclude=[], splitDuration=8, ignoreDuration=1):
    # Hyperparameter
    self.splitDuration = splitDuration
    self.ignoreDuration = ignoreDuration
    self.dimension = (256, 256)
    self.x_test = []
    self.sr = []

    if (labelsToInclude == []):
      self.labels_name = ['Neutral', 'Frustration', 'Anger', 'Sadness', 'Happiness', 'Excitement', 'Surprise', 'Disgust', 'Fear']
    else:
      self.labels_name = labelsToInclude
      
  def loadAndExtractTestData(self):
    audio_list = []
    
    data_path = os.path.join(os.getcwd(), 'demoData')
    
    for dirname, _, filenames in os.walk(data_path):
      for filename in filenames:
        
        if (filename == 'desktop.ini' or filename == 'desktop.in.txt' or filename == '.DS_Store' or filename == '.DS'):
          continue
        
        # Load Audio and x
        wav_path = os.path.join(dirname, filename)
        audio = AudioSegment.from_file(wav_path)
        
        audio_list.append(audio)
    
    self.extractTestData(audio_list)
  
  def extractTestData(self, audio_list):
    # Process Audio
    for audio in audio_list:
      sr = audio.frame_rate
      
      audio = effects.normalize(audio, headroom = 5.0) # TODO: Try other head room
      processed_x = np.array(audio.get_array_of_samples(), dtype = 'float32')
      processed_x, _ = librosa.effects.trim(processed_x, top_db = 30)
      processed_x = nr.reduce_noise(processed_x, sr=sr)
      self.x_test.append(processed_x)
      self.sr.append(sr)
  
  def processData(self):
    self.melProcessing()
  
  def melProcessing(self):
    # Splitting and Padding Data
    # Split at or add padding to splitDuration (hyperparameter)
    #   if remaining duration is less than 1 sec, remove
    x_test = []
    sampling_rates = []
    
    for index, processed_x in enumerate(self.x_test):
      sr = self.sr[index]
      
      duration = len(processed_x) / sr
      size = sr * self.splitDuration

      if (duration < self.splitDuration):
        processed_x = np.pad(processed_x, (0, size - len(processed_x)), 'constant')
        
        x_test.append(processed_x)
        sampling_rates.append(sr)
      elif (duration > self.splitDuration):

        for j in range(0, len(processed_x), size):
          splitSection = processed_x[j:j+size]

          # Check if it is longer than ignoreDuration
          if (len(splitSection) > self.ignoreDuration * sr):

            # Pad audio that is shorter than splitDuration
            if (len(splitSection) < size):
              padded_x = np.pad(splitSection, (0, size - len(splitSection)), 'constant')
              
              x_test.append(padded_x)
              sampling_rates.append(sr)
            else:
              x_test.append(splitSection)
              sampling_rates.append(sr)
    
    # Convert to Mel-Spectrogram
    x_images = []

    for i, x in enumerate(x_test):
      # Extract Mel-Sectrogram
      mel_spec = librosa.feature.melspectrogram(y=x, sr=sampling_rates[i])
      mel_spec = librosa.amplitude_to_db(mel_spec, ref=np.min)

      # Resize Mel-Spectrogram
      mel_spec = cv2.resize(mel_spec, self.dimension, interpolation=cv2.INTER_CUBIC)

      x_images.append(mel_spec)

    x_images = [ x for x in x_images ]
    x_images = np.asarray(x_images)
    x_images = x_images.reshape(x_images.shape[0], x_images.shape[1], x_images.shape[2], 1)
    self.x_test = x_images
    self.sr = sampling_rates
  
  
    