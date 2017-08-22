'use strict';
var express = require('express');
var router = express.Router();
//http?

var gdal = require("gdal");

router.get('/', function (req, res) {
    var extent = req.query.extent;
    var ID = req.query.ID;
    var filepath = "C:\\Users\\20274\\OneDrive\\Dokumenty\\Visual Studio 2017\\Projects\\Imagery-Explorer\\Imagery-Explorer\\public\\imagery\\s1\\" + ID + "\\measurement\\" + ID + "_vh.tiff"

    console.log(filepath);

    var image = gdal.open(filepath);

    console.log("number of bands: " + image.bands.count());
    console.log("width: " + image.rasterSize.x);
    console.log("height: " + image.rasterSize.y);
    console.log("geotransform: " + image.geoTransform);
    console.log("srs: " + (image.srs ? image.srs.toWKT() : 'null'));

    image.close();

    res.render('crop', {title: 'crop'});
});

module.exports = router;