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
    var query = {};

    if (satellite == 'S1') {
        query['$or'] = [{ 'properties.satellite': 'S1A' }, { 'properties.satellite': 'S1B' }]
    } else if (satellite == 'S2') {
        query['$or'] = [{ 'properties.satellite': 'S2A' }, { 'properties.satellite': 'S2B' }]
    } else {
        //do nothing
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
