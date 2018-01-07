function JSONtoWKT(extent){
    var wkt = 'POLYGON(('
    wkt = wkt + extent['minX'] + ' ' + extent['maxY'] + ',' + extent['maxX'] + ' ' + extent['maxY'] + ',' + extent['maxX'] + ' ' + extent['minY'] + ',' + extent['minX'] + ' ' + extent['minY'] + ',' + extent['minX'] + ' ' + extent['maxY'] + '))'
    return wkt
};