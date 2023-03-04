import argparse
from Data import Data

parser = argparse.ArgumentParser()

parser.add_argument("--dataset_dir", type=str, required=True)
parser.add_argument("--h5_matched_dir", type=str, required=True)
parser.add_argument("--midi_dir", type=str, required=True)
parser.add_argument("--match_scores_filepath", type=str, required=True)
parser.add_argument("--genre_list", type=str, default=None)
parser.add_argument("--sample_size", type=int, default=None)
parser.add_argument("--pool_size", type=int, default=1)
parser.add_argument("--print_plot", type=bool, default=False)

args = parser.parse_args()

if __name__ == "__main__":
  data = Data(args.dataset_dir, args.h5_matched_dir, args.midi_dir, args.match_scores_filepath, args.genre_list, args.sample_size)
  data.extract(args.pool_size, args.print_plot)

# Example Usage
# python3 DataRunner.py --dataset_dir="data/LAKH-MIDI-Dataset-Matched" --h5_matched_dir="data/LAKH-H5-Matched" --midi_dir="midi_data" --match_scores_filepath="data/match_scores.json" --genre_list="['pop']" --sample_size=10000 --pool_size=4
