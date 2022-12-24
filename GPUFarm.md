# GPU Farm Instruction

## Initialization

### Terminal
1. `ssh -X hlto@gpugate1.cs.hku.hk`
2. `gpu-interactive` or `srun --gres=gpu:2 --cpus-per-task=8 --pty --mail-type=ALL bash`
3. `conda activate tensorflow`
4. `hostname -I`
5. `jupyter-lab --no-browser --FileContentsManager.delete_to_trash=False`
6. New Tab
7. `ssh -L 8888:localhost:8888 hlto@10.XXX.XXX.XXX`
8. Open website link