import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request
from BlockChain import Blockchain

# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
# 基于随机数生成唯一的id
nodeIdentifier = str(uuid4()).replace('-', '')

# Instantiate the BlockChain
blockchain = Blockchain()

#创建/mine GET接口
@app.route('/mine', methods=['GET'])
def mine():
    # 1.计算工作量证明PoW
    # 2.通过新增一个交易授予矿工(自己)一个币
    # 3.构造新区块并且添加到链中
    # We run the proof of work algorithm to get the next proof...
    lastBlock = blockchain.lastBlock
    lastProof = lastBlock['proof']
    proof = blockchain.proofOfWork(lastBlock)

    # 给工作量证明的节点提供奖励.
    # 发送者为 "0" 表明是新挖出的币
    blockchain.newTransaction(
        sender='0',
        recipient=nodeIdentifier,
        amount=1
    )

    #加入到链中
    block = blockchain.newBlock(proof)

    response = {
        'message' : "New Block Forged",
        'index' : block['index'],
        'transactions' : block['transactions'],
        'proof' : block['proof'],
        'previousHash' : block['previousHash'],
    }
    return jsonify(response), 200



#创建/transactions/new POST接口,可以给接口发送交易数据
@app.route('/transactions/new', methods=['POST'])
def newTransaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.newTransaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

#创建/chain接口, 返回整个区块链。
@app.route('/chain', methods=['GET'])
def fullChain():
    response = {
        'chain' : blockchain.chain,
        'length' : len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    #服务运行在端口5000上.
    app.run(host='127.0.0.1', port=5000)
