import os
import numpy as np

from pydub import AudioSegment, effects
import librosa
import IPython.display as ipd
from IPython.display import clear_output
import matplotlib.pyplot as plt
import pytz
import cv2

from sklearn.preprocessing import LabelEncoder

import warnings
warnings.filterwarnings('ignore')

tz = pytz.timezone('Asia/Hong_Kong')

class DataModel:
  def __init__(self, labelsToInclude=[], mergeHappinessExcitement=False, splitDuration=8, ignoreDuration=1):
    # Hyperparameter
    self.splitDuration = splitDuration
    self.ignoreDuration = ignoreDuration
    self.dimension = (256, 256)
    self.test_percent = 0.2
    self.validation_percent = 0.2

    if (labelsToInclude == []):
      self.labels_name = ['Neutral', 'Frustration', 'Anger', 'Sadness', 'Happiness', 'Excitement', 'Surprise', 'Disgust', 'Fear']
    else:
      self.labels_name = labelsToInclude
    
    self.mergeHappinessExcitement = mergeHappinessExcitement
    
    self.data = []
    self.labels = []
    self.sampling_rates = []
    self.x_images = []
    self.x_train = None
    self.y_train = None
    self.sr_train = None
    self.x_test = None
    self.y_test = None
    self.sr_test = None
  
  ###############################
  ### Data Processing Methods ###
  ###############################
  def processData(self):
    if (self.data == [] or self.labels == [] or self.sampling_rates == []):
      print('Please call extractIEMOCAPData() and/or extractEmoDBData() before calling this method!')
    else:
      self.melProcessing()
      self.labelProcessing()
      self.dataSplit()
    
      print('Data Processing Completed!')
      print('  Data shapes:')
      print(f'    x_train  : {self.x_train.shape}')
      print(f'    y_train  : {self.y_train.shape}')
      print(f'    sr_train : {self.sr_train.shape}')
      print(f'    x_test   : {self.x_test.shape}')
      print(f'    y_test   : {self.y_test.shape}')
      print(f'    sr_test  : {self.sr_test.shape}')
      print('')
  
  def extractIEMOCAPData(self):
    labels_dict = {'neu': 'Neutral',
          'fru': 'Frustration',
          'ang': 'Anger',
          'sad': 'Sadness',
          'hap': 'Happiness',
          'exc': 'Excitement',
          'sur': 'Surprise',
          'dis': 'Disgust',
          'fea': 'Fear'}
    
    data = []
    labels = []
    sampling_rates = []

    count = 0

    # range 1 to 2 means loading Session 1 only
    # If want to load session 2, change to range 2 to 3
    # If want to load all sessions, change to 1 to 6
    for i in list(range(1, 6)):
      data_path = os.path.join(os.getcwd(), 'Data/IEMOCAP/Sentences/Session' + str(i))
      labels_dir = os.path.join(data_path, 'evaluation/')
      session = 'Session' + str(i)

      for dirname, _, filenames in os.walk(data_path):
        folderName = dirname.split("/")[-1]

        if (folderName != "evaluation" and folderName != "categorical"):
          for filename in filenames:

            if (filename == 'desktop.ini' or filename == 'desktop.in.txt' or filename == '.DS_Store' or filename == '.DS'):
              continue

            # Load Label
            recording_name = filename[:filename.rfind('_')]
            label_path = labels_dir + recording_name + '.txt'

            sentence_name = filename.split('.')[0]

            with open(label_path) as f:
              line = [line.strip() for line in f.readlines() if sentence_name in line]

            if (len(line) == 0):
              continue
            item = line[0].split('\t')
            if (len(item) < 3):
              continue

            label_code = line[0].split('\t')[2]
            if (label_code in labels_dict):
              label = labels_dict[label_code]
            else:
              label = 'Other'
            
            # Merge Labels of Happiness and Excitement if needed
            if (self.mergeHappinessExcitement):
              if (label == "Excitement"):
                label = "Happiness"
            
            # Filter Labels
            if (label not in self.labels_name):
              continue

            # Load Audio and x
            wav_path = os.path.join(dirname, filename)

            # Extract Data
            tempData, tempLabels, tempSamplingRates = self._extractData(wav_path, label)
            
            data.extend(tempData)
            labels.extend(tempLabels)
            sampling_rates.extend(tempSamplingRates)

            count += 1
            if (count % 100 == 0):
              clear_output()
              print('Extracting data...')
              print(f'    Loaded {len(data):4} data')
              
    self.data.extend(data)
    self.labels.extend(labels)
    self.sampling_rates.extend(sampling_rates)

    clear_output()
    label_count = {'Neutral': 0, 'Frustration': 0, 'Anger': 0, 'Sadness': 0, 'Happiness': 0, 'Excitement': 0, 'Surprise': 0, 'Disgust': 0, 'Fear': 0, 'Boredom': 0}
    for label in self.labels:
      label_count[label] += 1
    
    print('Data Extration Completed')
    print('    Number of data:', len(self.data))
    print(f"      Neutral     : {label_count['Neutral']}")
    print(f"      Frustration : {label_count['Frustration']}")
    print(f"      Anger       : {label_count['Anger']}")
    print(f"      Sadness     : {label_count['Sadness']}")
    print(f"      Happiness   : {label_count['Happiness']}")
    print(f"      Excitement  : {label_count['Excitement']}")
    print(f"      Surprise    : {label_count['Surprise']}")
    print(f"      Disgust     : {label_count['Disgust']}")
    print(f"      Fear        : {label_count['Fear']}")
    print(f"      Boredom     : {label_count['Boredom']}")
    
    

    for i in range(len(data)):
      if (len(data[i]) != self.splitDuration * sampling_rates[i]):
        print(f'    Incorrect found {i:4}: Duration = {len(data[i])}')
    
    print('')
   
  def extractEmoDBData(self):
    labels_dict = {'N': 'Neutral',
          'A': 'Frustration',
          'W': 'Anger',
          'T': 'Sadness',
          'F': 'Happiness',
          'E': 'Disgust',
          'L': 'Boredom'}
    
    data = []
    labels = []
    sampling_rates = []
    
    count = 0
    
    data_path = os.path.join(os.getcwd(), 'Data/EmoDB')
    
    for dirname, _, filenames in os.walk(data_path):
      for filename in filenames:
        
        if (filename == 'desktop.ini' or filename == 'desktop.in.txt' or filename == '.DS_Store' or filename == '.DS'):
              continue
        
        # Load Label
        label_code = filename[5]
        label = labels_dict[label_code]
        
        # Filter Labels
        if (label not in self.labels_name):
          continue
        
        # Load Audio and x
        wav_path = os.path.join(dirname, filename)
        
        # Extract Data
        tempData, tempLabels, tempSamplingRates = self._extractData(wav_path, label)
        
        data.extend(tempData)
        labels.extend(tempLabels)
        sampling_rates.extend(tempSamplingRates)

        count += 1
        if (count % 100 == 0):
          clear_output()
          print('Extracting data...')
          print(f'    Loaded {len(data):4} data')
          
    self.data.extend(data)
    self.labels.extend(labels)
    self.sampling_rates.extend(sampling_rates)

    clear_output()
    label_count = {'Neutral': 0, 'Frustration': 0, 'Anger': 0, 'Sadness': 0, 'Happiness': 0, 'Excitement': 0, 'Surprise': 0, 'Disgust': 0, 'Fear': 0, 'Boredom': 0}
    for label in self.labels:
      label_count[label] += 1
    
    print('Data Extration Completed')
    print('    Number of data:', len(self.data))
    print(f"      Neutral     : {label_count['Neutral']}")
    print(f"      Frustration : {label_count['Frustration']}")
    print(f"      Anger       : {label_count['Anger']}")
    print(f"      Sadness     : {label_count['Sadness']}")
    print(f"      Happiness   : {label_count['Happiness']}")
    print(f"      Excitement  : {label_count['Excitement']}")
    print(f"      Surprise    : {label_count['Surprise']}")
    print(f"      Disgust     : {label_count['Disgust']}")
    print(f"      Fear        : {label_count['Fear']}")
    print(f"      Boredom     : {label_count['Boredom']}")
    
    

    for i in range(len(data)):
      if (len(data[i]) != self.splitDuration * sampling_rates[i]):
        print(f'    Incorrect found {i:4}: Duration = {len(data[i])}')
    
    print('')
    
  def _extractData(self, wav_path, label):
    data = []
    labels = []
    sampling_rates = []
    
    audio = AudioSegment.from_file(wav_path)
    sr = audio.frame_rate

    # Process Audio
    audio = effects.normalize(audio, headroom = 5.0) # TODO: Try other head room
    processed_x = np.array(audio.get_array_of_samples(), dtype = 'float32')
    processed_x, _ = librosa.effects.trim(processed_x, top_db = 30)
    
    ### Noise reduction is SUPER SLOW
    # processed_x = nr.reduce_noise(processed_x, sr=sr)
    
    # Split at or add padding to splitDuration (hyperparameter)
    #   if remaining duration is less than 1 sec, remove
    duration = len(processed_x) / sr
    size = sr * self.splitDuration

    if (duration < self.splitDuration):
      processed_x = np.pad(processed_x, (0, size - len(processed_x)), 'constant')
      
      data.append(processed_x)
      labels.append(label)
      sampling_rates.append(sr)
    elif (duration > self.splitDuration):

      for j in range(0, len(processed_x), size):
        splitSection = processed_x[j:j+size]

        # Check if it is longer than ignoreDuration
        if (len(splitSection) > self.ignoreDuration * sr):

          # Pad audio that is shorter than splitDuration
          if (len(splitSection) < size):
            padded_x = np.pad(splitSection, (0, size - len(splitSection)), 'constant')
            
            data.append(padded_x)
            labels.append(label)
            sampling_rates.append(sr)
          else:
            data.append(splitSection)
            labels.append(label)
            sampling_rates.append(sr)
    
    return data, labels, sampling_rates
    
  def melProcessing(self):
    print('Processing data to Mel Spectrogram...')
    
    x_images = []

    for i, x in enumerate(self.data):
      # Extract Mel-Sectrogram
      mel_spec = librosa.feature.melspectrogram(y=x, sr=self.sampling_rates[i])
      mel_spec = librosa.amplitude_to_db(mel_spec, ref=np.min)

      # Resize Mel-Spectrogram
      mel_spec = cv2.resize(mel_spec, self.dimension, interpolation=cv2.INTER_CUBIC)

      x_images.append(mel_spec)

    x_images = [ x for x in x_images ]
    x_images = np.asarray(x_images)
    x_images = x_images.reshape(x_images.shape[0], x_images.shape[1], x_images.shape[2], 1)
    self.x_images = x_images

    print('Mel Spectrogram Processing Completed')
    print('    Shape of images:', self.x_images.shape)
    print('')
  
  def labelProcessing(self):
    print('Processing labels...')
    
    # Label Encoding
    encoder = LabelEncoder()
    encoder.fit(self.labels_name)
    self.labels = encoder.transform(self.labels)
    
    print('Label Processing Completed')
    print('')
 
  def dataSplit(self):
    print('Splitting data...')
    
    test_size = np.floor(len(self.x_images) * self.test_percent).astype(int)
    training_size = len(self.x_images) - test_size

    # Take training data and shuffle
    x_train = self.x_images[:training_size]
    y_train = self.labels[:training_size]
    sr_train = self.sampling_rates[:training_size]

    train = list(zip(x_train, y_train, sr_train))
    np.random.seed(0)
    np.random.shuffle(train)
    
    x_train, y_train, sr_train = zip(*train)
    self.x_train = np.asarray(x_train)
    self.y_train = np.asarray(y_train)
    self.sr_train = np.asarray(sr_train)

    # Take test data
    self.x_test = np.asarray(self.x_images[training_size:])
    self.y_test = np.asarray(self.labels[training_size:])
    self.sr_test = np.asarray(self.sampling_rates[training_size:])

    print('Data Split Completed')
    print('')

  #############################
  ### Visualization Methods ###
  #############################
  def plotAudio(self, x, sr, title):
    plt.figure(figsize=(12,1))
    librosa.display.waveplot(x, sr)
    plt.title(title)

  def playAudio(self, x, sr):
    ipd.display(ipd.Audio(data = x, rate=sr))

  def visualizeMelSpec(self, mel_spectrogram, sr):
    librosa.display.specshow(mel_spectrogram, sr=sr, x_axis='time', y_axis='mel')
    plt.colorbar(format='%+2.0f dB')
  