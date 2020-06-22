# Creation of BigEarthNet-Sen1

## Overall Pipeline

Based on the created BigEarthNet-Sen2 archive, the main steps for creating the corresponding BigEarthNet-Sen1 are introduced as follows:

- Retrieve the geo-locations of the Sentinel-2 tiles which are utilized for the creation of BigEarthNet-Sen2.

  - Getting the footprint of Sentinel-2 tiles in the meta data

  - Retrieve the Sentinel-1 tiles based on the footprint

  - For each Sentinel-2 tile, there may be several Sentinel-1 tiles covering it. In order to significantly reduce the number of Sentinel-1 tiles to be downloaded, [relative orbit](https://sentinel.esa.int/web/sentinel/missions/sentinel-1/satellite-description/orbit) of each tile should be retrieved. For each relative orbit, we just keep one Sentinel-1 tile, to avoid the duplicated Sentinel-1 tiles for downloading.

  - Also, we should make sure that the union of the footprints of the Sentinel-1 tiles should cover the Sentinel-2 tile

  - Finally, we can get the product information of the Sentinel-1 tiles to be downloaded

    The code can be found in `/home/jkang/Documents/py/Sen1_BigEarthNet/notebook/Sen2tile2Sen1tile.ipynb`

- The following work is based on the [Sen1mosaic](https://readthedocs.org/projects/sen1mosaic/downloads/pdf/latest/) python toolbox:

- Based on the created Sen2TileUUID2Sen1TileUUID, we download the corresponding tiles via `/home/jkang/Documents/py/Sen1_BigEarthNet/sen1mosaic_scripts/down_sen1_tiles.py`

- Preprocess the downloaded Sentinel-1 tiles based on the following steps:

  - GRD border noise removal

  - Thermal noise removal

  - Radiometric calibration

  - Speckle noise filtering

  - Terrain correction

  - Transform into decibels (dB)

    These functions can be achieved based on ```/home/jkang/Documents/py/Sen1_BigEarthNet/sen1mosaic_scripts/proc_sen1_tiles.py``` and ```/home/jkang/Documents/py/Sen1_BigEarthNet/sen1mosaic_scripts/proc_defected_S1_tiles```

    For **Radiometric calibration**, for some tiles with high latitude, there are some problems, so it is not necessary for this step. For **Terrain correction**, for some tiles with high latitude, ASTER DEM is needed, not SRTM. For reference, refer to [Sentinel-1 preprocessing on Google Earth Engine](https://developers.google.com/earth-engine/sentinel1). For the xml file run with snap, GraphBuilder function can be used for visualizing some example processing chains.

* Mosaic the preprocessed SAR images via `/home/jkang/Documents/py/Sen1_BigEarthNet/sen1mosaic_scripts/mosaic_sen1_tiles.py`
* Clip the mosaic SAR images with respect to the associated Sentinel-2 tiles via `/home/jkang/Documents/py/Sen1_BigEarthNet/sen1mosaic_scripts/clip_patches_sen1_tiles.py`

* Create the BigEarthNet-Sen1 via `/home/jkang/Documents/py/Sen1_BigEarthNet/sen1mosaic_scripts/sv_sen1_bigearthV1_nms.py`