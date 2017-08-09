'use strict';
var express = require('express');
var router = express.Router();

var http = require('http');
var MongoClient = require('mongodb').MongoClient;
var url = "mongodb://localhost:27017/db";

/* GET home page. */
router.get('/', function (req, res) {

    // TODO: get request handler
    // TODO: get records

    var datefrom = req.query.dataod;

    var dateto = req.query.datado;

    var satellite = req.query.satellite;

    var orbitdirectionS1 = req.query.orbitdirectionS1;
    var producttypeS1 = req.query.producttypeS1;
    var modeS1 = req.query.modeS1;
    var polarisationmodeS1 = req.query.polarisationmodeS1;
    var relativeorbitnumberS1 = req.query.relativeorbitnumberS1;

    var orbitdirectionS2 = req.query.orbitdirectionS2;
    var relativeorbitnumberS2 = req.query.relativeorbitnumberS2;

    var query = {};

    var dataspace = {};

    if (datefrom != '') {
        datefrom = 'ISODate(' + datefrom + 'T00:00:00.000Z)';
        dataspace['$gte'] = datefrom
        query['properties.ingestiondate'] = dataspace;
    };

    if (dateto != '') {
        dateto = 'ISODate(' + dateto + 'T23:59:59.999Z)';
        dataspace['$lt'] = dateto
        query['properties.ingestiondate'] = dataspace;
    };

    if (satellite == 'S1') {
        query['properties.satellite'] = new RegExp('S1')

        if (orbitdirectionS1 == 'ASCENDING') {
            query['properties.orbitdirection'] = 'ASCENDING'
        } else if (orbitdirectionS1 == 'DESCENDING') {
            query['properties.orbitdirection'] = 'DESCENDING'
        } else {
            //do nothing
        };

        if (producttypeS1 == 'GRD') {
            query['properties.producttype'] = 'GRD'
        } else if (producttypeS1 == 'SLC') {
            query['properties.producttype'] = 'SLC'
        } else if (producttypeS1 == 'RAW') {
            query['properties.producttype'] = 'RAW'
        } else {
            //do nothing
        };

        if (polarisationmodeS1 == 'VV') {
            query['properties.polarisationmode'] = new RegExp('VV')
        } else if (polarisationmodeS1 == 'HV') {
            query['properties.polarisationmode'] = new RegExp('HV')
        } else if (polarisationmodeS1 == 'VH') {
            query['properties.polarisationmode'] = new RegExp('VH')
        } else if (polarisationmodeS1 == 'HH') {
            query['properties.polarisationmode'] = new RegExp('HH')
        } else {
            //do nothing
        };

        if (modeS1 == 'IW') {
            query['properties.mode'] = 'IW'
        } else if (modeS1 == 'SM') {
            query['properties.mode'] = 'SM'
        } else if (modeS1 == 'EW') {
            query['properties.mode'] = 'EW'
        } else {
            //do nothing
        };

        if (relativeorbitnumberS1) {
            query['properties.relativeorbitnumber'] = relativeorbitnumberS1
        };

    } else if (satellite == 'S2') {
        query['properties.satellite'] = new RegExp('S2')

        if (orbitdirectionS2 == 'ASCENDING') {
            query['properties.orbitdirection'] = 'ASCENDING'
        } else if (orbitdirectionS2 == 'DESCENDING') {
            query['properties.orbitdirection'] = 'DESCENDING'
        } else {
            //do nothing
        };

        if (relativeorbitnumberS2) {
            query['properties.relativeorbitnumber'] = relativeorbitnumberS2
        };

    } else {
        query['$or'] = [{ 'properties.satellite': new RegExp('S1') }, { 'properties.satellite': new RegExp('S2') }]
        if (orbitdirectionS1 == 'ASCENDING') {
            query['$or'][0]['properties.orbitdirection'] = 'ASCENDING'
        } else if (orbitdirectionS1 == 'DESCENDING') {
            query['$or'][0]['properties.orbitdirection'] = 'DESCENDING'
        } else {
            //do nothing
        };

        if (producttypeS1 == 'GRD') {
            query['$or'][0]['properties.producttype'] = 'GRD'
        } else if (producttypeS1 == 'SLC') {
            query['$or'][0]['properties.producttype'] = 'SLC'
        } else if (producttypeS1 == 'RAW') {
            query['$or'][0]['properties.producttype'] = 'RAW'
        } else {
            //do nothing
        };

        if (polarisationmodeS1 == 'VV') {
            query['$or'][0]['properties.polarisationmode'] = new RegExp('VV')
        } else if (polarisationmodeS1 == 'HV') {
            query['$or'][0]['properties.polarisationmode'] = new RegExp('HV')
        } else if (polarisationmodeS1 == 'VH') {
            query['$or'][0]['properties.polarisationmode'] = new RegExp('VH')
        } else if (polarisationmodeS1 == 'HH') {
            query['$or'][0]['properties.polarisationmode'] = new RegExp('HH')
        } else {
            //do nothing
        };

        if (modeS1 == 'IW') {
            query['$or'][0]['properties.mode'] = 'IW'
        } else if (modeS1 == 'SM') {
            query['$or'][0]['properties.mode'] = 'SM'
        } else if (modeS1 == 'EW') {
            query['$or'][0]['properties.mode'] = 'EW'
        } else {
            //do nothing
        };

        if (relativeorbitnumberS1 != '') {
            query['$or'][0]['properties.relativeorbitnumber'] = relativeorbitnumberS1
        };

        if (orbitdirectionS2 == 'ASCENDING') {
            query['$or'][1]['properties.orbitdirection'] = 'ASCENDING'
        } else if (orbitdirectionS2 == 'DESCENDING') {
            query['$or'][1]['properties.orbitdirection'] = 'DESCENDING'
        } else {
            //do nothing
        };

        if (relativeorbitnumberS2 != '') {
            query['$or'][1]['properties.relativeorbitnumber'] = relativeorbitnumberS2
        };
    };

    

    console.log(query);

    MongoClient.connect(url, function (err, db) {
        if (err) throw err;
        db.collection("products").find(query).toArray(function (err, array) {
            if (err) throw err;
            res.render('search', { title: 'search', result: JSON.stringify(array)});
            db.close();
        });
    });

    
});

module.exports = router;
