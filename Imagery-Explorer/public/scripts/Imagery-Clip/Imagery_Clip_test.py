import os, sys
import gdal
import requests
import zipfile, shutil
import json
import time

startTime = time.time()

order = '{"token":"6ewqnu0r","orderedTime":1506515962901,"completedTime":1506515963,"extent":{"minX":13.893173192627728,"maxX":14.189804052002726,"minY":50.897717175804516,"maxY":50.996352918763},"cart":[{"ID":"8b61bae7-d96d-4d7d-9d83-a653e2913ea4","title":"S1B_IW_GRDH_1SDV_20170102T165051_20170102T165116_003672_0064CF_5582","satellite":"S1B"}],"email":"example@example.com","status":"0"}'
#order = '{"token":"0aovfa1t","orderedTime":1506517319561,"completedTime":1506517320,"extent":{"minX":19.824142456054688,"maxX":20.131759643554688,"minY":50.00850024720049,"maxY":50.10724739511635},"cart":[{"ID":"939d3727-b5b9-4969-aa1f-aeedb79551df","title":"S1A_IW_GRDH_1SDV_20170110T163434_20170110T163459_014772_0180D5_91A3","satellite":"S1A"}],"email":"example@example.com","status":"0"}'
#order = '{"status": "1", "orderedTime": 1506408181116, "completedTime": 1506408631.142, "cart": [{"satellite": "S1A", "ID": "1ad1bbad-f624-4b21-ad7c-ac6377144f8e", "title": "S1A_IW_GRDH_1SDV_20170110T163459_20170110T163524_014772_0180D5_D774"}], "token": "b993ku02", "extent": {"minX": 16.8475341796875, "minY": 50.98043613046862, "maxX": 17.2265625, "maxY": 51.23565415168644}, "email": "example@example.com"}'
extractPath = 'D:\\test\\downloaded\\'
ordersPath = 'D:\\test\\orders\\'

############################

def printMessage(message, startTime):

    print message + ' ' +  str(time.time() - startTime)

def isDownloaded (title):
    if os.path.isfile(extractPath + title + '.zip'):
        return True
    else:
        return False

def downloadProduct (order, cartElement):
    url = "https://scihub.copernicus.eu/dhus/odata/v1/Products('" + cartElement['ID'] + "')/$value"                 #URL zobrazowania na serwerze ESA

    downloadPath = 'D:\\test\\downloaded\\' + cartElement['title'] + '.zip'                                         #Sciezka pobranego obrazu                                                                        #Folder w ktorym rozpakowywany jest pobrany obraz

    username = 'tprzybylek'
    password = 'pracainz2015'
    
    printMessage('Downloading product', startTime)
    r = requests.get(url, auth=(username, password), stream=True)                                                   #zadanie HTTP, pobranie pliku do pamieci
    if r.status_code == 200:
        with open(downloadPath, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)                                                                            #zapis odebranego pliku w downloadPath
            printMessage('Product downloaded', startTime)

    sys.stdout.flush()

def unzipProduct(title):
    printMessage('Extracting product', startTime)
    zip_ref = zipfile.ZipFile(extractPath + title + '.zip', 'r')
    zip_ref.extractall(extractPath)                                                                                 #wypakowanie obrazu do extractPath
    zip_ref.close()
    printMessage('Product extracted', startTime)

def zipOrder(token):
    folderPath = 'D:\\test\\orders\\' + token + '\\'
    outputPath = 'D:\\test\\orders\\' + token + '.zip'

    parentFolder = os.path.dirname(folderPath)

    contents = os.walk(folderPath)

    try:
        zipFile = zipfile.ZipFile(outputPath, 'w', zipfile.ZIP_DEFLATED)
        for root, folders, files in contents:
            for folderName in folders:
                absolutePath = os.path.join(root, folderName)
                relativePath = absolutePath.replace(parentFolder + '\\', '')
                zipFile.write(absolutePath,relativePath)

            for fileName in files:
                absolutePath = os.path.join(root, fileName)
                relativePath = absolutePath.replace(parentFolder + '\\', '')
                zipFile.write(absolutePath, relativePath)

        print "'%s' created succesfully." %outputPath
    except IOError, message:
        print message
        sys.exit(1)
    finally:
        zipFile.close()

def clipImages(token, extent, title, satellite):
    def clipImage(extent, sourceImagePath, outputImagePath):
        WKT_Projection = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
        
        dataset = gdal.Open(sourceImagePath)
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

        #################################################

        xOrigin = geotransform[0]
        yOrigin = geotransform[3]
        pixelWidth = geotransform[1]
        pixelHeight = geotransform[5]

        i1 = int((extent['minX'] - xOrigin) / pixelWidth)
        j1 = int((extent['minY'] - yOrigin) / pixelHeight)
        i2 = int((extent['maxX'] - xOrigin) / pixelWidth)
        j2 = int((extent['maxY'] - yOrigin) / pixelHeight)

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

        dst_ds = gdal.GetDriverByName('GTiff').Create(outputImagePath, new_cols, new_rows, bands = 1, eType = gdal.GDT_Byte)

        dst_ds.SetProjection(WKT_Projection)
        dst_ds.SetGCPs(newGCPs, WKT_Projection)

        dst_ds.GetRasterBand(1).WriteArray(data)
    
        dst_ds = None
        dataset_middle = None

############################

    if not os.path.exists(ordersPath + token + '\\' + title):
        os.makedirs(ordersPath + token + '\\' + title)
    
    if (satellite[:2] == 'S1'):
        printMessage('Clipping image', startTime)
        for image in os.listdir(extractPath + title + '.SAFE\\measurement\\'):
            if image.endswith('.tiff'):
                sourceImagePath = extractPath + title + '.SAFE\\measurement\\' + image
                outputImagePath = ordersPath + token + '\\' + title + '\\' + image
                clipImage(extent, sourceImagePath, outputImagePath)
        pass
    elif (satellite[:2] == 'S2'):
        printMessage('Sattelite not supported...yet', startTime)
    else:
        printMessage('Sattelite not supported', startTime)

############################

def main (order):  
    j = json.loads(order)

    for product in j['cart']:
        print product['title']

        if isDownloaded(product['title']):
            printMessage('Is downloaded', startTime)
        else:
            printMessage('Is not downloaded', startTime)
            downloadProduct(j, product)

        #unzipProduct(product['title'])

        clipImages(j['token'], j['extent'], product['title'], product['satellite'])

    #zipOrder(j['token'])

    #j['status']='1'
    #j['completedTime']=time.time()
    #ordersFilePath = 'C:\\Users\\20274\\OneDrive\\Dokumenty\\Visual Studio 2017\\Projects\\Imagery-Explorer\\Imagery-Explorer\\public\\orders.json'
    #with open(ordersFilePath, 'r+') as f:
    #    fJ = json.load(f)
    #    for n, i in enumerate(fJ):
    #        if i['token'] == j['token']:
    #           fJ[n] = j
    #    f.close()

    #with open(ordersFilePath, 'w') as f:
    #    json.dump(fJ, f)
    #    f.close()

    #printMessage('Deleting temporary files', startTime)

    #for product in j['cart']:
    #    shutil.rmtree(extractPath + product['title'] + '.SAFE')

    #shutil.rmtree(ordersPath + j['token'])


    print '------------------------------------------'
    printMessage('Total time in seconds', startTime)
    print '------------------------------------------'

############################

if __name__ == "__main__":
    #main(sys.argv[1])
    main(order)
###
