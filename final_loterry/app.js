global.userID = "";
global.drawID = "";
var createError = require('http-errors');
var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');
var logger = require('morgan');
var session = require('express-session');//session
var schedule = require('node-schedule');

var indexRouter = require('./routes/index');
var usersRouter = require('./routes/users');
var register = require('./routes/register');
var login = require('./routes/login');
var guess = require('./routes/guess');
var result = require('./routes/result');
var lottery = require('./routes/lottery');

var mysql = require('mysql');
var pool = mysql.createPool({
  host:"localhost",
  user:"root",
  password:"123456",
  database:"tutorial"
});
pool.getConnection(function(err){
  if(err){
    console.log("connecting error");
  }
  else
  console.log("connecting successfully");
})

var app = express();
app.use(function(req,res,next){
  req.connection = pool;
  next();
})
// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'pug');

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

// sign for session
app.use(session({secret:'123456789'}));

app.use('/', indexRouter);
app.use('/users', usersRouter);
app.use('/register', register);
app.use('/login', login);
app.use('/guess', guess);
app.use('/result', result);
app.use('/lottery', lottery);

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  next(createError(404));
});

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});


module.exports = app;
