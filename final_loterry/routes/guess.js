var express = require('express');
var router = express.Router();

var mem_add;
var mem_key;
var guess_num;
var membuy_val;

function buylottery(mem_add, mem_key, guess_num, membuy_val)
{

var get_val = membuy_val*Math.pow(10,18);
//Transaction
var Web3 = require('web3');
const testnet = 'https://ropsten.infura.io/';
const web3 = new Web3(new Web3.providers.HttpProvider(testnet)); //串以太坊

var contract_address = "0xB0xF21B7f68E969677c22b25C37F3bB8e75642fad2E";
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
	"value": get_val,
	"data": contract.buylottery.getData(guess_num)//轉100枚
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
    res.render('guess', {
        id:req.session.idd
        //id: global.userID
    });
});

router.post('/', function(req, res){
    var id = req.session.id;
    var number = req.body.user_guess_number;
    var pool = req.connection;
    pool.getConnection(function (err, connection) {
        connection.query('INSERT INTO user_guess(userId, lotteryId, number) VALUES(?,?,?)', [id,1,number],function (err, result) {
            if (err) {
                res.render('error', {
                    message: err.message,
                    error: err
                });
            }
            else {
                console.log(result);
                res.render('guess', { 
                    id: req.session.idd,
                    number:number
                });

            }
        })
        connection.release();
    })
});
module.exports = router;
