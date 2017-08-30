import gdal
import rasterio

#####################################################
raster = 'D:\\test\\S1B_IW_GRDH_1SDV_20170101T045911_20170101T045940_003650_006425_45AB.SAFE\\measurement\\s1b-iw-grd-vh-20170101t045911-20170101t045940-003650-006425-002.tiff'

crs = rasterio.crs.CRS.from_epsg(4326)

raster_georef = 'D:\\test\\raster_georef.tiff'
raster_output = 'D:\\test\\raster_output.tiff'

#####################################################

def cutByBBox (minX, maxX, minY, maxY):

    dataset = rasterio.open(raster, mode = 'r+', crs = crs)

    GCPsX = []
    GCPsY = []

    for a, val in enumerate(dataset.gcps[0]):
        GCPsX.append(dataset.gcps[0][a].x)
        GCPsY.append(dataset.gcps[0][a].y)
        pass

    geotransform = {'minX':min(GCPsX), 'maxX':max(GCPsX), 'minY':min(GCPsY), 'maxY':max(GCPsY)}

    #####################################################
    dataset.set_crs(crs)

    transform = rasterio.warp.calculate_default_transform(src_crs = crs,
                                                          dst_crs = True,
                                                          width = dataset.width,
                                                          height = dataset.height,
                                                          gcps = dataset.get_gcps())

    pass
    

cutByBBox(18.30, 18.80, 54.30, 54.80)