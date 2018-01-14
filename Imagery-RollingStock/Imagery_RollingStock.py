import numpy
from osgeo import gdal, gdalnumeric, ogr, osr
from PIL import Image, ImageDraw

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 

# Raster image to clip
raster = "D:\\test\\shp_test\\L2A_T33UXR_20170928T100021_B03_10m_WGS84.jp2"
# Polygon shapefile used to clip
shp = "D:\\test\\shp_test\\PL"
# Name of clip raster file(s)
output = "D:\\test\\shp_test\\clip"
  
def imageToArray(i):
    """
    Converts a Python Imaging Library array to a 
    gdalnumeric image.
    """
    a=gdalnumeric.fromstring(i.tostring(),'b')
    a.shape=i.im.size[1], i.im.size[0]
    return a
def arrayToImage(a):
    """
    Converts a gdalnumeric array to a 
    Python Imaging Library Image.
    """
    i=Image.fromstring('L',(a.shape[1],a.shape[0]),
            (a.astype('b')).tostring())
    return i   
def world2Pixel(geoMatrix, x, y):
  """
  Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate
  the pixel location of a geospatial coordinate 
  """

  ulX = geoMatrix[0]
  ulY = geoMatrix[3]
  xDist = geoMatrix[1]
  yDist = geoMatrix[5]
  rtnX = geoMatrix[2]
  rtnY = geoMatrix[4]
  pixel = int((x - ulX) / xDist)
  line = int((y - ulY) / yDist)
  return (pixel, line) 
def getOffset(m):
    if not numpy.all(m[1]):
        topOffset = 0
    else:
        for i, v in enumerate(m):
            if numpy.all(v):
                topOffset = i
                #print i, v
    print "topOffset =", topOffset

    m = numpy.rot90(m)

    if not numpy.all(m[1]):
        rightOffset = 0
    else:
        for i, v in enumerate(m):
            if numpy.all(v):
                rightOffset = i
                #print i, v
    print "rightOffset =", rightOffset

    m = numpy.rot90(m)

    if not numpy.all(m[1]):
        bottomOffset = 0
    else:
        for i, v in enumerate(m):
            if numpy.all(v):
                bottomOffset = i
                #print i, v
    print "bottomOffset =", bottomOffset

    m = numpy.rot90(m)

    if not numpy.all(m[1]):
        leftOffset = 0
    else:
        for i, v in enumerate(m):
            if numpy.all(v):
                leftOffset = i
                #print i, v
    print "leftOffset =", leftOffset

    m = numpy.rot90(m)
    return topOffset, rightOffset, bottomOffset, leftOffset
def getGeometryExtent(points):
    ## Convert the layer extent to image pixel coordinates V2?
    minX = min(points, key=lambda x: x[0])[0]
    maxX = max(points, key=lambda x: x[0])[0]
    minY = min(points, key=lambda x: x[1])[1]
    maxY = max(points, key=lambda x: x[1])[1]
    return minX, maxX, minY, maxY

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 

srcArray = gdalnumeric.LoadFile(raster)
srcImage = gdal.Open(raster)
geoTrans = srcImage.GetGeoTransform()

sourceMinRasterX = geoTrans[0]
xPixelSize = geoTrans[1]
sourceMaxRasterY = geoTrans[3]
yPixelSize = geoTrans[5]

sourceRasterHeight = srcImage.RasterYSize
sourceRasterWidth = srcImage.RasterXSize

sourceMaxRasterX = sourceMinRasterX+(sourceRasterWidth*xPixelSize)
sourceMinRasterY = sourceMaxRasterY+(sourceRasterHeight*yPixelSize)

# Create an OGR layer from a boundary shapefile
shapefile = ogr.Open("%s.shp" % shp)
lyr = shapefile.GetLayer("PL")
poly = lyr.GetNextFeature()
cutterGeometry = poly.GetGeometryRef()


rasterWKT = "POLYGON ((%s %s, %s %s, %s %s, %s %s, %s %s))" % (str(sourceMinRasterX), str(sourceMaxRasterY), str(sourceMaxRasterX), str(sourceMaxRasterY), str(sourceMaxRasterX), str(sourceMinRasterY), str(sourceMinRasterX), str(sourceMinRasterY), str(sourceMinRasterX), str(sourceMaxRasterY))
rasterGeometry = ogr.CreateGeometryFromWkt(rasterWKT)

shapei = cutterGeometry.Intersection(rasterGeometry)

pts = shapei.GetGeometryRef(0)
points = []
for p in range(pts.GetPointCount()):
    points.append((pts.GetX(p), pts.GetY(p)))
minX, maxX, minY, maxY = getGeometryExtent(points)

# Convert the layer extent to image pixel coordinates
#minX, maxX, minY, maxY = lyr.GetExtent()
ulX, ulY = world2Pixel(geoTrans, minX, maxY)
lrX, lrY = world2Pixel(geoTrans, maxX, minY)

if (ulX <0):
    ulX = 0
if (ulY <0):
    ulY = 0
if (lrX > sourceRasterWidth):
    lrX = sourceRasterWidth
if (lrY > sourceRasterHeight):
    lrY = sourceRasterHeight

# Calculate the pixel size of the new image
pxWidth = int(lrX - ulX)
pxHeight = int(lrY - ulY)

#clip = srcArray[:, ulY:lrY, ulX:lrX]
clip = srcArray[ulY:lrY, ulX:lrX]

# Create a new geomatrix for the image
geoTrans = list(geoTrans)
geoTrans[0] = minX
geoTrans[3] = maxY
#geoTrans[0] = sourceMinRasterX
#geoTrans[3] = sourceMaxRasterY

# Map points to pixels for drawing the 
# boundary on a blank 8-bit, 
# black and white, mask image.
pixels = []

for p in points:
    pixels.append(world2Pixel(geoTrans, p[0], p[1]))

rasterPoly = Image.new("L", (pxWidth, pxHeight), 1)
rasterize = ImageDraw.Draw(rasterPoly)
rasterize.polygon(pixels, 0)
mask = imageToArray(rasterPoly) 

tOffset, rOffset, bOffset, lOffset = getOffset(mask)

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 

#mask = mask[ulY+topOffset:lrY-bottomOffset, ulX+leftOffset:lrX-rightOffset]
#clip = clip[ulY+topOffset:lrY-bottomOffset, ulX+leftOffset:lrX-rightOffset]

# Clip the image using the mask
clip = gdalnumeric.choose(mask, (clip, 0)).astype(gdalnumeric.uint16 )

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 

# Save ndvi as tiff
dst_filename = "%s.tif" % output
x_pixels = lrX - ulX  # number of pixels in x
y_pixels = lrY - ulY  # number of pixels in y
driver = gdal.GetDriverByName('GTiff')
#dataset = driver.Create(dst_filename,x_pixels, y_pixels, 1,gdal.GDT_Float32)
dataset = driver.Create(dst_filename,x_pixels, y_pixels, 1,gdal.GDT_UInt16)
dataset.GetRasterBand(1).WriteArray(clip)

# follow code is adding GeoTranform and Projection
#  #get GeoTranform from existed 'data0'

proj=srcImage.GetProjection() #you can get from a exsited tif or import 
dataset.SetGeoTransform(geoTrans)
dataset.SetProjection(proj)
dataset.FlushCache()
dataset=None

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

# Save ndvi as an 8-bit jpeg for an easy, quick preview
clip = clip.astype(gdalnumeric.uint8)
gdalnumeric.SaveArray(clip, "%s.jpg" % output, format="JPEG")