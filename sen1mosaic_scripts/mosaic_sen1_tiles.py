""" 
use sen1mosaic mosaic to merge sen1 images
https://readthedocs.org/projects/sen1mosaic/downloads/pdf/latest/
"""
from datetime import datetime
sv_name = datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S')

import logging
logging.basicConfig(filename=f'./log/mosaic_sen1_{sv_name}.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)

import numpy as np
import os
import subprocess
import csv

# sen2_tile_info_pth = './BigEarthNetTileInfo_v2.npy'
# data = np.load(sen2_tile_info_pth, allow_pickle=True).item()
# tile_info = data['tile_info']

sen2_tile_info_pth = './BigEarthNetTileInfo.npy'
data = np.load(sen2_tile_info_pth, allow_pickle=True).item()
tile_info = data['tile_info']

datahome = '/data/sen1_bigearth_sen1mosaic'

opj = os.path.join

log_csv = './log/preproc_sen1_20200406_081346.csv'

preproc_complete = dict()
with open(log_csv, newline='') as csvfile:
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
        # print(row)
        preproc_complete[row[0]] = int(row[1])

## TODO change it into multi-processing

for tile_grid in list(tile_info.keys()):
    logging.info(f"mosaicing tile grid {tile_grid}")

    for uuid in list(tile_info[tile_grid].keys()):
        logging.info(f"mosaicing sen2 uuid {uuid}")
        
        epsg = tile_info[tile_grid][uuid]['EPSG'].decode()
        ul_x, ul_y, br_x, br_y = tile_info[tile_grid][uuid]['coordinate']
        xmin = min(ul_x, br_x)
        xmax = max(ul_x, br_x)
        ymin = min(ul_y, br_y)
        ymax = max(ul_y, br_y)

        download_dir = opj(datahome, tile_grid, uuid, 'download')
        processing_dir = opj(datahome, tile_grid, uuid, 'processing')
        tif_dir = opj(datahome, tile_grid, uuid, 'tif')
        tmp_dir = opj(datahome, tile_grid, uuid, 'tmp')

        if preproc_complete[processing_dir]:

            if not os.path.isdir(tif_dir):
                os.makedirs(tif_dir)
                logging.info(f"making mosaicing dir {tif_dir}")

            flag = True

            bashCommand = f"python /home/jkang/sen1mosaic/cli/mosaic.py {processing_dir} -o {tif_dir} -te {xmin} {ymin} {xmax} {ymax} -e {epsg} -r 20 -n sen1 -v"
            
            try:
                process = subprocess.run(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,check=True)
                logging.info(process.stdout.decode())
            except Exception as e:
                flag = False
                logging.error("Exception occured", exc_info=True)

            with open(f'./log/mosaic_sen1_{sv_name}.csv', 'a+', newline='') as write_obj:
                csv_writer = csv.writer(write_obj)
                csv_writer.writerow([tif_dir, f'{int(flag)}'])



