'use strict';
var express = require('express');
var router = express.Router();
//http?

var myPythonScript = "Imagery_Clip.py";

var pythonExecutable = "C:\\Python27\\python.exe";

router.get('/', function (req, res) {
    var extent = req.query.extent;
    var ID = req.query.ID;
    var title = req.query.Title;

    var PythonShell = require('python-shell');

    var options = {
        mode: 'text',
        pythonPath: 'C:\\Python27\\python.exe',
        pythonOptions: ['-u'],
        scriptPath: 'C:\\Users\\20274\\OneDrive\\Dokumenty\\Visual Studio 2017\\Projects\\Imagery-Explorer\\Imagery-Explorer\\public\\scripts\\Imagery-Clip\\',
        args: [req.query.ID, req.query.title]
    };

    PythonShell.run(myPythonScript, options, function (err) {
        if (err) throw err;
        console.log('finished');
    });
    
    res.render('crop', {title: 'crop'});
});

module.exports = router;