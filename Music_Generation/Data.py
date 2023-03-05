import os
import json
import copy
import glob
import timeit
import random
import shutil
import tables  # For opening the .h5 dataset
import requests
import matplotlib.pyplot as plt
from collections import Counter
from itertools import cycle
from multiprocessing import Manager
from multiprocessing import Pool
from typing import Optional, List, Dict
from bokeh.colors.groups import purple as colors
from pretty_midi import PrettyMIDI, program_to_instrument_class, Instrument
from magenta.pipelines import pipeline

from AtomicCounter import AtomicCounter


class Data:

  DATASET_DIR: str
  H5_MATCHED_DIR: str
  MIDI_DIR: str
  MATCH_SCORES_FILEPATH: str
  GENRE_LIST: List[str] = None  # NOTE: None means all genres
  SAMPLE_SIZE: int = None  # NOTE: None means all MIDI

  ALL_MIDI_PATHS = None
  MSD_SCORE: Dict
  LAST_FM_API_KEY: str = "aefb8c01606bdd01e4b3a246722ff119"


  def __init__(self,
               dataset_dir: str,
               h5_matched_dir: str,
               midi_dir: str,
               match_scores_filepath: str,
               genre_list: List[str] = None,
               sample_size: int = None
               ):
    self.MIDI_DIR = midi_dir

    # Check if dataset directory exists
    if (os.path.isdir(dataset_dir)):
      self.DATASET_DIR = dataset_dir
    else:
      raise OSError(f"Dataset directory not found at {dataset_dir}")

    # Check if h5_matched directory exists
    if (os.path.isdir(h5_matched_dir)):
      self.H5_MATCHED_DIR = h5_matched_dir
    else:
      raise OSError(f"H5_matched directory not found at {h5_matched_dir}")
    
    # Check if path of match score file is correct
    if (os.path.isfile(match_scores_filepath)):
      self.MATCH_SCORES_FILEPATH = match_scores_filepath
      self.MSD_SCORE = self.get_msd_score_matches(match_scores_filepath)
    else:
      raise OSError(f"Match Scores file not found at {match_scores_filepath}")
    
    # Create a midi_dir if not exists and clean the directory
    shutil.rmtree(self.MIDI_DIR, ignore_errors=True) 
    os.makedirs(self.MIDI_DIR, exist_ok=True)

    # Get all the midi paths
    self.MIDI_PATHS = glob.glob(os.path.join(self.DATASET_DIR, "**", "*.mid"), recursive=True)

    self.GENRE_LIST = genre_list
    self.SAMPLE_SIZE = sample_size


  def get_genres(self, h5) -> Optional[List]:
    title = h5.root.metadata.songs.cols.title[0].decode("utf-8")
    artist = h5.root.metadata.songs.cols.artist_name[0].decode("utf-8")
    request = (f"https://ws.audioscrobbler.com/2.0/"
              f"?method=track.gettoptags"
              f"&artist={artist}"
              f"&track={title}"
              f"&api_key={self.LAST_FM_API_KEY}"
              f"&format=json")
    response = requests.get(request, timeout=10)
    json = response.json()

    if "error" in json:
      raise Exception(f"Error in request for '{artist}' - '{title}': "
                      f"'{json['message']}'")
    if "toptags" not in json:
      raise Exception(f"Error in request for '{artist}' - '{title}': "
                      f"no top tags")
    
    tags = [tag["name"] for tag in json["toptags"]["tag"]]
    tags = [tag.lower().strip() for tag in tags if tag]

    return tags
  
  def get_instrument(self, msd_id) -> Optional[list]:
    midi_md5 = self.get_matched_midi_md5(msd_id, self.MSD_SCORE)
    midi_path = self.get_midi_path(msd_id, midi_md5, self.DATASET_DIR)
    pm = PrettyMIDI(midi_path)

    # For all instruments that are not drums
    instruments = [program_to_instrument_class(instrument.program) for instrument in pm.instruments if not instrument.is_drum]

    # For all drums
    drums = ["Drums" for instrument in pm.instruments if instrument.is_drum]

    instruments = instruments + drums

    if not instruments:
      raise Exception(f"No program classes for {msd_id}: "
                      f"{len(instruments)}")
    return instruments

  def extract_drums(self, msd_id: str) -> Optional[PrettyMIDI]:
    # Create and empty drums directory inside the midi directory
    DRUMS_DIRECTORY = os.path.join(self.MIDI_DIR, "drums")
    os.makedirs(DRUMS_DIRECTORY, exist_ok=True)

    midi_md5 = self.get_matched_midi_md5(msd_id, self.MSD_SCORE)
    midi_path = self.get_midi_path(msd_id, midi_md5, self.DATASET_DIR)
    pm = PrettyMIDI(midi_path)

    # Copy it because we want to keep the time singatures and tempo changes from the original file
    pm_drums = copy.deepcopy(pm)
    pm_drums.instruments = [instrument for instrument in pm_drums.instruments if instrument.is_drum]

    if (len(pm_drums.instruments) > 1):
      drums = Instrument(program=0, is_drum=True)

      # If there are multiple instruments, we merged them together to one instrument
      for instrument in pm_drums.instruments:
        for note in instrument.notes:
          drums.notes.append(note)
      pm_drums.instruments = [drums]

    if (len(pm_drums.instruments) != 1):
      raise Exception(f"Invalid number of drums {midi_path}: {len(pm_drums.instruments)}")
    
    # Store in corresponding directory
    pm_drums.write(os.path.join(DRUMS_DIRECTORY, f"{msd_id}.mid"))

    return pm_drums
  
  def extract_pianos(self, msd_id: str) -> List[PrettyMIDI]:
    PIANO_PROGRAMS = list(range(0, 8))
    INSTRUMENTS_TYPE = "pianos"
    return self.extract_instrument(msd_id, PIANO_PROGRAMS, INSTRUMENTS_TYPE)

  def extract_instrument(self, msd_id: str, instruments_list: list, instruments_type: str) -> List[PrettyMIDI]:
    # General MIDI Level 1 (Link: https://www.midi.org/specifications-old/item/gm-level-1-sound-set)
    #   1 -   8 -> Piano
    #   9 -  16 -> Chromatic Percussion
    #  17 -  24 -> Organ
    #  25 -  32 -> Guitar
    #  33 -  40 -> Bass
    #  41 -  48 -> Strings
    #  49 -  56 -> Esemble
    #  57 -  64 -> Brass
    #  65 -  72 -> Reed
    #  73 -  80 -> Pipe
    #  81 -  88 -> Synth Lead
    #  89 -  96 -> Synth Pad
    #  97 - 104 -> Synth Effects
    # 105 - 112 -> Ethnic
    # 113 - 120 -> Percussive
    # 121 - 128 -> Sound Effects


    # Create and empty instrument directory inside the midi directory
    INSTRUMENT_DIRECTORY = os.path.join(self.MIDI_DIR, instruments_type)
    os.makedirs(INSTRUMENT_DIRECTORY, exist_ok=True)

    midi_md5 = self.get_matched_midi_md5(msd_id, self.MSD_SCORE)
    midi_path = self.get_midi_path(msd_id, midi_md5, self.DATASET_DIR)
    pm = PrettyMIDI(midi_path)
    pm.instruments = [instrument for instrument in pm.instruments
                      if instrument.program in instruments_list and not instrument.is_drum]
    pm_pianos = []

    # Concatenate all the instrument programs into 1 instrument
    if len(pm.instruments) > 1:
      for instrument in pm.instruments:
        pm_piano = copy.deepcopy(pm)
        pm_piano_instrument = Instrument(program=instrument.program)
        pm_piano.instruments = [pm_piano_instrument]
        for note in instrument.notes:
          pm_piano_instrument.notes.append(note)
        pm_pianos.append(pm_piano)
    else:
      pm_pianos.append(pm)
    
    # Check for invalid instruments
    for index, pm_piano in enumerate(pm_pianos):
      if len(pm_piano.instruments) != 1:
        raise Exception(f"Invalid number of instruments {msd_id}: "
                        f"{len(pm_piano.instruments)}")
      if pm_piano.get_end_time() > 1000:
        raise Exception(f"Instrument track too long {msd_id}: "
                        f"{pm_piano.get_end_time()}")
    
    # Store in corresponding directory
    for index, pm_piano in enumerate(pm_pianos):
      pm_piano.write(os.path.join(INSTRUMENT_DIRECTORY, f"{msd_id}_{index}.mid"))

    return pm_pianos



  # Get higher score match from MSD_ID
  def get_matched_midi_md5(self, msd_id: str, msd_score_matches: dict):
    max_score = 0

    for midi_md5, score in msd_score_matches[msd_id].items():
      if (score > max_score):
        max_score = score
        matched_midi_md5 = midi_md5
    
    if not matched_midi_md5:
      raise Exception(f"Not matched {msd_id}: {msd_score_matches[msd_id]}")

    return matched_midi_md5

  # Given MSD ID, return path to corresponding h5
  def msd_id_to_h5(self, msd_id: str, dataset_path: str) -> str:
    return os.path.join(dataset_path, self.msd_id_to_dirs(msd_id) + ".h5")

  # Given MSD ID and MIDI MD5, return path to MIDI file
  def get_midi_path(self, msd_id: str, midi_md5: str, dataset_path: str) -> str:
    return os.path.join(dataset_path, self.msd_id_to_dirs(msd_id), midi_md5 + ".mid")

  # Given MSD ID, get path prefix
  def msd_id_to_dirs(self, msd_id: str) -> str:
    return os.path.join(msd_id[2], msd_id[3], msd_id[4], msd_id)

  # Returns the dictionary of scores from the match scores file
  def get_msd_score_matches(self, match_scores_path: str) -> Dict:
    with open(match_scores_path) as f:
      return json.load(f)
    

  
  def process(self, msd_id: str, counter: AtomicCounter = None) -> Optional[dict]:
    try:
      with tables.open_file(self.msd_id_to_h5(msd_id, self.H5_MATCHED_DIR)) as h5:
        # Extract artist
        artist = h5.root.metadata.songs.cols.artist_name[0].decode("utf-8")

        # Extract title
        title = h5.root.metadata.songs.cols.title[0].decode("utf-8")
        
        # Extract genres
        genres = self.get_genres(h5)
        if (self.GENRE_LIST != None):
          matching_genres = [genre for genre in genres if genre in self.GENRE_LIST]
          if not matching_genres:
            return
          genres = matching_genres

        # Extract instruments
        instruments = self.get_instrument(msd_id)

        # Extract drums (returning pretty midi of drums)
        pm_drums = self.extract_drums(msd_id)

        # Extract pianos
        pm_pianos = self.extract_pianos(msd_id)

        return {
          "msd_id": msd_id,
          "artist": artist,
          "title": title,
          "genres": genres,
          "instruments": instruments,
          "pm_drums": pm_drums,
          "pm_pianos": pm_pianos
        }
      
    except Exception as e:
      print(f"Exception during processing of {msd_id}: {e}")
    finally:
      if (counter):
        counter.increment()


  def app(self, msd_ids: List[str], pool_size: int = 1, print_plot: bool = False):
    start = timeit.default_timer()

    print("START")

    if (pool_size > 1):
      # Start process with threading
      with Pool(pool_size) as pool:
        manager = Manager()
        counter = AtomicCounter(manager, len(msd_ids))
        
        results = pool.starmap(self.process, zip(msd_ids, cycle([counter])))
        results = [ result for result in results if result]
    else:
      # Start process without threading
      results = []
      for msd_id in msd_ids:
        result = self.process(msd_id)
        results.append(result)

    print("END")
    
    results_percentage = len(results) / len(msd_ids) * 100
    print(f"Number of tracks: {len(self.MSD_SCORE)}, "
          f"number of tracks in sample: {len(msd_ids)}, "
          f"number of results: {len(results)} "
          f"({results_percentage:.2f}%)")  # This percentage shows how many of the results passes the bass_drums_on_beat_threshold
    
    stop = timeit.default_timer()
    print("Time:", stop - start)


    if (print_plot):
      # Creates an histogram for the drum lengths
      artists = [result["artist"] for result in results if result]
      most_common_artists = Counter(artists).most_common(25)

      # Artist song count
      plt.figure(num=None, figsize=(10, 8), dpi=500)
      plt.bar([artist for artist, _ in most_common_artists],
              [count for _, count in most_common_artists],
              color=[color.name for color in colors if color.name != "lavender"])
      plt.title("Artist song count")
      plt.xticks(rotation=30, horizontalalignment="right")
      plt.ylabel("count")
      plt.show()

      # Most common genre plot (Only count the most relevant genre)
      tags = [result["genres"][0] for result in results if result and result["genres"]]
      most_common_tags_20 = Counter(tags).most_common(20)
      plt.bar([tag for tag, _ in most_common_tags_20],
              [count for _, count in most_common_tags_20])
      plt.title("Most common tags (20)")
      plt.xticks(rotation=30, horizontalalignment="right")
      plt.ylabel("count")
      plt.show()

      # Most common instruments plot (Count all instruments)
      classes_list = [result["instruments"] for result in results if result and result["instruments"]]
      classes = [c for classes in classes_list for c in classes]
      most_common_classes = Counter(classes).most_common()
      plt.bar([c for c, _ in most_common_classes],
              [count for _, count in most_common_classes])
      plt.title('Instrument classes')
      plt.xticks(rotation=30, horizontalalignment="right")
      plt.ylabel('count')
      plt.show()

  def extract(self, pool_size: int = 1, print_plot: bool = False):
    if self.SAMPLE_SIZE:
      # Randomly sample the list of MIDI_PATHS for sample_size number of times
      MSD_IDS = random.sample(list(self.MSD_SCORE), self.SAMPLE_SIZE)
    else:
      # Process all dataset
      MSD_IDS = list(self.MSD_SCORE)

    self.app(MSD_IDS, pool_size=pool_size, print_plot=print_plot)
