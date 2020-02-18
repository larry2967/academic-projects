var express = require('express');
var router = express.Router();

router.get('/', function(req, res, next) {
    res.render('login', {title: 'Login'});
});

router.post('/', function(req, res, next) {
    var id = req.body.user_id;
    var pass = req.body.user_password;
    if(id=="" || pass==""){
        res.render('login');
   }else{
       //global.userID = id;
       req.session.idd = req.body.user_id;
       req.session.address = req.body.user_address;
       console.log(req.session.idd);
       console.log(req.session.address);
       res.redirect('guess');
   }

});

module.exports = router;
