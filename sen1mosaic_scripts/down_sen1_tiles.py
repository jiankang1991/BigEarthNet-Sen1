""" 
use sen1mosaic and ost to download sen1 images
https://readthedocs.org/projects/sen1mosaic/downloads/pdf/latest/
"""
from datetime import datetime
sv_name = datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S')

import logging
logging.basicConfig(filename=f'./log/down_sen1_{sv_name}.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)

import numpy as np
import os
from pathlib import Path
from datetime import date, datetime, timedelta
# import datetime
import shapely.wkt
import pandas as pd
import csv
from down_utils import download_sentinel1

sen2_tile_info_pth = './BigEarthNetTileInfo_v2.npy'
sen1_tile_download_info_pth = './BigEarthNetSen2UUID2Sen1ProdName.npy'

data = np.load(sen2_tile_info_pth, allow_pickle=True).item()
tile_info = data['tile_info']

data = np.load(sen1_tile_download_info_pth, allow_pickle=True).item()
Sen2UUID_2_Sen1ProdNames = data['Sen2UUID_2_Sen1ProdName']

datahome = '/data/sen1_bigearth_sen1mosaic'

# period = 3
# buffer = 0.15 # buffer in GPS coordinates

fmt_str = r"%Y-%m-%d"

earth_data_usr = ''
earth_data_psd = ''

opj = os.path.join

downloaded_failed_sen1_prod = []

for tile_grid in list(tile_info.keys()):
    logging.info(f"processing tile grid {tile_grid}")

    for uuid in list(tile_info[tile_grid].keys()):
        logging.info(f"processing sen2 uuid {uuid}")

        if not os.path.isdir(opj(datahome, tile_grid, uuid)):
            os.makedirs(opj(datahome, tile_grid, uuid))
            logging.info(f"making dir {opj(datahome, tile_grid, uuid)}")

        # wkt_polygon = tile_info[tile_grid][uuid]['footprint']
        # sen2_shp = shapely.wkt.loads(wkt_polygon)
        # sen2_shp_buf = sen2_shp.buffer(buffer, cap_style=1, join_style=2)
        # # wkt_polygon = sen2_shp_buf.wkt
        # minlon, minlat, maxlon, maxlat = sen2_shp_buf.bounds

        # str_date = tile_info[tile_grid][uuid]['acquisition_time'].split(' ')[0]
        # mid_date = datetime.strptime(str_date, fmt_str)
        # start = (mid_date-timedelta(days=period)).date()
        # end = (mid_date+timedelta(days=period)).date()

        # retrieve the sen1 products from the sen2 uuid
        sen1_tiles = Sen2UUID_2_Sen1ProdNames[uuid]
        download_dir = opj(datahome, tile_grid, uuid, 'download')

        if not os.path.isdir(download_dir):
            os.mkdir(download_dir)

        logging.info(f"downloading sen1 tiles into {download_dir}")
        suc_finished = True

        df = pd.DataFrame({'identifier': sen1_tiles})
        try:
            download_sentinel1(df, download_dir, concurrent=2, uname=earth_data_usr, pword=earth_data_psd)
        except Exception as e:
            suc_finished = False
            logging.info(" ")
            logging.error("Exception occured", exc_info=True)
            logging.info(" ")
        # if all the tiles are successfully downloaded, set 1
        with open(f'./log/down_sen1_{sv_name}.csv', 'a+', newline='') as write_obj:
            csv_writer = csv.writer(write_obj)
            csv_writer.writerow([download_dir, f'{int(suc_finished)}'])
            








