# GPU Farm Instruction

## Initialization

### Terminal
1. `ssh -X hlto@gpugate1.cs.hku.hk`
2. `gpu-interactive` or `srun --gres=gpu:2 --cpus-per-task=8 --pty --mail-type=ALL bash` or `srun --gres=gpu:4 --cpus-per-task=16 --pty --mail-type=ALL bash`
  * With 3090: `srun --gres=gpu:rtx3090:2 --cpus-per-task=8 --pty --mail-type=ALL bash -p q3090`
3. `conda activate tensorflow` or `source activate magenta`
4. `hostname -I`
5. `jupyter-lab --no-browser --FileContentsManager.delete_to_trash=False`
6. New Tab
7. `ssh -L 8888:localhost:8888 hlto@10.XXX.XXX.XXX`
8. Open website link



### Install magenta

1. Clone Magenta: `git clone https://github.com/tensorflow/magenta.git`
2. Follow README.py from `https://github.com/0x00009b/pkget` to install `libjack-dev` and `libasound2-dev`
  1. `wget https://raw.githubusercontent.com/0x00009b/pkget/master/pget && chmod +x pget`
  2. `vi pget` anc change `BUILD_DIR=/home/$USER` to your desired directory
  3. `./pget libjack-dev`
  4. `./pget libasound2-dev`
3. Install GCC: `conda install -c conda-forge gcc`
4. Install G++: `conda install -c conda-forge gxx`
4. Install Wheel: `pip install wheel`
5. Setup Magenta: `pip install -e .`