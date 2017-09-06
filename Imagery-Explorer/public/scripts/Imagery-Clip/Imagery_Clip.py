import os, sys
import requests
from osgeo import gdal
import zipfile, shutil

def cutByBBox (minX, maxX, minY, maxY, path, i, extractpath, title):
    WKT_Projection = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
    raster_output = extractpath + '\\' + title + '_clip\\' + 'raster_output_' + str(i) + '.tiff'

    dataset = gdal.Open(path)
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

    dst_ds.GetRasterBand(1).WriteArray(data)
    
    dst_ds = None
    dataset_middle = None

def zipFolder(folderPath, outputPath):
    parentFolder = os.path.dirname(folderPath)

    contents = os.walk(folderPath)

    try:

        zipFile = zipfile.ZipFile(outputPath, 'w', zipfile.ZIP_DEFLATED)
        for root, folders, files in contents:
            for folderName in folders:
                absolutePath = os.path.join(root, folderName)
                relativePath = absolutePath.replace(parentFolder + '\\', '')
                print 'Adding %s to archive.' % absolutePath
                zipFile.write(absolutePath,relativePath)

            for fileName in files:
                absolutePath = os.path.join(root, fileName)
                relativePath = absolutePath.replace(parentFolder + '\\', '')
                print 'Adding %s to archive.' % outputPath
                zipFile.write(absolutePath, relativePath)

        print "'%s' created succesfully." %outputPath
    except IOError, message:
        print message
        sys.exit(1)
    except IOError, message:
        print message
        sys.exit(1)
    except IOError, message:
        print message
        sys.exit(1)
    finally:
        zipFile.close()


def getProduct (id, title):
    url = "https://scihub.copernicus.eu/dhus/odata/v1/Products('" + id + "')/$value"

    filepath = 'D:\\test\\' + title + '.zip'
    extractpath = 'D:\\test\\'

    #if os.path.isdir(extractpath + id)

    #username = 'tprzybylek'
    #password = 'pracainz2015'
  
    #r = requests.get(url, auth=(username, password), stream=True)
    #if r.status_code == 200:
    #    with open(filepath, 'wb') as f:
    #        r.raw.decode_content = True
    #        shutil.copyfileobj(r.raw, f)

    #zip_ref = zipfile.ZipFile(filepath, 'r')
    #filename = zip_ref.filelist[0].filename
    #zip_ref.extractall(extractpath)
    #zip_ref.close()

    #i = 0

    #if not os.path.exists('D:\\test\\' + title + '_clip'):
    #    os.makedirs('D:\\test\\' + title + '_clip')

    #for image in os.listdir(extractpath + filename[:-1] + '\\measurement\\'):
    #    if image.endswith('.tiff'):
    #        imagepath = extractpath + filename[:-1] + '\\measurement\\' + image
    #        print imagepath

    #        cutByBBox(18.30, 18.80, 54.30, 54.80, imagepath, i, extractpath, title)
    #        i = i+1
    zipFolder(extractpath + title + '_clip', extractpath + title + '_clip.zip')

    f = open(extractpath + title + '_clip.zip', 'r')

    return f
    sys.stdout.flush()
    

#def main():
#    getProduct(sys.argv[0], sys.argv[1])

def main(id, title):
    getProduct(id, title)

if __name__ == "__main__":
    main('d31b76a6-7894-42ed-9bf1-871f73fba2eb', 'S1B_IW_GRDH_1SDV_20170101T045911_20170101T045940_003650_006425_45AB')