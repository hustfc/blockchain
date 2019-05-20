import hashlib
import json
from time import time
from uuid import uuid4
from urllib.parse import urlparse
import requests

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.currentTransaction = []
        self.nodes = set()

        #Create the genesis block
        self.newBlock(proof=100, previousHash=1)

    def registerNode(self, address):
        """
        Add a new node to the list of nodes
        :param address: <str> Address of node. Eg. 'http://192.168.0.5:5000'
        :return: None
        """
        parsedUrl = urlparse(address)
        self.nodes.add(parsedUrl.netloc)

    #区块是否有效(是否被篡改、工作量证明对不对)
    def validChain(self, chain):
        """
        Determine if a given blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """
        previousBlock = chain[0]
        currentIndex = 1

        while currentIndex < len(chain):
            block = chain[currentIndex]
            print(f'{previousBlock}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previousHash'] != self.hash(previousBlock):
                return False

            # Check that the Proof of Work is correct
            if not self.validProof(previousBlock['proof'], block['proof']):
                return False

            previousBlock = block
            currentIndex += 1

        return True

    def resolveConflicts(self):
        """
        共识算法解决冲突
        使用网络中最长的链.
        :return: <bool> True 如果链被取代, 否则为False
        """
        neighbours = self.nodes
        newChain = None

        # We're only looking for chains longer than ours
        maxLength = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > maxLength and self.validChain(chain):
                    maxLength = length
                    newChain = chain

        if newChain:
            self.chain = newChain
            return True

        return False

    def newBlock(self, proof, previousHash = None):
        # Creates a new Block and adds it to the chain
        """
        生成新块
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """
        block = {
            'index' : len(self.chain) + 1,
            'timestamp' : time(),
            'transactions' : self.currentTransaction,
            'proof' : proof,
            'previousHash' : previousHash or self.hash(self.chain[-1])
        }

        # Reset the current list of transactions
        self.currentTransaction = []

        self.chain.append(block)
        return block

    def newTransaction(self, sender, recipient, amount):
        # Adds a new transaction to the list of transactions
        """
        生成新交易信息，信息将加入到下一个待挖的区块中
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """
        self.currentTransaction.append({
            'sender' : sender,
            'recipient' : recipient,
            'amount' : amount,
        })

        #下一个待挖的区块中
        return self.lastBlock['index'] + 1

    @staticmethod
    def hash(block):
        # Hashes a Block
        """
        生成块的 SHA-256 hash值
        :param block: <dict> Block
        :return: <str>
        转化为json编码格式之后hash，最后以16进制的形式输出
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        blockString = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(blockString).hexdigest()

    @property
    def lastBlock(self):
        # Returns the last Block in the chain
        return self.chain[-1]

    @staticmethod
    def validProof(lastProof, proof):
        """
        验证证明: 是否hash(last_proof, proof)以4个0开头?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """
        guess = f'{lastProof}{proof}'.encode()
        guessHash = hashlib.sha256(guess).hexdigest()
        return guessHash[:4] == '0000'

    def proofOfWork(self, lastProof):
        """
        简单的工作量证明:
         - 查找一个 p' 使得 hash(pp') 以4个0开头
         - p 是上一个块的证明,  p' 是当前的证明
        :param last_proof: <int>
        :return: <int>
        """
        proof = 0
        while self.validProof(lastProof, proof) is False:
            proof += 1

        return proof


