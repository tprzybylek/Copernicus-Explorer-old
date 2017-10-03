'use strict';
var express = require('express');
var mysql = require('mysql');
var router = express.Router();
var async = require('async');
var fs = require('fs');
var path = require('path');

router.get('/', function (req, res) {

    var token = req.query.token;
    var jsonPath = path.join(__dirname, '..', 'public', 'orders.json');

    fs.readFile(jsonPath, function (err, data) {
        var j = JSON.parse(data);

        for (var i = 0; i < j.length; i++) {
            if (j[i]['token'] == token) {
                if (j[i]['status'] == '1') {
                    var status = j[i]['status'];
                    console.log(j[i]);
                    console.log(j[i]['status']);
                    res.render('order', { title: 'Zamówienie', orderID: token, status: j[i]['status']});
                }
            }
        }
    });


});

module.exports = router;