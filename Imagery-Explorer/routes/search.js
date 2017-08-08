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

    var satellite = req.query.satellite;
    var orbitdirection = req.query.orbitdirection;
    var producttype = req.query.producttype;
    var mode = req.query.mode;
    var polarisationmode = req.query.polarisationmode;
    var relativeorbitnumber = req.query.relativeorbitnumber;

    var query = {};

    if (satellite == 'S1') {
        query['$or'] = [{ 'properties.satellite': 'S1A' }, { 'properties.satellite': 'S1B' }]
    } else if (satellite == 'S2') {
        query['$or'] = [{ 'properties.satellite': 'S2A' }, { 'properties.satellite': 'S2B' }]
    } else {
        //do nothing
    };

    if (orbitdirection == 'ASCENDING') {
        query['properties.orbitdirection'] = 'ASCENDING'
    } else if (orbitdirection == 'DESCENDING') {
        query['properties.orbitdirection'] = 'DESCENDING'
    } else {
        //do nothing
    };

    if (producttype == 'GRD') {
        query['properties.producttype'] = 'GRD'
    } else if (producttype == 'SLC') {
        query['properties.producttype'] = 'SLC'
    } else if (producttype == 'RAW') {
        query['properties.producttype'] = 'RAW'
    } else {
        //do nothing
    };

    if (polarisationmode == 'VV') {
        query['properties.polarisationmode'] = new RegExp('VV')
    } else if (polarisationmode == 'HV') {
        query['properties.polarisationmode'] = new RegExp('HV')
    } else if (polarisationmode == 'VH') {
        query['properties.polarisationmode'] = new RegExp('VH')
    } else if (polarisationmode == 'HH') {
        query['properties.polarisationmode'] = new RegExp('HH')
    } else {
        //do nothing
    };

    if (mode == 'IW') {
        query['properties.mode'] = 'IW'
    } else if (mode == 'SM') {
        query['properties.mode'] = 'SM'
    } else if (mode == 'EW') {
        query['properties.mode'] = 'EW'
    } else {
        //do nothing
    };
 
    if (relativeorbitnumber) {
        query['properties.relativeorbitnumber'] = relativeorbitnumber
    }

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
