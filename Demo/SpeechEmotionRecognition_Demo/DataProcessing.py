import os
import numpy as np
import tensorflow as tf
from pydub import AudioSegment, effects
import librosa
import noisereduce as nr

class DataProcessing:
  def __init__(self, labelsToInclude=[], splitDuration=8, ignoreDuration=1):
    # Hyperparameter
    self.splitDuration = splitDuration
    self.ignoreDuration = ignoreDuration
    self.dimension = (256, 256)

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
    