var express = require('express');
var router = express.Router();

/* GET home page. */
router.get('/', function (req, res) {
    res.render('users', { title: 'Express' });
});

module.exports = router;//模組化