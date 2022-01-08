import os
import os.path as osp
import h5py
import argparse
import glob
import json
import numpy as np
from PIL import Image
import multiprocessing as mp
from tqdm import tqdm


def read(path):
    img_files = glob.glob(osp.join(path, 'rgba_*.png'))
    md = json.load(open(osp.join(path, 'metadata.json')))
    bboxes = md['instances']
    bboxes = [bbox['bboxes'] for bbox in bboxes]
    bboxes = np.array(bboxes) # KT4
    bboxes = np.transpose(bboxes, (1, 0, 2)) # TK4 in y1, x1, y2, x2
    
    shift_x = 2 * (bboxes[:, :, 1] +  bboxes[:, :, 3]) - 1
    shift_y = 2 * (bboxes[:, :, 0] +  bboxes[:, :, 2]) - 1
    width = bboxes[:, :, 3] - bboxes[:, :, 1]
    height = bboxes[:, :, 2] - bboxes[:, :, 0]
    bboxes = np.stack((shift_x, shift_y, width, height), axis=-1) # TK4

    imgs = []
    for img_f in img_files:
        img = Image.open(img_f)
        img = np.array(img)
        imgs.append(img)
    imgs = np.stack(imgs) # THWC

    return imgs, bboxes

def process_split(episode_paths, split):
    pool = mp.Pool(32)
    result = list(tqdm(pool.imap(episode_paths), total=len(episode_paths)))
    imgs, bboxes = list(zip(*result))
    idxs = [0]
    for i in range(len(imgs)):
        idxs.append(idxs[-1] + len(imgs[i]))
    idxs = np.array(idxs[:-1])
    assert len(idxs) == len(imgs) == len(bboxes)

    imgs = np.concatenate(imgs, axis=0)
    bboxes = np.concatenate(bboxes, axis=0)
    assert len(imgs) == len(bboxes)
    
    f.create_dataset(f'{split}_data', data=imgs)
    f.create_dataset(f'{split}_bboxes', data=bboxes.astype(np.float32))
    f.create_dataset(f'{split}_idx', data=idxs)

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--data_path', type=str, required=True)
args = parser.parse_args()

if args.data_path[-1] == '/':
    args.data_path = args.data_path[:-1]

episode_paths = glob.glob(osp.join(args.data_path, 'episode_*'))
print(f'Found {len(episode_paths)} episodes')

f = h5py.File(args.data_path + '.hdf5', 'a')

t = min(500, int(len(episode_paths) * 0.1))
train_paths = episode_paths[:-t]
process_split(train_paths, 'train')

test_paths = episode_paths[-t:]
process_split(test_paths, 'test')