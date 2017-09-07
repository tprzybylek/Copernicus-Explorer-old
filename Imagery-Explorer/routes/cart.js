'use strict';
var express = require('express');
var router = express.Router();
var mysql = require('mysql');
//http?

var pool = mysql.createPool({
    connectionLimit: 2,
    host: 'localhost',
    user: 'root',
    database: 'products'
});

router.get('/', function (req, res) {

    var IDs = JSON.parse(req.cookies.IDs);

    if (IDs.length > 0) { 

        results = [];

        /*
        var myCallback = function (data) {
            console.log('got data: ' + data);
        };

        var usingItNow = function (callback) {
            callback('get it?');
        };

        usingItNow(myCallback);
        */

        /*
        var pushResult = function (data) {
            console.log('got data: ' + result);
        };

        var queryDB = function (callback) {

            connection.query("SELECT * FROM (SELECT * FROM s1 UNION SELECT * FROM s2) AS U WHERE U.ID = ?", IDs[0], function (err, result, fields) {
                if (err) throw err;
                console.log(result);
                //res.render('cart', { title: 'Koszyk', items: results });
                callback(results);
                connection.release();
            });
            
        };
        */

        queryDB(pushResult);
        






        pool.getConnection(function (err, connection) {
            if (err) throw err;
            console.log('Connection ID: ' + connection.threadId);

            connection.query("SELECT * FROM (SELECT * FROM s1 UNION SELECT * FROM s2) AS U WHERE U.ID = ?", IDs[0] ,function (err, result, fields) {
                if (err) throw err;
                console.log(result);
                res.render('cart', { title: 'Koszyk', items: results });
                connection.release();
            });
        });

    } else {
        res.render('cart', { title: 'Koszyk'});
    };

    console.log('IDs: ', IDs)
});

module.exports = router;