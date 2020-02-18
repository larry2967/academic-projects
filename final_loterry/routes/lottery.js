var express = require('express');
var router = express.Router();
var schedule = require('node-schedule');
var start = 1576831803;//2019/12/20 16:50
var numbers;
var lotteryId;
var mem_add;
var mem_key;
var draw_num;

function drawing(mem_add, mem_key, draw_num)
{
	
//Transaction
var Web3 = require('web3');
const testnet = 'https://ropsten.infura.io/';
const web3 = new Web3(new Web3.providers.HttpProvider(testnet)); //串以太坊

var contract_address = "0xB24679190D187A32F7900079e6B8ab245320af02";
var contractABI = [
	{
		"constant": false,
		"inputs": [
			{
				"name": "buy_num",
				"type": "uint256"
			}
		],
		"name": "buylottery",
		"outputs": [],
		"payable": true,
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "num_temp",
				"type": "uint256"
			}
		],
		"name": "drawing",
		"outputs": [],
		"payable": true,
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [],
		"name": "find_winner1",
		"outputs": [],
		"payable": true,
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [],
		"name": "find_winner2",
		"outputs": [],
		"payable": true,
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "num_lottery",
				"type": "uint256"
			}
		],
		"name": "public_lottery_num",
		"outputs": [],
		"payable": true,
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "dest",
				"type": "address"
			},
			{
				"name": "winning_prize",
				"type": "uint256"
			}
		],
		"name": "win_lottery",
		"outputs": [],
		"payable": true,
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"payable": true,
		"stateMutability": "payable",
		"type": "fallback"
	},
	{
		"constant": true,
		"inputs": [
			{
				"name": "",
				"type": "address"
			}
		],
		"name": "buy_num_mapping",
		"outputs": [
			{
				"name": "",
				"type": "uint256"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [
			{
				"name": "",
				"type": "address"
			}
		],
		"name": "lottery_num",
		"outputs": [
			{
				"name": "",
				"type": "uint256"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "num_players",
		"outputs": [
			{
				"name": "",
				"type": "uint256"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [
			{
				"name": "",
				"type": "uint256"
			}
		],
		"name": "player_address",
		"outputs": [
			{
				"name": "",
				"type": "address"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [
			{
				"name": "",
				"type": "uint256"
			}
		],
		"name": "winning_address",
		"outputs": [
			{
				"name": "",
				"type": "address"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "winning_people_num",
		"outputs": [
			{
				"name": "",
				"type": "uint256"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	}
]
var contract = web3.eth.contract(contractABI).at(contract_address);

var wallet_address = mem_add;//test
// var to_address = "0xCf3892087b9A007930C199EA0cAdc62418161fB5";
var count = web3.eth.getTransactionCount(wallet_address); //計數器


var rawTransacton = {
	"from": wallet_address,
	"nonce": web3.toHex(count), //上面都是十六進位
	"gasPrice": web3.toHex(21000000000),
	"gasLimit": web3.toHex(200000),
	"to": contract_address,
	"value": "0x0",
	"data": contract.drawing.getData(draw_num)//轉100枚
};
//   function transfer(address _to, uint256 _value) public returns (bool) 
var Tx = require("ethereumjs-tx").Transaction;
//var Tx = require('ethereumjs-tx'); //簽署合約 以下都是固定寫法
var privateKey = new Buffer(mem_key,"hex");
var tx = new Tx(rawTransacton,{'chain':'ropsten'});

tx.sign(privateKey);
var serializedTx = tx.serialize();//把它序列化

web3.eth.sendRawTransaction('0x' + serializedTx.toString('hex'), function(err,hash){ //call back function 上面做完才會往下，等待時就不會進入
	if(!err){
		console.log(hash); //這筆交易的流水號
	}
	else{
		console.log(err);
	}
});
}
router.get('/', function(req, res, next) {
    var pool = req.connection;
    pool.getConnection(function (err, connection) {
        connection.query('SELECT LotteryId FROM lottery ORDER BY LotteryId DESC LIMIT 0 , 1', function (err, rows) {
            if (err) {
                res.render('error', {
                    message: err.message,
                    error: err
                });
            }
            else {
                console.log(rows);
                //rows = JSON.stringify(rows);
                lotteryId = rows[0].LotteryId+1;
                console.log(lotteryId);
                res.render('lottery', { 
                    router_method: 'post',
                    rows: rows
                });

            }
        })
        
        connection.release();
    })
});

router.post('/', function(req, res){
    var pool = req.connection;
    numbers = Math.floor(Math.random() * (5- 1) + 1);
    console.log('randomNumber:'+numbers)
    pool.getConnection(function (err, connection) {
        connection.query('INSERT INTO lottery(LotteryId, number) VALUES(?,?)', [lotteryId,numbers], function (err, rows) {
            if (err) {
                res.render('error', {
                    message: err.message,
                    error: err
                });
            }
            else {
                res.render('lottery', { 
                    draw: '第'+lotteryId+'期',
                    number: '中獎號碼：'+numbers
                });
                lotteryId++;
            }
        })
        
        connection.release();
    })
});
module.exports = router;