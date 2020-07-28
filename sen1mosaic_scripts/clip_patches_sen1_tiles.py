""" 
create GeoTiff sen1 patches for BigEarthNet
"""

from datetime import datetime
sv_name = datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S')

import logging
logging.basicConfig(filename=f'./log/clip_df_sen1_{sv_name}.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)

import numpy as np
import os
import csv
import subprocess
import multiprocessing
import shutil

MAX_ROW_NUM = 90
MAX_COL_NUM = 90
W, H = 5480, 5480
patch_sz = 60

sen2_tile_info_pth = './BigEarthNetTileInfo.npy'
data = np.load(sen2_tile_info_pth, allow_pickle=True).item()
tile_info = data['tile_info']

datahome = '/data/sen1_bigearth_sen1mosaic'

opj = os.path.join

## mosaic csv file
# log_csv = './log/mosaic_df_sen1_20200612_164156.csv'
log_csv = './log/preproc_df_sen1_20200612_120620.csv'

S2Tile2Patch = np.load('./S2Tile2Patches.npy', allow_pickle=True).item()['S2Tile2Patch']


mosaic_complete = dict()
with open(log_csv, newline='') as csvfile:
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
        # print(row)
        mosaic_dir = opj('/'.join(row[0].split('/')[:-1]), 'tif')
        mosaic_complete[mosaic_dir] = int(row[1])

# previous processed sen1 images
last_clip_csv = './log/clip_df_sen1_20200618_152435.csv'

clip_complete = dict()
with open(last_clip_csv, newline='') as csvfile:
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
        # print(row)
        clip_complete[row[0]] = int(row[1])


def createImgPatches(clip_info):
    """ 
    https://gdal.org/programs/gdal_translate.html
    https://gis.stackexchange.com/questions/14712/splitting-raster-into-smaller-chunks-using-gdal
    """
    x, y, patch_sz, VV_mean_tif_pth, VV_pat_pth, VH_mean_tif_pth, VH_pat_pth = clip_info

    bashCommand_VV = f"gdal_translate -of GTiff -srcwin {x} {y} {patch_sz} {patch_sz} {VV_mean_tif_pth} {VV_pat_pth}"
    bashCommand_VH = f"gdal_translate -of GTiff -srcwin {x} {y} {patch_sz} {patch_sz} {VH_mean_tif_pth} {VH_pat_pth}"

    process_VV = subprocess.run(bashCommand_VV.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,check=True)
    process_VH = subprocess.run(bashCommand_VH.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,check=True)

def clipTile2ImgPatches(tif_dir, uuid, VVVH_patch_dir):

    tile_tif_dir = tif_dir
    # sen2_prod_nm = tile_tif_sen2_prod_nm[1]

    VV_mean_tif_pth = opj(tile_tif_dir, 'sen1_mean_VV_R20m.tif')
    VH_mean_tif_pth = opj(tile_tif_dir, 'sen1_mean_VH_R20m.tif')

    flag = True
    logging.info(f"clipping patch for {tile_tif_dir}")

    clip_info_list = []

    S2_idx = 0
    no_S2_idx = 0

    for i, x in enumerate(range(0, W-patch_sz, patch_sz)):
        for j, y in enumerate(range(0, H-patch_sz, patch_sz)):
            
            if f"{i}_{j}" in S2Tile2Patch[uuid]:
                sen2_prod_nm = S2Tile2Patch[uuid][f"{i}_{j}"]
                S2_idx += 1
            else:
                sen2_prod_nm = S2Tile2Patch[uuid]['prefix']
                no_S2_idx += 1

            patch_dir = opj(VVVH_patch_dir, f'{sen2_prod_nm}_S1_{i}_{j}')
            
            if not os.path.isdir(patch_dir):
                os.makedirs(patch_dir)

            VV_pat_pth = opj(patch_dir, f'{sen2_prod_nm}_S1_{i}_{j}_VV.tif')
            VH_pat_pth = opj(patch_dir, f'{sen2_prod_nm}_S1_{i}_{j}_VH.tif')

            clip_info_list.append((x,y,patch_sz,VV_mean_tif_pth,VV_pat_pth,VH_mean_tif_pth,VH_pat_pth))
    
    logging.info(f"within S2 tiles: {S2_idx}")
    logging.info(f"without S2 tiles: {no_S2_idx}")

    try:
        pool = multiprocessing.Pool(processes=16)
        # pool.map(clipper(VVVH_patch_dir), tils_tif_dir_sen2_product_names)
        pool.map(createImgPatches, clip_info_list)
    except Exception as e:
        flag = False
        logging.error("Exception occured", exc_info=True)

    with open(f'./log/clip_df_sen1_{sv_name}.csv', 'a+', newline='') as write_obj:
        csv_writer = csv.writer(write_obj)
        csv_writer.writerow([VVVH_patch_dir, f'{int(flag)}'])

    
# class clipper:
#     def __init__(self, VVVH_patch_dir):
#         self.VVVH_patch_dir = VVVH_patch_dir
#     def __call__(self, tile_tif_sen2_prod_nm):
#         clipTile2ImgPatches(tile_tif_sen2_prod_nm, self.VVVH_patch_dir)



for tile_grid in list(tile_info.keys()):
    logging.info(f"mosaicing tile grid {tile_grid}")

    # tiles_tif_dir = []
    # sen2_product_names = []

    # tils_tif_dir_sen2_product_names = []

    for uuid in list(tile_info[tile_grid].keys()):
        logging.info(f"mosaicing sen2 uuid {uuid}")

        tif_dir = opj(datahome, tile_grid, uuid, 'tif')
        
        # sen2_prod_nm = tile_info[tile_grid][uuid]['product_name'].split('_')
        # sen2_prod_p_nm = '_'.join([sen2_prod_nm[0], 'MSIL2A', sen2_prod_nm[2]])
        
        # sen2_prod_p_nm = S2Tile2Patch[uuid]['prefix']

        if tif_dir in mosaic_complete and mosaic_complete[tif_dir]:
            
            # tils_tif_dir_sen2_product_names.append((tif_dir, sen2_prod_p_nm))
            # tiles_tif_dir.append(tif_dir)
            # sen2_product_names.append(sen2_prod_p_nm)

            VVVH_patch_dir = opj(datahome, tile_grid, uuid, 'VVVH_patches')
            # VV_patch_dir = opj(datahome, tile_grid, uuid, 'VV_patches')

            if not os.path.isdir(VVVH_patch_dir):
                os.makedirs(VVVH_patch_dir)
                logging.info(f"making VVVH patches dir {VVVH_patch_dir}")

            if VVVH_patch_dir in clip_complete and clip_complete[VVVH_patch_dir] == 1:
                with open(f'./log/clip_df_sen1_{sv_name}.csv', 'a+', newline='') as write_obj:
                    csv_writer = csv.writer(write_obj)
                    csv_writer.writerow([VVVH_patch_dir, '1'])
                logging.info(f"{VVVH_patch_dir} has been processed")
                continue

            shutil.rmtree(VVVH_patch_dir)

            # tif_dir_sen2_nm = (tif_dir, S2Tile2Patch)
            clipTile2ImgPatches(tif_dir, uuid, VVVH_patch_dir)
    

