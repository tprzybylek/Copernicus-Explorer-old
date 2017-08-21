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
    var isNotEmpty = true
    if (!req.query.dataod && !req.query.datado && !req.query.extent && (Object.keys(req.query).length == 4)) {
        isNotEmpty = false
    }

////////////////////////////////////////////////////////////////////////////////////////////////////

    var Render = function (resultsS1, polygonScriptS1, resultsS2, polygonScriptS2) {
        //render website

        console.log('got data resultsS1 160: ' + resultsS1);
        console.log('got data mapScript 162: ' + polygonScriptS1);
        console.log('got data resultsS2 161: ' + resultsS2);
        console.log('got data mapScript 162: ' + polygonScriptS2);

        var OSMCopyright = "{attribution: '&copy; OpenStreetMap contributors'}"//"{attribution: '&copy; <a href=" + '"http://openstreetmap.org\"' + ">OpenStreetMap</a> contributors'}"
        var mapHeader = "var map = L.map('map').setView([52.07, 19.48], 6);\n L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', " + OSMCopyright + ").addTo(map); map.doubleClickZoom.disable();"

        var mapScript = '';

        if (polygonScriptS1) {
            mapScript = mapHeader + polygonScriptS1;
        };

        if (polygonScriptS2) {
            mapScript = mapHeader + polygonScriptS2;
        };

        res.render('search', { items: resultsS1, mapScript: mapScript, title: 'Wyniki wyszukiwania' });

    };

    var Query = function (callback) {

        var BuildQuery = function (callback) {
            //build two queries

            //var myQueryS1 = 'myQueryS1';
            //var myQueryS2 = 'myQueryS2';

            /////////////////////////////////////////////////////////////////////// S1
            if (req.query.satellite == 'S1') {
                var myQueryS1 = 'SELECT ID, Ingestiondate, Satellite, Mode, Orbitdirection, Polarisationmode, Producttype, Relativeorbitnumber, Size, AsText(coordinates) AS bbox FROM s1 WHERE';
                var myQueryVariablesS1 = [];
                var count = false;

                if (req.query.dataod || req.query.datado) {
                    if (count) {
                        myQueryS1 = myQueryS1 + ' AND';
                        count = false
                    };
                    myQueryS1 = myQueryS1 + ' (Ingestiondate BETWEEN ? AND ?)';
                    myQueryVariablesS1.push(req.query.dataod);
                    myQueryVariablesS1.push(req.query.datado);
                    count = true;
                };
                if (req.query.polarisationmodeS1) {
                    if (count) {
                        myQueryS1 = myQueryS1 + ' AND';
                        count = false
                    };
                    myQueryS1 = myQueryS1 + ' (Polarisationmode LIKE ?)';
                    req.query.polarisation = '%' + req.query.polarisationmodeS1 + '%'
                    myQueryVariablesS1.push(req.query.polarisationmodeS1)
                    count = true;
                };
                if (req.query.producttypeS1) {
                    if (count) {
                        myQueryS1 = myQueryS1 + ' AND';
                        count = false
                    };
                    myQueryS1 = myQueryS1 + ' (Producttype = ?)';
                    myQueryVariablesS1.push(req.query.producttypeS1)
                    count = true;
                };
                if (req.query.modeS1) {
                    if (count) {
                        myQueryS1 = myQueryS1 + ' AND';
                        count = false
                    };
                    myQueryS1 = myQueryS1 + ' (Mode = ?)';
                    myQueryVariablesS1.push(req.query.modeS1)
                    count = true;
                };
                if (req.query.extent) {
                    if (count) {
                        myQueryS1 = myQueryS1 + ' AND';
                        count = false
                    };
                    myQueryS1 = myQueryS1 + ' (Overlaps(Coordinates, ST_GeomFromText(?)) OR Within(ST_GeomFromText(?), Coordinates) OR Within(Coordinates, ST_GeomFromText(?)))';
                    myQueryVariablesS1.push(req.query.extent)
                    myQueryVariablesS1.push(req.query.extent)
                    myQueryVariablesS1.push(req.query.extent)
                    count = true;
                };
                if (req.query.orbitdirectionS1) {
                    if (count) {
                        myQueryS1 = myQueryS1 + ' AND';
                        count = false
                    };
                    myQueryS1 = myQueryS1 + ' (Orbitdirection = ?)';
                    myQueryVariablesS1.push(req.query.orbitdirectionS1)
                    count = true;
                };

                if (req.query.relativeorbitnumberS1) {
                    if (count) {
                        myQueryS1 = myQueryS1 + ' AND';
                        count = false
                    };
                    myQueryS1 = myQueryS1 + ' (Relativeorbitnumber = ?)';
                    myQueryVariablesS1.push(req.query.relativeorbitnumberS1)
                    count = true;
                };
                myQueryS1 = myQueryS1 + ' ORDER BY Ingestiondate DESC'
                /////////////////////////////////////////////////////////////////////// S2
            } else if (req.query.satellite == 'S2') {
                var myQueryS2 = 'SELECT ID, Ingestiondate, Satellite, Mode, Orbitdirection, Producttype, Relativeorbitnumber, Size, AsText(coordinates) AS bbox FROM s2 WHERE';
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
                        myQueryS2 = myQueryS2 + ' AND';
                        count = false
                    };
                    myQueryS2 = myQueryS2 + ' (Overlaps(Coordinates, ST_GeomFromText(?)) OR Within(ST_GeomFromText(?), Coordinates) OR Within(Coordinates, ST_GeomFromText(?)))';
                    myQueryVariablesS2.push(req.query.extent)
                    myQueryVariablesS2.push(req.query.extent)
                    myQueryVariablesS2.push(req.query.extent)
                    count = true;
                };
                myQueryS2 = myQueryS2 + ' ORDER BY Ingestiondate DESC'
            };

            callback(myQueryS1, myQueryS2, myQueryVariablesS1, myQueryVariablesS2)
        };

        var QueryDB = function (myQueryS1, myQueryS2, myQueryVariablesS1, myQueryVariablesS2) {
            //commit two queries (if they exist), return results and mapScript

            console.log('got data myQueryS1 175: ' + myQueryS1);
            console.log('got data myQueryS2 176: ' + myQueryS2);

            if (myQueryS1) {
                pool.getConnection(function (err, connectionS1, resultsS1) {
                    if (err) throw err;
                    connectionS1.query(myQueryS1, myQueryVariablesS1, function (err, resultsS1, fields) {
                        console.log('Query: ' + myQueryS1);
                        var polygonScriptS1 = '';
                        if (resultsS1.length) {
                            for (var result in resultsS1) {
                                var polygonGeoJSON = parse(resultsS1[result].bbox)

                                var polygonParsed = [];
                                for (var pair in polygonGeoJSON.coordinates[0]) {
                                    console.log(polygonGeoJSON.coordinates[0][pair]);
                                    polygonParsed.push([polygonGeoJSON.coordinates[0][pair][1], polygonGeoJSON.coordinates[0][pair][0]]);
                                }
                                polygonParsed = JSON.stringify(polygonParsed);

                                polygonScriptS1 = polygonScriptS1 + "\n var polygon = L.polygon(" + polygonParsed + ", {color : '#000101', opacity : 0.8, className : '" + resultsS1[result].ID + "'}).addTo(map)" + '.bindPopup("<p>' + 'typ produktu: ' + resultsS1[result].Producttype + '<br>tryb sensora: ' + resultsS1[result].Mode + '<br>polaryzacja: ' + resultsS1[result].Polarisationmode + '<br>data i czas pozyskania: ' + resultsS1[result].Ingestiondate + '<br>satelita: ' + resultsS1[result].Satellite + '<br>pobierz ' + resultsS1[result].ID + '</p>")'
                            }
                        }

                        connectionS1.release();
                        console.log('Connection connectionS1 relased');
                        callback(resultsS1, polygonScriptS1)
                    });
                });
            };

            if (myQueryS2) {
                pool.getConnection(function (err, connectionS2, resultsS2) {
                    if (err) throw err;
                    connectionS2.query(myQueryS2, myQueryVariablesS2, function (err, resultsS2, fields) {
                        console.log('Query: ' + myQueryS2);
                        var polygonScriptS2 = '';
                        if (resultsS2.length) {
                            for (var result in resultsS2) {
                                var polygonGeoJSON = parse(resultsS2[result].bbox);

                                var polygonParsed = [];

                                for (var pair in polygonGeoJSON.coordinates[0]) {
                                    console.log(polygonGeoJSON.coordinates[0][pair]);
                                    polygonParsed.push([polygonGeoJSON.coordinates[0][pair][1], polygonGeoJSON.coordinates[0][pair][0]]);
                                }

                                polygonParsed = JSON.stringify(polygonParsed);
                                polygonScriptS2 = polygonScriptS2 + "\n var polygon = L.polygon(" + polygonParsed + ", {color : '#000101', opacity : 0.8, className : '" + resultsS2[result].ID + "'}).addTo(map)" + '.bindPopup("<p>' + 'typ produktu: ' + resultsS2[result].Producttype + '<br>tryb sensora: ' + resultsS2[result].Mode + '<br>polaryzacja: ' + resultsS2[result].Polarisationmode + '<br>data i czas pozyskania: ' + resultsS2[result].Ingestiondate + '<br>satelita: ' + resultsS2[result].Satellite + '<br>pobierz ' + resultsS2[result].ID + '</p>")'
                            }
                        }
                        connectionS2.release();
                        console.log('Connection connectionS2 relased');
                        callback(resultsS2, polygonScriptS2)
                    });
                });
            };
        };

        BuildQuery(QueryDB);
    };

    Query(Render);

////////////////////////////////////////////////////////////////////////////////////////////////////
    /*

    if (isNotEmpty) {
        pool.getConnection(function (err, connection) {
            if (err) throw err;
            connection.query(myQueryS1, myQueryVariablesS1, function (err, results, fields) {
                console.log('Query: ' + myQueryS1);

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

    */
});














module.exports = router;