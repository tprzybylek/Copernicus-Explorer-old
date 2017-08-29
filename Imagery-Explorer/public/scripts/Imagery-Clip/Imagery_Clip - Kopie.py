import zipfile, requests
from osgeo import gdal, gdalnumeric, ogr, osr
import os, sys
from PIL import Image, ImageDraw
#####################################################

def getImageZIP (url):
    username = 'tprzybylek'
    password = 'pracainz2015'

    f = requests.get(url, auth=(username, password))
    return f

def openImageZIP (path):
    z = zipfile.ZipFile(path, 'r')
    #filename = z.filename[3:-4] + '.SAFE'
    #f = z.read(filename)
    return z

def imageToArray(i):
    a = gdalnumeric.fromstring(i.tostring(), 'b')
    a.shape = i.im.size[1], i.im.size[0]
    return a

def arrayToImage(a):
    i = Image.fromstring('L', (a.shape[1], a.shape[0]), (a.astype('b')).tostring())
    return i

def world2Pixel(geoMatrix, x, y):
    ulX = geoMatrix[0]
    ulY = geoMatrix[3]
    xDist = geoMatrix[1]
    yDist = geoMatrix[5]
    rtnX = geoMatrix[2]
    rtnY = geoMatrix [4]
    pixel = int ((x- ulx) / xDist)
    line = int ((ulY - y) / xDist)
    return (pixel, line)

def openArray(array, prototype_ds = None, xoff = 0, yoff = 0):
    ds = gdal.Open(gdalnumeric.GetArrayFilename(array))

    if ds is not None and prototype_ds is not None:
        if type(prototype_ds).__name__ == 'str':
            prototype_ds = gdal.Open( prototype_ds)
        if prototype_ds is not None:
            gdalnumeric.CopyDatasetInfo( prototype_ds, ds, xoff = xoff, yoff = yoff)
    return ds

#####################################################

#ID = 'd31b76a6-7894-42ed-9bf1-871f73fba2eb'
#url = "https://scihub.copernicus.eu/dhus/odata/v1/Products('" + ID + "')/$value"

#path = 'D:\S1B_IW_GRDH_1SDV_20170101T045911_20170101T045940_003650_006425_45AB.SAFE'

#extent = '{ "type": "Feature", "properties": {}, "geometry": { "type": "Polygon", "coordinates": [ [ [ 18.499603271484375, 54.262015759179484 ], [ 18.851165771484375, 54.262015759179484 ], [ 18.851165771484375, 54.446887364029756 ], [ 18.499603271484375, 54.446887364029756 ], [ 18.499603271484375, 54.262015759179484 ] ] ] } }'

#z = gdal.Open(path, gdal.GA_ReadOnly)

#####################################################

def main (shapefile_path, raster_path):
    srcArray = gdalnumeric.LoadFile(raster_path)

    srcImage = gdal.Open(raster_path)
    geoTrans = srcImage.GetGeoTransform()

    shapef = ogr.Open(shapefile_path)
    lyr = shapef.GetLayer( os.path.split(os.path.splitext(shapefile_path)[0])[1])
    poly = lyr.GetNextFeature()

    minX, maxX, minY, maxY = lyr.GetExtent()
    ulX, ulY = world2Pixel(geoTrans, minX, maxY)
    lrX, lrY = world2Pixel(geoTrans, maxX, minY)

    pxWidth = int(lrX - ulX)
    pxHeight = int(lrY - ulY)

    clip = srcArray[:, ulY:lrY, ulX:lrX]

    xoffset = ulX
    yoffset = ulY
    print "Xoffset, Yoffset = ( %f, %f)" % (xoffset, yoffset)

    geoTrans = list(geoTrans)
    geoTrans[0] = minX
    geoTrans[3] = maxY

    points = []
    pixels = []
    geom = poly.GetGeometryRef()
    pts = geom.getGeometryRef(0)

    for p in range(pts.GetPointCount()):
        points.append((pts.GetX(p), pts.GetY(p)))

    for p in points:
        pixels.append(world2Pixel(geoTrans, p[0], p[1]))

    rasterPoly = Image.new("L", (pxWidth, pxHeight), 1)
    rasterize = ImageDraw.Draw(rasterPoly)
    rasterize.polygon(pixels, 0)
    mask = imageToArray(rasterPoly)

    clip = gdalnumeric.choose(mask, (clip, 0)).astype(gdalnumeric.uint8)

    gtiffDriver = gdal.GetDriverByName('GTiff')
    if gtiffDriver is None:
        raise ValueError('Can not find GeoTiff Driver')
    gtiffDriver.CreateCopy('OUTPUT.tif', openArray(clip, prototype_ds=raster_path, xoff=xoffset, yoff=yoffset))

    clip = clip.astype(gdalnumeric.uint8)
    gdalnumeric.SaveArray(clip, 'OUTPUT.jpg', format = 'JPEG')

#####################################################

raster = 'D:\\test\\S1B_IW_GRDH_1SDV_20170101T045911_20170101T045940_003650_006425_45AB.SAFE\\measurement\\s1b-iw-grd-vh-20170101t045911-20170101t045940-003650-006425-002.tiff'
cut = 'D:\\test\\shape.shp'

main(cut, raster)

