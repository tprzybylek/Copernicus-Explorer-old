from osgeo import gdal, gdalnumeric, ogr, osr, gdal_array
from PIL import Image, ImageDraw
import os, sys
gdal.UseExceptions()

def imageToArray(i):

    a=gdalnumeric.fromstring(i.tostring(),'b')
    a.shape=i.im.size[1], i.im.size[0]
    return a

def arrayToImage(a):
   
    i=Image.fromstring('L',(a.shape[1],a.shape[0]),
            (a.astype('b')).tostring())
    return i

def world2Pixel(geoMatrix, x, y):

  ulX = geoMatrix[0]
  ulY = geoMatrix[3]
  xDist = geoMatrix[1]
  yDist = geoMatrix[5]
  rtnX = geoMatrix[2]
  rtnY = geoMatrix[4]
  pixel = int((x - ulX) / xDist)
  line = int((ulY - y) / xDist)
  return (pixel, line)

def OpenArray( array, prototype_ds = None, xoff=0, yoff=0 ):
    #use gdal_array.OpenArray()
    #ds = gdal.Open( gdalnumeric.GetArrayFilename(array) )
    ds = gdal_array.OpenArray(array)

    if ds is not None and prototype_ds is not None:
        if type(prototype_ds).__name__ == 'str':
            prototype_ds = gdal.Open( prototype_ds )
        if prototype_ds is not None:
            gdalnumeric.CopyDatasetInfo( prototype_ds, ds, xoff=xoff, yoff=yoff )
    return ds

def main( shapefile_path, raster_path ):

    shapef = ogr.Open(shapefile_path)                                                           #otwiera *.shp z konturem
    lyr = shapef.GetLayer( os.path.split( os.path.splitext( shapefile_path )[0] )[1] )

    feature = lyr.GetNextFeature()                                                              #wybiera obiekt w pliku *.shp
    geom = feature.GetGeometryRef()
    
    #wktShapef = geom.GetSpatialReference()
    #print wktShapef

    #raster_warped = 'D:\\test\\downloaded\\S2A_MSIL2A_20170928T100021_N0205_R122_T33UXR_20170928T100617.SAFE\\GRANULE\\L2A_T33UXR_A011845_20170928T100617\\IMG_DATA\\R10m\\L2A_T33UXR_20170928T100021_B03_10m_WGS84.jp2'
    raster_warped = 'D:\\test\\shp_test\\input_raster_WGS84.tif'

    ################################################################################
    srcImage = gdal.Open(raster_path)                                                           #otwiera raster do przyciecia, uklad wejsciowy
    gdal.Warp(raster_warped, srcImage, dstSRS='EPSG:4326')                                      #konwertuje raster na układ WGS84
    srcImage = None                                                                             #zamyka raster w ukladzie wejsciowym
    ################################################################################

    srcImage = gdal.Open(raster_warped)                                                         #otwiera raster w ukladzie wyjsciowym (WGS84)
    srcArray = gdalnumeric.LoadFile(raster_warped)
    geoTrans = srcImage.GetGeoTransform()
    
    #wktImage = srcImage.GetProjection()
    #print wktImage

    ################################################################################

    minX, maxX, minY, maxY = lyr.GetExtent()                            #zasieg *.shp
    ulX, ulY = world2Pixel(geoTrans, minX, maxY)
    lrX, lrY = world2Pixel(geoTrans, maxX, minY)
    

    pxWidth = int(lrX - ulX)
    pxHeight = int(lrY - ulY)

    clip = srcArray[ulY:lrY, ulX:lrX]

    xoffset =  ulX
    yoffset =  ulY

    print "Xoffset, Yoffset = ( %f, %f )" % ( xoffset, yoffset )

    geoTrans = list(geoTrans)
    geoTrans[0] = minX
    geoTrans[3] = maxY

    points = []
    pixels = []


    pts = geom.GetGeometryRef(0)
    for p in range(pts.GetPointCount()):
      points.append((pts.GetX(p), pts.GetY(p)))
    for p in points:
      pixels.append(world2Pixel(geoTrans, p[0], p[1]))
    rasterPoly = Image.new("L", (pxWidth, pxHeight), 1)
    rasterize = ImageDraw.Draw(rasterPoly)
    rasterize.polygon(pixels, 0)
    mask = imageToArray(rasterPoly)



    clip = gdalnumeric.numpy.choose(mask, (clip, 0)).astype(gdalnumeric.uint8)



    gtiffDriver = gdal.GetDriverByName( 'GTiff' )
    if gtiffDriver is None:
        raise ValueError("Can't find GeoTiff Driver")
    gtiffDriver.CreateCopy( "OUTPUT.tif", OpenArray( clip, prototype_ds=raster_path, xoff=xoffset, yoff=yoffset ))
    gdal.ErrorReset()


if __name__ == '__main__':
    #if len( sys.argv ) < 2:
    #   print "[ ERROR ] you must two args. 1) the full shapefile path and 2) the full raster path"
    #   sys.exit( 1 )

    #EPSG:32633

    #Clipping_SHP = 'D:\\test\\shp_test\\PL_simple.shp'
    Clipping_SHP = 'D:\\test\\shp_test\\PL_clip.shp'
    #Clipped_TIFF = 'D:\\test\\downloaded\\S2A_MSIL2A_20170928T100021_N0205_R122_T33UXR_20170928T100617.SAFE\\GRANULE\\L2A_T33UXR_A011845_20170928T100617\\IMG_DATA\\R10m\\L2A_T33UXR_20170928T100021_B03_10m.jp2'
    Clipped_TIFF = 'D:\\test\\shp_test\\input_raster.tif'

    main(Clipping_SHP, Clipped_TIFF)
    #main( sys.argv[1], sys.argv[2] )