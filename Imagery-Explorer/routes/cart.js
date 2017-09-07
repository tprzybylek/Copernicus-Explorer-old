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

    var IDs = req.cookies.IDs.split(",");

    var query = '';

    pool.getConnection(function (err, connection) {
        if (err) throw err;
        console.log('Connection ID: ' + connection.threadId);

        connection.query("SELECT * FROM (SELECT * FROM s1 UNION SELECT * FROM s2) AS U WHERE U.ID = ?", IDs[0] ,function (err, result, fields) {
            if (err) throw err;
            console.log(result);
            res.render('cart', { title: 'cart', items: result });
            connection.release();
        });

    });

    console.log('IDs: ', IDs)
});

module.exports = router;