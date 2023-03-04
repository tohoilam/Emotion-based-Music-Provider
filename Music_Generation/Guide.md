
# Data Preparation Steps

## Step 1:

Filter MIDI file by genre, emotion, instruments, and other information.

```
python3 DataRunner.py --dataset_dir="data/LAKH-MIDI-Dataset-Matched" --h5_matched_dir="data/LAKH-H5-Matched" --midi_dir="midi_data" --match_scores_filepath="data/match_scores.json" --genre_list="['pop']" --sample_size=10000 --pool_size=4
```

## Step 2 : Convert from MIDI to NoteSequence

Pack `MIDI` data to `NoteSequence` data

```
convert_dir_to_note_sequences --input_dir="/Users/alexto/Documents/ProgrammingProjects/Emotion-based-Music-Provider/Music_Generation/midi_data/pianos/Happiness" --output_file="/Users/alexto/Documents/ProgrammingProjects/Emotion-based-Music-Provider/Music_Generation/training_input/Happiness/happiness_notesequences.tfrecord"
```

Note:
* --input_dir MUST be full path


## Step 3 : From NoteSequence to Training Input (training_melodies.tfrecord)
```
python3 melody_rnn_pipeline.py --input="/Users/alexto/Documents/ProgrammingProjects/Emotion-based-Music-Provider/Music_Generation/training_input/Happiness/happiness_notesequences.tfrecord" --output_dir="/Users/alexto/Documents/ProgrammingProjects/Emotion-based-Music-Provider/Music_Generation/training_input/Happiness" --config="attention_rnn"
```

Will Generate...

* `training_melodies.tfrecord` : Data ready for Training purposes
* `eval_melodies.tfrecord` : Data ready for Evaluation purposes

`--config` options:

* basic_rnn
* mono_rnn
* lookback_rnn
* attention_rnn