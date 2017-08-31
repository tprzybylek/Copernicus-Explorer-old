import os, sys
from osgeo import gdal

#####################################################
raster = 'D:\\test\\S1B_IW_GRDH_1SDV_20170101T045911_20170101T045940_003650_006425_45AB.SAFE\\measurement\\s1b-iw-grd-vh-20170101t045911-20170101t045940-003650-006425-002.tiff'

WKT_Projection = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'

raster_georef = 'D:\\test\\raster_georef.tiff'
raster_output = 'D:\\test\\raster_output.tiff'

#####################################################

def cutByBBox (minX, maxX, minY, maxY):

    dataset = gdal.Open(raster)
    cols = dataset.RasterXSize
    rows = dataset.RasterYSize

    #################################################

    GCPs = dataset.GetGCPs()

    GCPX = []
    GCPY = []

    for a, val in enumerate(GCPs):
        GCPX.append(GCPs[a].GCPX)
        GCPY.append(GCPs[a].GCPY)

    geotransform = {'minX':min(GCPX), 'maxX':max(GCPX), 'minY':min(GCPY), 'maxY':max(GCPY)}

    #################################################

    geotransform = [geotransform['minX'], (geotransform['maxX']-geotransform['minX'])/cols, 0, geotransform['maxY'], 0, (geotransform['maxY']-geotransform['minY'])/rows*(-1)]

    error_threshold = 0.125
    resampling = gdal.GRA_NearestNeighbour
    dataset_middle = gdal.AutoCreateWarpedVRT(dataset, None, WKT_Projection, resampling, error_threshold)
    dataset = None
    
    #dataset_middle.SetGeoTransform(geotransform)
    #dataset_middle.SetProjection(WKT_Projection)
    #dataset_middle.SetGCPs(GCPs, WKT_Projection)

    c, a, b, f, d, e = dataset_middle.GetGeoTransform()

    def GetPixelCoords(col, row):
        xp = a * col + b * row + a * 0.5 + b * 0.5 + c
        yp = d * col + e * row + d * 0.5 + e * 0.5 + f
        return(xp, yp)

    band = dataset_middle.GetRasterBand(1)
    
    band = None

    print dataset_middle.GetGeoTransform()

    #################################################

    xOrigin = geotransform[0]
    yOrigin = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]

    

    i1 = int((minX - xOrigin) / pixelWidth)
    j1 = int((minY - yOrigin) / pixelHeight)
    i2 = int((maxX - xOrigin) / pixelWidth)
    j2 = int((maxY - yOrigin) / pixelHeight)

    new_cols = i2 - i1 + 1
    new_rows = j1 - j2 + 1

    

    data = dataset_middle.ReadAsArray(i2, j2, new_cols, new_rows)

    #################################################

    newGCPs = []
    diff = i2-i1

    i, j = GetPixelCoords(i2 + diff, j2)
    newGCPs.append(gdal.GCP(i, j, 0.0, new_cols-1, 0.0))                  #BR

    i, j = GetPixelCoords(i1 + diff, j2)
    newGCPs.append(gdal.GCP(i, j, 0.0, 0.0, 0.0))                         #UL

    i, j = GetPixelCoords(i1 + diff, j1)
    newGCPs.append(gdal.GCP(i, j, 0.0, 0.0, new_rows-1))                  #BL

    i, j = GetPixelCoords(i2 + diff, j1)
    newGCPs.append(gdal.GCP(i, j, 0.0, new_cols-1, new_rows-1))           #UR

    #################################################

    newX = xOrigin + i1 * pixelWidth
    newY = yOrigin + j2 * pixelHeight

    new_transform = (newX, pixelWidth, 0.0, newY, 0.0, pixelHeight)

    dst_ds = gdal.GetDriverByName('GTiff').Create(raster_output, new_cols, new_rows, bands = 1, eType = gdal.GDT_Byte)

    dst_ds.SetProjection(WKT_Projection)
    dst_ds.SetGCPs(newGCPs, WKT_Projection)
    #dst_ds.SetGeoTransform(new_transform)

    dst_ds.GetRasterBand(1).WriteArray(data)
    
    dst_ds = None
    dataset_middle = None

cutByBBox(18.30, 18.80, 54.30, 54.80)