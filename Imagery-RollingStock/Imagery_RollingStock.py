import numpy
from osgeo import gdal, gdalnumeric, ogr, osr
from PIL import Image, ImageDraw

# Raster image to clip
raster = "D:\\test\\shp_test\\L2A_T33UXR_20170928T100021_B03_10m_WGS84.jp2"
# Polygon shapefile used to clip
shp = "D:\\test\\shp_test\\PL"

# Name of clip raster file(s)
output = "D:\\test\\shp_test\\clip"

# This function will convert the rasterized clipper shapefile 
# to a mask for use within GDAL.    
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

# Load the source data as a gdalnumeric array
srcArray = gdalnumeric.LoadFile(raster)

# Also load as a gdal image to get geotransform (world file) info
srcImage = gdal.Open(raster)
geoTrans = srcImage.GetGeoTransform()

minRasterX = geoTrans[0]
xPixelSize = geoTrans[1]
maxRasterY = geoTrans[3]
yPixelSize = geoTrans[5]

rasterHeight = srcImage.RasterYSize
rasterWidth = srcImage.RasterXSize

maxRasterX = minRasterX+(rasterWidth*xPixelSize)
minRasterY= maxRasterY+(rasterHeight*yPixelSize)

# Create an OGR layer from a boundary shapefile
shapef = ogr.Open("%s.shp" % shp)
shaperWKT = "POLYGON ((%s %s, %s %s, %s %s, %s %s, %s %s))" % (str(minRasterX), str(maxRasterY), str(maxRasterX), str(maxRasterY), str(maxRasterX), str(minRasterY), str(minRasterX), str(minRasterY), str(minRasterX), str(maxRasterY))

shaper = ogr.CreateGeometryFromWkt(shaperWKT)

lyr = shapef.GetLayer("PL")
poly = lyr.GetNextFeature()
geom = poly.GetGeometryRef()

shapei = geom.Intersection(shaper)

# Convert the layer extent to image pixel coordinates
minX, maxX, minY, maxY = lyr.GetExtent()
ulX, ulY = world2Pixel(geoTrans, minX, maxY)
lrX, lrY = world2Pixel(geoTrans, maxX, minY)

if (ulX <0):
    ulX = 0
if (ulY <0):
    ulY = 0
if (lrX > rasterWidth):
    lrX = rasterWidth
if (lrY > rasterHeight):
    lrY = rasterHeight

# Calculate the pixel size of the new image
pxWidth = int(lrX - ulX)
pxHeight = int(lrY - ulY)

clip = srcArray[ulY:lrY, ulX:lrX]

# Create a new geomatrix for the image
geoTrans = list(geoTrans)
#geoTrans[0] = minX
#geoTrans[3] = maxY

geoTrans[0] = minRasterX
geoTrans[3] = maxRasterY

# Map points to pixels for drawing the 
# boundary on a blank 8-bit, 
# black and white, mask image.
points = []
pixels = []

pts = shapei.GetGeometryRef(0)

for p in range(pts.GetPointCount()):
    points.append((pts.GetX(p), pts.GetY(p)))

for p in points:
    pixels.append(world2Pixel(geoTrans, p[0], p[1]))

rasterPoly = Image.new("L", (pxWidth, pxHeight), 1)
rasterize = ImageDraw.Draw(rasterPoly)
rasterize.polygon(pixels, 0)
mask = imageToArray(rasterPoly)

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 

if not numpy.all(mask[1]):
    topOffset = 0
else:
    for i, v in enumerate(mask):
        if numpy.all(v):
            topOffset = i
            #print i, v
print "topOffset =", topOffset

mask = numpy.rot90(mask)

if not numpy.all(mask[1]):
    rightOffset = 0
else:
    for i, v in enumerate(mask):
        if numpy.all(v):
            rightOffset = i
            #print i, v
print "rightOffset =", rightOffset

mask = numpy.rot90(mask)

if not numpy.all(mask[1]):
    bottomOffset = 0
else:
    for i, v in enumerate(mask):
        if numpy.all(v):
            bottomOffset = i
            #print i, v
print "bottomOffset =", bottomOffset

mask = numpy.rot90(mask)

if not numpy.all(mask[1]):
    leftOffset = 0
else:
    for i, v in enumerate(mask):
        if numpy.all(v):
            leftOffset = i
            #print i, v
print "leftOffset =", leftOffset

mask = numpy.rot90(mask)

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 

#mask = mask[ulY+topOffset:lrY-bottomOffset, ulX+leftOffset:lrX-rightOffset]
#clip = clip[ulY+topOffset:lrY-bottomOffset, ulX+leftOffset:lrX-rightOffset]

# Clip the image using the mask
clip = gdalnumeric.choose(mask, (clip, 0)).astype(gdalnumeric.uint16 )

# Save ndvi as tiff
gdalnumeric.SaveArray(clip, "%s.tif" % output, \
    format="GTiff", prototype=raster)

# Save ndvi as an 8-bit jpeg for an easy, quick preview
clip = clip.astype(gdalnumeric.uint8)
gdalnumeric.SaveArray(clip, "%s.jpg" % output, format="JPEG")