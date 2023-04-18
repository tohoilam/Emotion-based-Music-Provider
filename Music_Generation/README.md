# Set Up

1. Go to this site: https://colinraffel.com/projects/lmd/
2. Download the following:
    * LMD-matched
    * Match scores
    * LMD-matched metadata
3. Create a directory named `data` and store the 3 folders/file separately in the `data` directory
4. Follow [Magenta GitHub Site](https://github.com/magenta/magenta) for magenta installation
5. Run `pip install -r requirements.txt`
  * Note, I simply put all my pip version into requirements.txt, so pip version may affect your other projects, so be careful!!!


# Data Preparation and Training Steps

**IMPORTANT NOTE: Step 1 to 3 for Pop piano music with Happiness and Angry data has already been done**

* So can directly run step 4 for training
* OR Change the parameter and run step 1 to 3 again

## Step 1:

Filter MIDI file by genre, emotion, instruments, and other information.

```
python3 DataRunner.py --dataset_dir="data/LAKH-MIDI-Dataset-Matched" --h5_matched_dir="data/LAKH-H5-Matched" --midi_dir="midi_data" --match_scores_filepath="data/match_scores.json" --genre_list="['pop']" --pool_size=4
```

* Note: `--pool_size=1` means no threading

## Step 2 : Convert from MIDI to NoteSequence

Pack `MIDI` data to `NoteSequence` data

```
convert_dir_to_note_sequences --input_dir="/Users/alexto/Documents/ProgrammingProjects/Emotion-based-Music-Provider/Music_Generation/midi_data/guitars/Calmness" --output_file="/Users/alexto/Documents/ProgrammingProjects/Emotion-based-Music-Provider/Music_Generation/training_input/pianosAndGuitars_calmness_notesequences.tfrecord"
```


## Step 3 : From NoteSequence to Training Input (training_melodies.tfrecord)
```
python3 melody_rnn_pipeline.py --input="/Users/alexto/Documents/ProgrammingProjects/Emotion-based-Music-Provider/Music_Generation/training_input/pianosAndGuitars_calmness_notesequences.tfrecord" --output_dir="/Users/alexto/Documents/ProgrammingProjects/Emotion-based-Music-Provider/Music_Generation/training_input/attention_rnn/guitars_and_pianos/Calmness" --config="attention_rnn"
```

Will Generate...

* `training_melodies.tfrecord` : Data ready for Training purposes
* `eval_melodies.tfrecord` : Data ready for Evaluation purposes

`--config` options:

* basic_rnn
* mono_rnn
* lookback_rnn
* attention_rnn

## Step 4 : Train
```
melody_rnn_train --config="attention_rnn" --run_dir="logdir/baseline_attention_model_3" --sequence_example_file="training_input/Happiness/training_melodies.tfrecord" --hparams="batch_size=64,rnn_layer_sizes=[64,64]" --num_training_steps=20000

melody_rnn_train --config="attention_rnn" --run_dir="logdir/test_model" --sequence_example_file="training_input/Happiness/training_melodies.tfrecord" --hparams="batch_size=64,rnn_layer_sizes=[64,64]" --num_training_steps=200
```


`--config` options:

* basic_rnn
* mono_rnn
* lookback_rnn
* attention_rnn


## Step 5 : Generation with Console

```
melody_rnn_generate \
--config=attention_rnn \
--run_dir=/Users/alexto/Documents/ProgrammingProjects/Emotion-based-Music-Provider/Music_Generation/logdir/angry_baseline_attention_model_1 \
--output_dir=/Users/alexto/Documents/ProgrammingProjects/Emotion-based-Music-Provider/Music_Generation/generation/Happiness/angry_baseline_attention_model_1 \
--num_outputs=10 \
--num_steps=128 \
--primer_melody="[60]" \
--hparams="batch_size=64,rnn_layer_sizes=[64,64]"
```

## Step 6 : Evaluation with Console

```
CUDA_VISIBLE_DEVICES=-1 melody_rnn_train --config="attention_rnn" --run_dir="logdir/baseline_attention_model_3" --sequence_example_file="training_input/Happiness/eval_melodies.tfrecord" --hparams="batch_size=64,rnn_layer_sizes=[64,64]" --num_training_steps=2000 --eval

tensorboard --logdir="logdir/happiness_baseline_attention_model_1"
```

## Step 7: Pack Bundle

```
melody_rnn_generate \
--config=attention_rnn \
--run_dir=/Users/alexto/Documents/ProgrammingProjects/Emotion-based-Music-Provider/Music_Generation/logdir/angry_baseline_attention_model_1 \
--hparams="batch_size=64,rnn_layer_sizes=[64,64]" \
--bundle_file="/Users/alexto/Documents/ProgrammingProjects/Emotion-based-Music-Provider/Music_Generation/mag_models/angry_baseline_attention_model_1.mag" \
--save_generator_bundle
```

## Genererate from Bundle with Console

```
melody_rnn_generate \
--config=attention_rnn \
--output_dir=/Users/alexto/Documents/ProgrammingProjects/Emotion-based-Music-Provider/Music_Generation/generation/Happiness/angry_baseline_attention_model_1 \
--num_outputs=10 \
--num_steps=128 \
--primer_melody="[60]" \
--hparams="batch_size=64,rnn_layer_sizes=[64,64]" \
--bundle_file="/Users/alexto/Documents/ProgrammingProjects/Emotion-based-Music-Provider/Music_Generation/mag_models/angry_baseline_attention_model_1.mag"
```
