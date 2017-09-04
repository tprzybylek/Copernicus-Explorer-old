import xml.etree.ElementTree
import requests
from datetime import datetime
from datetime import timedelta
import mysql.connector
import time #UNUSED

for mal in range(50):
    #########################################

    def getXML (url, username, password):
        username = 'tprzybylek'
        password = 'pracainz2015'

        r = requests.get(url, auth=(username, password))  
        e = xml.etree.ElementTree.fromstring(r.content)
        return e

    def openXML (filename):
        e = xml.etree.ElementTree.parse(filename + '.xml').getroot()
        return e

    def getLastUpdate ():
        f = open('log.txt', 'r') 
        log = f.readlines()
        lastLine = log[-1]

        lastUpdateTime = datetime.strptime(lastLine[:23], '%Y-%m-%d %H:%M:%S.%f')
        lastUpdateStatus = lastLine[-3:]
        lastUpdateTimeDifference = datetime.now() - lastUpdateTime
        f.close()

        return {'lastUpdateTime':lastUpdateTime, 'lastUpdateStatus':lastUpdateStatus, 'lastUpdateTimeDifference': (lastUpdateTimeDifference.microseconds + (lastUpdateTimeDifference.seconds + lastUpdateTimeDifference.days * 24 * 3600) * 10**6) / 10**6}

    def writeUpdateTime (status):
        f = open('log.txt', 'a')
        global last_product_time
        last_product_time = last_product_time + timedelta(milliseconds = 1)
        f.write(last_product_time.__format__('%Y-%m-%d %H:%M:%S.%f') + ' ' + status + '\n')
        f.close()

    def WKT_to_GeoJSON (wkt):
        #UNUSED
        wkt = wkt.replace('((', ' ')
        wkt = wkt.replace('))', ' ')
        wkt = wkt.replace(',', ' ')

        words = wkt.split()[1:]
        n = [[float(words[x:x+2][0]), float(words[x:x+2][1])] for x in range(0, len(words), 2)]
        GeoJSON = [n]
        return GeoJSON

    def Size_to_Bytes(size):
        if size[-2:] == 'GB':
            return str(int((float(size[:-3]) * (10**9))))
        elif size[-2:] == 'MB':
            return str(int((float(size[:-3]) * (10**6))))
        else:
           return null

    def getProduct(entry):
        for attribute in entry:
                if (attribute.tag == namespace + 'title'):
                    satellite = attribute.text[:3]
                    product['title'] = attribute.text
                    product['satellite'] = satellite
                elif (attribute.tag == namespace + 'id'):
                    product['id'] = attribute.text
                elif (attribute.attrib and ('name' in attribute.attrib)):
                    if attribute.attrib['name'] == 'instrumentshortname':
                        product['instrument'] = attribute.text
                    elif attribute.attrib['name'] == 'sensoroperationalmode':
                        product['mode'] = attribute.text
                    elif attribute.attrib['name'] == 'ingestiondate':
                        try:
                            product['ingestiondate'] = datetime.strptime(attribute.text, '%Y-%m-%dT%H:%M:%S.%fZ')
                        except ValueError:
                            product['ingestiondate'] = datetime.strptime(attribute.text, '%Y-%m-%dT%H:%M:%SZ')
                    
                    elif attribute.attrib['name'] == 'footprint':
                        feature['geometry']['coordinates'] = attribute.text
                    elif attribute.attrib['name'] == 'orbitnumber':
                        product['orbitnumber'] = attribute.text
                    elif attribute.attrib['name'] == 'relativeorbitnumber':
                        product['relativeorbitnumber'] = attribute.text
                    elif attribute.attrib['name'] == 'orbitdirection':
                        product['orbitdirection'] = attribute.text
                    elif attribute.attrib['name'] == 'size':
                        product['size'] = attribute.text
                    elif (attribute.attrib['name'] == 'producttype'):
                        product['producttype'] = attribute.text
                    elif (attribute.attrib['name'] == 'polarisationmode' and satellite[:2] == 'S1'):
                        product['polarisationmode'] = attribute.text
                    elif (attribute.attrib['name'] == 'productclass' and satellite[:2] == 'S1'):
                        product['productclass'] = attribute.text
                    elif (attribute.attrib['name'] == 'cloudcoverpercentage' and satellite[:2] == 'S2'):
                        product['cloudcoverpercentage'] = attribute.text
                    elif (attribute.attrib['name'] == 'processingbaseline' and satellite[:2] == 'S2'):
                        product['processingbaseline'] = attribute.text
                    elif (attribute.attrib['name'] == 'processinglevel' and satellite[:2] == 'S2'):
                        product['processinglevel'] = attribute.text
        return product

    def BuildQuery(satellite):
        if (satellite[:2] == 'S1'):
            SQLquery = "INSERT INTO `s1`(`ID`, `Ingestiondate`, `Satellite`, `Mode`, `Orbitdirection`, `Polarisationmode`, `Producttype`, `Relativeorbitnumber`, `Size`, `Coordinates`) VALUES ("
            SQLquery += "'" + feature['properties']['id'] + "', "
            SQLquery += "'" + feature['properties']['ingestiondate'] + "', "
            SQLquery += "'" + feature['properties']['satellite'] + "', "
            SQLquery += "'" + feature['properties']['mode'] + "', "
            SQLquery += "'" + feature['properties']['orbitdirection'] + "', "
            SQLquery += "'" + feature['properties']['polarisationmode'] + "', "
            SQLquery += "'" + feature['properties']['producttype'] + "', "
            SQLquery += feature['properties']['relativeorbitnumber'] + ", "
            SQLquery += Size_to_Bytes(feature['properties']['size']) + ", "
            SQLquery += "ST_PolyFromText('" + feature['geometry']['coordinates'] + "')"
            SQLquery += ")"
        else:
            SQLquery = "INSERT INTO `s2`(`ID`, `Ingestiondate`, `Satellite`, `Mode`, `Cloudcover`, `Orbitdirection`, `Producttype`, `Relativeorbitnumber`, `Size`, `Coordinates`) VALUES ("
            SQLquery += "'" + feature['properties']['id'] + "', "
            SQLquery += "'" + feature['properties']['ingestiondate'] + "', "
            SQLquery += "'" + feature['properties']['satellite'] + "', "
            SQLquery += "'" + feature['properties']['mode'] + "', "
            SQLquery += feature['properties']['cloudcoverpercentage'] + ", "
            SQLquery += "'" + feature['properties']['orbitdirection'] + "', "
            SQLquery += "'" + feature['properties']['producttype'] + "', "
            SQLquery += feature['properties']['relativeorbitnumber'] + ", "
            SQLquery += Size_to_Bytes(feature['properties']['size']) + ", "
            SQLquery += "ST_PolyFromText('" + feature['geometry']['coordinates'] + "')"
            SQLquery += ")"
        return SQLquery

    #########################################

    lastUpdate = getLastUpdate()

    if lastUpdate['lastUpdateTimeDifference'] > 3600*6:

        queryURI = 'https://scihub.copernicus.eu/apihub/search?q=ingestiondate:[' + lastUpdate['lastUpdateTime'].isoformat() + 'Z%20TO%20NOW]%20AND%20footprint:%22Intersects(POLYGON((14.17%2054.14,18.19%2055.00,23.69%2054.35,24.26%2050.50,23.00%20 49.00,19.00%20 49.18,14.68%2050.73,14.02%2052.84,14.17%2054.14)))%22&orderby=ingestiondate%20asc&rows=100'
    #    queryURI = 'https://scihub.copernicus.eu/apihub/search?q=ingestiondate:[' + lastUpdate['lastUpdateTime'].isoformat() + 'Z%20TO%20NOW]%20AND%20footprint:%22Intersects(POLYGON((14.05%2054.89,24.23%2054.89,24.23%2048.95,14.05%2048.95,14.05%2048.95,14.05%2054.89)))%22&orderby=ingestiondate%20asc&rows=100'

        print queryURI

        xmldoc = getXML(queryURI, 'tprzybylek', 'pracainz2015')
    
        #DEBUG
        #xmldoc = openXML('search')

    #########################################
        cnx = mysql.connector.connect(user='root', database='products')
        cursor = cnx.cursor()

    #########################################
        namespace = '{http://www.w3.org/2005/Atom}'

        for entry in xmldoc.iter(tag = namespace + 'entry'):
            product = {}
            feature = {}
            feature['type'] = 'Feature'
            feature['geometry'] = {'type' : 'Polygon', 'coordinates' : ''}

            product = getProduct(entry)
            last_product_time = product['ingestiondate']

            product['ingestiondate'] = product['ingestiondate'].__format__('%Y-%m-%d %H:%M:%S.%f')

            feature['properties'] = product

            print BuildQuery(feature['properties']['satellite'])
            cursor.execute(BuildQuery(feature['properties']['satellite']))
        
        cnx.commit()
        writeUpdateTime('200')
        cursor.close()
        cnx.close()

    else:
        print('Wait')
    #########################################
    time.sleep(15)
