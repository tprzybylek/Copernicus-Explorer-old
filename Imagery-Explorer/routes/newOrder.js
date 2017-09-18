'use strict';
var express = require('express');
var mysql = require('mysql');
var router = express.Router();
var async = require('async');
var fs = require('fs');
var path = require('path');

/*

Get orderID, IDs, Titles, Extent, E-mail (as JSON)
Place them in a JSON file
Invoke Python Script
Show OrderID

*/


router.post('/', function (req, res) {
    var PythonShell = require('python-shell');
    
    var myPythonScript = "Imagery_Clip_test.py"; //!!!
    var pythonExecutable = "C:\\Python27\\python.exe";

    var options = {
        mode: 'text',
        pythonPath: 'C:\\Python27\\python.exe',
        pythonOptions: ['-u'],
        scriptPath: 'C:\\Users\\20274\\OneDrive\\Dokumenty\\Visual Studio 2017\\Projects\\Imagery-Explorer\\Imagery-Explorer\\public\\scripts\\Imagery-Clip\\',
        args: [orderString]
    };

    function joinParameters() {
        var resultsHelper = '[' + req.body.resultsString + ']';
        var resultsString = JSON.parse(resultsHelper);
        var extent = JSON.parse(req.body.extent);
        var email = req.body.email;
        var token = req.body.token;

        var joinedParameters = {};
        var images = [];

        for (var key in resultsString) {
            var obj = {}
            obj['ID'] = resultsString[key]['ID'];
            obj['title'] = resultsString[key]['Title'];
            obj['Satellite'] = resultsString[key]['Satellite'];
            images.push(obj);
        };
        joinedParameters['token'] = token;
        joinedParameters['orderedTime'] = Date.now();
        joinedParameters['completedTime'] = '0';
        joinedParameters['extent'] = extent;
        joinedParameters['cart'] = images;
        joinedParameters['email'] = email;
        joinedParameters['status'] = '0';

        return joinedParameters
    };

    var order = joinParameters();
    var orderString = JSON.stringify(order);
    var jsonPath = path.join(__dirname, '..', 'public', 'orders.json');

    fs.readFile(jsonPath, function (err, data) {
        var json = JSON.parse(data);
        json.push(order);

        fs.writeFile(jsonPath, JSON.stringify(json));
    });

    PythonShell.run(myPythonScript, options, function (err) {
        if (err) throw err;
        console.log(orderString);
        console.log('finished');
    });

    res.render('newOrder', { title: 'new order' });
});

module.exports = router;

/*



*/