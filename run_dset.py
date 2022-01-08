import os
import os.path as osp
import argparse
import multiprocessing as mp

DATASET = 'MOVi-v1'

def generate_episode(i):
    output_dir = osp.join('datasets', DATASET, f'episode_{i}')
    cmd = f'python examples/movid.py --job-dir {output_dir}' 
    os.system(cmd)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--n_episodes', type=int, default=11000)
    parser.add_argument('-p', '--n_procs', type=int, default=32)
    args = parser.parse_args()

    os.makedirs(osp.join('datasets', DATASET), exist_ok=True)

    pool = mp.Pool(args.n_procs)
    pool.map(generate_episode, range(args.n_episodes))
    print('Done')
