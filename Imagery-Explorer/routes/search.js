'use strict';
var express = require('express');
var mysql = require('mysql');
var parse = require('wellknown')

var pool = mysql.createPool({
    connectionLimit: 2,
    host: 'localhost',
    user: 'root',
    database: 'products'
});

pool.getConnection(function (err, connection) {
    if (err) throw err;
    console.log('Connection ID: ' + connection.threadId);
});

var router = express.Router();

var http = require('http');

/* GET home page. */
router.get('/', function (req, res) {
    var orbitdirectionS2 = req.query.orbitdirectionS2;
    var relativeorbitnumberS2 = req.query.relativeorbitnumberS2;

    var isNotEmpty = true

    if (!req.query.dataod && !req.query.datado && !req.query.extent && (Object.keys(req.query).length == 4)) {
        isNotEmpty = false
    }
    //HERE
    if (req.query.satellite == 'S1') {
        var myQuery = 'SELECT ID, Ingestiondate, Satellite, Mode, Orbitdirection, Polarisationmode, Producttype, Relativeorbitnumber, Size, AsText(coordinates) AS bbox FROM s1 WHERE';
        var myQueryVariables = [];
        var count = false;

        if (req.query.dataod || req.query.datado) {
            if (count) {
                myQuery = myQuery + ' AND';
                count = false
            };
            myQuery = myQuery + ' (Ingestiondate BETWEEN ? AND ?)';
            myQueryVariables.push(req.query.dataod);
            myQueryVariables.push(req.query.datado);
            count = true;
        };
        if (req.query.polarisationmodeS1) {
            if (count) {
                myQuery = myQuery + ' AND';
                count = false
            };
            myQuery = myQuery + ' (Polarisationmode LIKE ?)';
            req.query.polarisation = '%' + req.query.polarisationmodeS1 + '%'
            myQueryVariables.push(req.query.polarisationmodeS1)
            count = true;
        };
        if (req.query.producttypeS1) {
            if (count) {
                myQuery = myQuery + ' AND';
                count = false
            };
            myQuery = myQuery + ' (Producttype = ?)';
            myQueryVariables.push(req.query.producttypeS1)
            count = true;
        };
        if (req.query.modeS1) {
            if (count) {
                myQuery = myQuery + ' AND';
                count = false
            };
            myQuery = myQuery + ' (Mode = ?)';
            myQueryVariables.push(req.query.modeS1)
            count = true;
        };
        if (req.query.extent) {
            if (count) {
                myQuery = myQuery + ' AND';
                count = false
            };
            myQuery = myQuery + ' (Overlaps(Coordinates, ST_GeomFromText(?)) OR Within(ST_GeomFromText(?), Coordinates) OR Within(Coordinates, ST_GeomFromText(?)))';
            myQueryVariables.push(req.query.extent)
            myQueryVariables.push(req.query.extent)
            myQueryVariables.push(req.query.extent)
            count = true;
        };
        if (req.query.orbitdirectionS1) {
            if (count) {
                myQuery = myQuery + ' AND';
                count = false
            };
            myQuery = myQuery + ' (Orbitdirection = ?)';
            myQueryVariables.push(req.query.orbitdirectionS1)
            count = true;
        };

        if (req.query.relativeorbitnumberS1) {
            if (count) {
                myQuery = myQuery + ' AND';
                count = false
            };
            myQuery = myQuery + ' (Relativeorbitnumber = ?)';
            myQueryVariables.push(req.query.relativeorbitnumberS1)
            count = true;
        };
        myQuery = myQuery + ' ORDER BY Ingestiondate DESC'
        /////////////////////////////////////////////////////////////////////// S2
    } else if (req.query.satellite == 'S2') {
        var myQueryS2 = 'SELECT ID, Ingestiondate, Satellite, Mode, Orbitdirection, Producttype, Relativeorbitnumber, Size, AsText(coordinates) AS bbox FROM s1 WHERE';
        var myQueryVariablesS2 = [];
        var count = false;

        if (req.query.dataod || req.query.datado) {
            if (count) {
                myQueryS2 = myQueryS2 + ' AND';
                count = false
            };
            myQueryS2 = myQueryS2 + ' (Ingestiondate BETWEEN ? AND ?)';
            myQueryVariablesS2.push(req.query.dataod);
            myQueryVariablesS2.push(req.query.datado);
            count = true;
        };
        if (req.query.orbitdirectionS2) {
            if (count) {
                myQueryS2 = myQueryS2 + ' AND';
                count = false
            };
            myQueryS2 = myQueryS2 + ' (Orbitdirection = ?)';
            myQueryVariablesS2.push(req.query.orbitdirectionS2)
            count = true;
        };
        if (req.query.relativeorbitnumberS2) {
            if (count) {
                myQueryS2 = myQueryS2 + ' AND';
                count = false
            };
            myQueryS2 = myQueryS2 + ' (Orbitdirection = ?)';
            myQueryVariablesS2.push(req.query.relativeorbitnumberS2)
            count = true;
        };
        if (req.query.extent) {
            if (count) {
                myQuery = myQuery + ' AND';
                count = false
            };
            myQuery = myQuery + ' (Overlaps(Coordinates, ST_GeomFromText(?)) OR Within(ST_GeomFromText(?), Coordinates) OR Within(Coordinates, ST_GeomFromText(?)))';
            myQueryVariables.push(req.query.extent)
            myQueryVariables.push(req.query.extent)
            myQueryVariables.push(req.query.extent)
            count = true;
        };
        myQuery2 = myQuery2 + ' ORDER BY Ingestiondate DESC'
    };

    if (isNotEmpty) {
        pool.getConnection(function (err, connection) {
            if (err) throw err;
            connection.query(myQuery, myQueryVariables, function (err, results, fields) {
                console.log('Query: ' + myQuery);

                var OSMCopyright = "{attribution: '&copy; OpenStreetMap contributors'}"//"{attribution: '&copy; <a href=" + '"http://openstreetmap.org\"' + ">OpenStreetMap</a> contributors'}"
                var mapScript = "var map = L.map('map').setView([52.07, 19.48], 6);\n L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', " + OSMCopyright + ").addTo(map); map.doubleClickZoom.disable();"
                if (results.length) {
                    for (var result in results) {
                        var polygonGeoJSON = parse(results[result].bbox)
                        var polygonParsed = '[' + '[' + polygonGeoJSON.coordinates[0][0][1] + ',' + polygonGeoJSON.coordinates[0][0][0] + '], ' + '[' + polygonGeoJSON.coordinates[0][1][1] + ',' + polygonGeoJSON.coordinates[0][1][0] + '], ' + '[' + polygonGeoJSON.coordinates[0][2][1] + ',' + polygonGeoJSON.coordinates[0][2][0] + '], ' + '[' + polygonGeoJSON.coordinates[0][3][1] + ',' + polygonGeoJSON.coordinates[0][3][0] + ']' + ']'
                        var polygonScriptS1 = "\n var polygon = L.polygon(" + polygonParsed + ", {color : '#000101', opacity : 0.8, className : '" + results[result].ID + "'}).addTo(map)" + '.bindPopup("<p>' + 'typ produktu: ' + results[result].Producttype + '<br>tryb sensora: ' + results[result].Mode + '<br>polaryzacja: ' + results[result].Polarisationmode + '<br>data i czas pozyskania: ' + results[result].Ingestiondate + '<br>satelita: ' + results[result].Satellite + '<br>pobierz ' + results[result].ID + '</p>")'
                        mapScript = mapScript + polygonScriptS1
                    }
                }
                res.render('search', { items: results, mapScript: mapScript, title: 'Wyniki wyszukiwania' });
                connection.release();
                console.log('Connection relased');
            });
        });
    } else {
        res.render('index', { error: 'Wprowadź kryteria wyszukiwania', title: 'Wyszukiwarka' });
    };
});

module.exports = router;