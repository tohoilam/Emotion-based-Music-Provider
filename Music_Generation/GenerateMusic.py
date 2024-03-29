import os
import math
import time
import copy
import magenta.music as mm

from magenta.music import DEFAULT_QUARTERS_PER_MINUTE
from magenta.models.melody_rnn import melody_rnn_sequence_generator

from note_seq.protobuf.music_pb2 import NoteSequence
from note_seq.protobuf.generator_pb2 import GeneratorOptions
from note_seq import notebook_utils
from magenta.models.shared import sequence_generator_bundle
from magenta.models.polyphony_rnn import polyphony_sequence_generator
from magenta.models.performance_rnn import performance_sequence_generator
from visual_midi import Plotter, Preset
from pretty_midi import PrettyMIDI, Instrument
from IPython import display


def generate_music(bundle_path: str,
                  sequence_generator_option: str,
                  generator_id: str = None,
                  primer_path: str = None,
                  qpm: float = DEFAULT_QUARTERS_PER_MINUTE,
                  total_length_steps: int = 64,
                  temperature: float = 1.0,
                  beam_size: int = 1,
                  branch_factor: int = 1,
                  steps_per_iteration: int = 1,
                  show_plot: bool = False) -> NoteSequence:

  if (not os.path.isabs(bundle_path)):
    bundle_path = os.path.abspath(bundle_path)
  
  if (not os.path.isabs(primer_path)):
    primer_path = os.path.abspath(primer_path)

  sequence_generator_available_option = ["melody_rnn"]
  if (sequence_generator_option not in sequence_generator_available_option):
    print(f"Please choose an available sequence generator in {str(sequence_generator_available_option)}")
    return None

  if (sequence_generator_option == "melody_rnn"):
    sequence_generator = melody_rnn_sequence_generator
  
  if (sequence_generator_option == "polyphony"):
    sequence_generator = polyphony_sequence_generator
  
  if (sequence_generator_option == "performance"):
    sequence_generator = performance_sequence_generator

  bundle = sequence_generator_bundle.read_bundle_file(bundle_path)

  # Initialize generator
  generator_map = sequence_generator.get_generator_map()
  generator = generator_map[generator_id](checkpoint=None, bundle=bundle)
  generator.initialize()
  
  # Configure Primer Sequence
  if primer_path:
    primer_sequence = mm.midi_io.midi_file_to_note_sequence(primer_path)
  else:
    # If no primer, then empty note sequence
    primer_sequence = NoteSequence()

  # Configure qpm parameter (if primer_sequence has a qpm)
  if primer_sequence.tempos:
    if (len(primer_sequence.tempos) > 1):
      # Magenta does not handle multple tempos  in a midi
      raise Exception("No support for multiple tempos")
    qpm = primer_sequence.tempos[0].qpm

  # Calculate seconds per 1 step
  # step_per_quarter is mostly 4 in generator problems
  seconds_per_step = 60.0 / qpm / getattr(generator, "steps_per_quarter", 4)
  
  # Calculate primer sequence length in steps
  primer_sequence_length_steps = math.ceil(primer_sequence.total_time / seconds_per_step)
  primer_sequence_length_time = (primer_sequence_length_steps * seconds_per_step)

  # Calculate start and end of primer sequence
  # NOTE: We add a negative delta to the end, because if we don't, some generators won't start the generation right at the beginning of the bar
  #                                                                instead, start at the next step (which means a small gap between primer and generater sequence)
  primer_end_adjust = (0.00001 if primer_sequence_length_time > 0 else 0)
  primer_start_time = 0
  primer_end_time = (primer_start_time + primer_sequence_length_time - primer_end_adjust)

  # Calculate length for generation sequence as well as start and end time
  generation_length_steps = total_length_steps - primer_sequence_length_steps
  generation_length_time = generation_length_steps - seconds_per_step
  generation_start_time = primer_end_time
  generation_end_time = (generation_start_time + generation_length_time + primer_end_adjust)

  # Calculate generation time
  generation_length_steps = total_length_steps - primer_sequence_length_steps
  if generation_length_steps <= 0:
    raise Exception(f"Total length in steps too small ({str(total_length_steps)}), needs to be at least one bar bigger than primer ({str(primer_sequence_length_steps)})")
  generation_length_time = generation_length_steps * seconds_per_step

  # Show time
  print(f"Primer time: [{str(primer_start_time)}, {str(primer_end_time)}]")
  print(f"Generation time: [{str(generation_start_time)}, {str(generation_end_time)}]")

  # Add configuration into generator_options
  generator_options = GeneratorOptions()
  generator_options.args['temperature'].float_value = temperature
  generator_options.args['beam_size'].int_value = beam_size
  generator_options.args['branch_factor'].int_value = branch_factor
  generator_options.args['steps_per_iteration'].int_value = steps_per_iteration
  generator_options.generate_sections.add(
    start_time = generation_start_time,
    end_time = generation_end_time
  )

  # Generate Sequence
  sequence = generator.generate(primer_sequence, generator_options)

  # Write the resulting midi file to the output directory
  date_and_time = time.strftime('%Y-%m-%d_%H%M%S')
  generator_name = str(generator.__class__).split(".")[2]
  plot_filename = "%s_%s_%s.html" % (generator_name, generator_id, date_and_time)
  plot_path = os.path.abspath(os.path.join("midi_plot", plot_filename))

  pretty_midi = mm.midi_io.note_sequence_to_pretty_midi(sequence)
  plotter = Plotter()
  if show_plot:
    plotter.show(pretty_midi, plot_path)
  else:
    plotter.save(pretty_midi, plot_path)

  print("Generated plot file: " + str(os.path.abspath(plot_path)))

  return sequence

def prepare_primers_midi_from_dir(midi_dir_path: str,
                                  save_dir: str,
                                  num_of_midi: int = None,
                                  num_of_primers: int = 10):
  count = 0
  midi_paths = []

  for dirname, _, filenames in os.walk(midi_dir_path):
    for filename in filenames:
      if filename[-4:] != ".mid":
        print(f"Incorrect file type: {filename}")
        continue

      midi_paths.append(os.path.join(dirname, filename))

      count += 1
      if (count != None and count >= num_of_midi):
        break
    if (count != None and count >= num_of_midi):
      break
  
  print(f"Number of primers midi to prepare: {count}\n")

  primers_midi_paths = []

  for midi_path in midi_paths:
    primers_midi_path = prepare_primers_midi(midi_path, save_dir, num_of_primers)
    primers_midi_paths.append(primers_midi_path)

  print(f"\nAll {count} primers midi prepared!")

  return primers_midi_paths

def prepare_primers_midi(midi_path: str, save_dir: str, num_of_primers: int = 10):
  if (not os.path.isabs(midi_path)):
    midi_path = os.path.abspath(midi_path)
  
  if (not os.path.isabs(save_dir)):
    save_dir = os.path.abspath(save_dir)

  filename = os.path.basename(midi_path)[:-4]

  pm = PrettyMIDI(midi_path)

  if (len(pm.instruments) != 1):
    print(f"Warning: Number of instruments is {len(pm.instruments)}")

  instrument = pm.instruments[0]

  if instrument.is_drum:
    print("Warning: Instrument is drum, please change to non-drum instruments")

  pm_piano = copy.deepcopy(pm)
  pm_piano_instrument = Instrument(program=instrument.program)
  pm_piano.instruments = [pm_piano_instrument]

  count = 0
  for note in instrument.notes:
    pm_piano_instrument.notes.append(note)
    count += 1
    if (count >= num_of_primers):
      break

  new_pm_path = os.path.join(save_dir, f"{filename}_primer_{num_of_primers}.mid")

  pm_piano.write(new_pm_path)

  print(f"New primers midi prepared at {new_pm_path}")

  return new_pm_path

