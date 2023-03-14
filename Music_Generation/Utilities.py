import numpy as np
from visual_midi import Plotter, Preset
from pretty_midi import PrettyMIDI
from IPython import display

from MEC import MEC_predict, get_MIDI_features

# def play_audio(pm: PrettyMIDI, seconds=30):
#   waveform = pm.fluidsynth(fs=_SAMPLING_RATE)
#   # Take a sample of the generated waveform to mitigate kernel resets
#   waveform_short = waveform[:seconds*_SAMPLING_RATE]
#   return display.Audio(waveform_short, rate=_SAMPLING_RATE)

def play_audio(pm: PrettyMIDI, seconds=30, sampling_rate=16000):
  waveform = pm.fluidsynth(fs=sampling_rate)
  # Take a sample of the generated waveform to mitigate kernel resets
  waveform_short = waveform[:seconds * sampling_rate]
  return display.Audio(waveform_short, rate=sampling_rate)

def midi_show_notebook(pm: PrettyMIDI):
  preset = Preset(plot_width=850)
  plotter = Plotter(preset, plot_max_length_bar=4)
  plotter.show_notebook(pm)

def classify_midi(midi_path: str, model_path: str, emotion_class: list()=['Happiness', 'Angry', 'Sadness', 'Calmness']):

  # Get emotion
  ys_pred = MEC_predict(model_path, midi_path, 0)
  ys_class = np.argmax(ys_pred)
  emotion = emotion_class[ys_class]

  # Get features
  features = get_MIDI_features(midi_path, 0)

  print(f"Emotion : {emotion}")
  print(f"    Happiness : {ys_pred[0][0]:.4f}")
  print(f"    Angry     : {ys_pred[0][1]:.4f}")
  print(f"    Sadness   : {ys_pred[0][2]:.4f}")
  print(f"    Calmness  : {ys_pred[0][3]:.4f}")

  print('')

  print(f"Average:")
  print(f"    Note Density  : {features['note_density_avg']}")
  print(f"    Note Length   : {features['note_length_avg']}")
  print(f"    Note Velocity : {features['note_velocity_avg']}")
  print(f"    Pitch         : {features['pitch_avg']}")
  print("")
  print(f"Standard Deviation:")
  print(f"    Note Density  : {features['note_density_sd']}")
  print(f"    Note Length   : {features['note_length_sd']}")
  print(f"    Note Velocity : {features['note_velocity_sd']}")
  print(f"    Pitch         : {features['pitch_sd']}")
  print("")
  print(f"Scale              : {features['scale']}")
  print(f"Major Minor        : {features['major_minor']}")
  print(f"80% Pitch Range    : {features['80%_pitch_range']}")
  print(f"Polyphony          : {features['polyphony']}")
  print(f"Pitch Entropy      : {features['pitch_entropy']}")
  print(f"Groove Consistency : {features['groove_consistency']}")
  print("")


  play_audio(midi_path, seconds=120)

  # Happiness Angry Sadness Calmness

  """
  Note Density: How many notes in one beat
  Note Length: How long is one note (in beat unit)
  Note Velocity: Volume [0, 127]
  Pitch: [0, 127]

  https://computermusicresource.com/midikeys.html
  Scale: [0, 12) -> C, C#, D, D#, E, F, F#, G, G#, A, A#, B
  Major: Minor = 0, Major = 1
  80% Pitch Range: Middle 80% pitch range
  Polyphony: Average Number of pitch per second (1.0 = Mono)
  Pitch Entropy: IGNORE
  Groove Consistency: Groove consistence or not (hamming distance)
  """
