'use strict';
var express = require('express');
var mysql = require('mysql');
var router = express.Router();
var async = require('async');
var fs = require('fs');
var path = require('path');

router.post('/', function (req, res) {
    var PythonShell = require('python-shell');
    
    var myPythonScript = "Imagery_Clip.py"; //!!!
    var pythonExecutable = "C:\\Python27\\python.exe";

    

    function joinParameters() {
        var resultsHelper = '[' + req.body.resultsString + ']';

        //console.log(req.body.resultsString);
        //console.log(resultsHelper);

        var resultsString = JSON.parse(resultsHelper);
        var extent = JSON.parse(req.body.extent);
        var email = req.body.email;
        var token = req.body.token;

        //console.log(resultsString);

        var joinedParameters = {};
        var images = [];

        for (var key in resultsString) {
            var image = JSON.parse(resultsString[0][key])
            var obj = {}
            obj['ID'] = image['ID'];
            obj['title'] = image['Title'];
            obj['satellite'] = image['Satellite'];
            images.push(obj);
            console.log(images);
        };
        joinedParameters['token'] = token;

        var d = new Date();
        var seconds = Math.round(d.getTime() / 1000);

        joinedParameters['orderedTime'] = Date.now();
        joinedParameters['completedTime'] = seconds;
        joinedParameters['extent'] = extent;
        joinedParameters['cart'] = images;
        joinedParameters['email'] = email;
        joinedParameters['status'] = '0';

        return joinedParameters
    };

    var order = joinParameters();
    var orderString = JSON.stringify(order);
    var jsonPath = path.join(__dirname, '..', 'public', 'orders.json');

    console.log(orderString);

    fs.readFile(jsonPath, function (err, data) {
        var json = JSON.parse(data);
        json.push(order);

        fs.writeFile(jsonPath, JSON.stringify(json));
    });

    var options = {
        mode: 'text',
        pythonPath: 'C:\\Python27\\python.exe',
        pythonOptions: ['-u'],
        scriptPath: 'C:\\Users\\20274\\OneDrive\\Dokumenty\\Visual Studio 2017\\Projects\\Imagery-Explorer\\Imagery-Explorer\\public\\scripts\\Imagery-Clip\\',
        args: [orderString]
    };
    
    PythonShell.run(myPythonScript, options, function (err) {
        if (err) throw err;
        console.log(orderString);
        console.log('finished');
    });
    

    res.render('newOrder', { title: 'new order', orderID: req.body.token });
});

module.exports = router;

/*



*/