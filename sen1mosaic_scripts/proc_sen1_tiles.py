""" 
use sen1mosaic preprocess to process sen1 images
https://readthedocs.org/projects/sen1mosaic/downloads/pdf/latest/
"""
from datetime import datetime
sv_name = datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S')

import logging
logging.basicConfig(filename=f'./log/preproc_sen1_{sv_name}.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)


import numpy as np
import os
import subprocess
import csv


def logging_call(popenargs, **kwargs):
    """ 
    https://gist.github.com/jaketame/3ed43d1c52e9abccd742b1792c449079
    """
    process = subprocess.Popen(popenargs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def check_io():
        while True:
            output = process.stdout.readline().decode()
            # output = out.readline().decode()
            if output:
                logging.info(output)
            else:
                break

    # keep checking stdout/stderr until the child exits
    while process.poll() is None:
        check_io()


sen2_tile_info_pth = './BigEarthNetTileInfo_v2.npy'
data = np.load(sen2_tile_info_pth, allow_pickle=True).item()
tile_info = data['tile_info']

datahome = '/data/sen1_bigearth_sen1mosaic'

opj = os.path.join

log_csv = './log/down_sen1_20200403_115549.csv'
down_complete = dict()
with open(log_csv, newline='') as csvfile:
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
        # print(row)
        down_complete[row[0]] = int(row[1])

# previous processed sen1 images
last_prepoc_csv = './log/preproc_sen1_20200403_203138.csv'
preproc_complete = dict()
with open(last_prepoc_csv, newline='') as csvfile:
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
        # print(row)
        preproc_complete[row[0]] = int(row[1])


for tile_grid in list(tile_info.keys()):
    logging.info(f"processing tile grid {tile_grid}")

    for uuid in list(tile_info[tile_grid].keys()):
        logging.info(f"processing sen2 uuid {uuid}")
    
        download_dir = opj(datahome, tile_grid, uuid, 'download')
        processing_dir = opj(datahome, tile_grid, uuid, 'processing')
        tmp_dir = opj(datahome, tile_grid, uuid, 'tmp')

        if down_complete[download_dir]:

            if not os.path.isdir(processing_dir):
                os.makedirs(processing_dir)
                logging.info(f"making processing dir {processing_dir}")
            
            if not os.path.isdir(tmp_dir):
                os.makedirs(tmp_dir)
                logging.info(f"making temp dir {tmp_dir}")

            flag = True

            if processing_dir in preproc_complete and preproc_complete[processing_dir] == 1:
                with open(f'./log/preproc_sen1_{sv_name}.csv', 'a+', newline='') as write_obj:
                    csv_writer = csv.writer(write_obj)
                    csv_writer.writerow([processing_dir, f'{int(flag)}'])
                logging.info(f"{processing_dir} has been processed")
                continue
            
            ###
            # try:
            # os.system(f"s1m preprocess {download_dir} -o {processing_dir} -t {tmp_dir} -f -p 16 -v")
            bashCommand = f"python /home/jkang/sen1mosaic/cli/preprocess.py {download_dir} -o {processing_dir} -t {tmp_dir} -f -p 16 -v"

            try:
                process = subprocess.run(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,check=True)
                logging.info(process.stdout.decode())
            except Exception as e:
                flag = False
                logging.error("Exception occured", exc_info=True)
            
            with open(f'./log/preproc_sen1_{sv_name}.csv', 'a+', newline='') as write_obj:
                csv_writer = csv.writer(write_obj)
                csv_writer.writerow([processing_dir, f'{int(flag)}'])



