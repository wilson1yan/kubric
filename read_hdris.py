from bs4 import BeautifulSoup
import os
import os.path as osp
from tqdm import tqdm

FORMAT = 'https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/4k/{}_4k.hdr'

with open('hdri.html') as fp:
    soup = BeautifulSoup(fp, 'html.parser')
out = soup.select('a[class*="GridItem_gridItem__"]')
hdri_paths = [o['href'][3:] for o in out] # remove '/a/'

os.makedirs('hdris', exist_ok=True)
for path in tqdm(hdri_paths):
    url = FORMAT.format(path)
    cmd = f'wget {url} -P hdris'
    os.system(cmd)