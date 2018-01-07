'use strict';
var express = require('express');
var mysql = require('mysql');
var router = express.Router();
var async = require('async');
var randomToken = require('random-token');

var pool = mysql.createPool({
    connectionLimit: 2,
    host: 'localhost',
    user: 'root',
    database: 'products'
});

//////////////////////////////////////////////////////////////////////////////////////////////////////////////

router.get('/', function (req, res) {
    if (req.cookies.IDs) {
        var IDs = JSON.parse(req.cookies.IDs);
        var extent = JSON.parse(req.cookies.extent);
        var extentString = JSON.stringify(extent);
        var token = randomToken(8);

        var resultsJSON = [];
        var resultsString = [];

        console.log(extent);

        if (IDs.length > 0) {
            var QueryDB = function (IDs) {
                var query = "SELECT * FROM (SELECT ID, Title, Ingestiondate, Mode, Orbitdirection, Relativeorbitnumber, Satellite, Size FROM s1 UNION SELECT ID, Title, Ingestiondate, Mode, Orbitdirection, Relativeorbitnumber, Satellite, Size FROM s2) AS U WHERE U.ID = ?"
                var resultsJSON = [];
                var resultsString = [];

                async.forEachOf(IDs, function (value, index, callback) {
                    pool.getConnection(function (err, connection) {
                        if (err) throw err;
                        connection.query(query, value, function (err, result, fields) {
                            connection.release();
                            var resultString = JSON.stringify(result[0]);
                            var resultJSON = JSON.parse(resultString);
                            resultsJSON.push(resultJSON);
                            resultsString.push(resultString);
                            if (resultsJSON.length == IDs.length) {
                                res.render('cart', { title: 'Koszyk', items: resultsJSON, extent: extentString, token: token, resultsString: resultsString });
                            };
                        });
                    });
                });
            };

            QueryDB(IDs);
        } else {
            res.render('cart', { title: 'Koszyk' });
        };
    };
});


module.exports = router;