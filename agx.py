# -*- coding: utf-8 -*-
"""

My AGX crypto

"""

# Libraries import

import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse


# Building a blockchain

class Blockchain:
    """
    Initiate the object
    create a chain list to hold mined transactions
    create transactions list to hold unmined transactions
    create a nodes set to hold the nodes on my network
    create a genesis block

    """

    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof=1, previous_hash='0')
        self.nodes = set()

    """

    This method creates a block using the given information and add it to the chain
    after adding the transactions to the chain it truncates the transactions list

    """

    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block

    """

    Get the last block in the chain

    """

    def get_previous_block(self):
        return self.chain[-1]

    """

    proof of work number finder by

    1. setting the default to 1
    2. as long as it isnt generating a hash starting with 4 zeroes try again by incrementing the proof
    3. once the proof number gets a correct hash set the check_proof to true

    """

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1

        return new_proof

    """

    hash given block

    """

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    """
    validate bwana wangu

    1. check if the previous hash is correct/ existing link
    2. check if the proof hashing starts by 4 zeroes
    3. Increment the block index to take the next block and set previous block to the current/finished block

    """

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof ** 2 - previous_proof ** 2).encode()).hexdigest()

            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1

        return True

    """
    
    This method creates transactions in the transaction[],
    in the needed format via a dict,
    then return the index of the block supposed to hold this transaction in the future(just the last_block+1).
    
    """
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({
            'sender':sender,
            'receiver':receiver,
            'amount':amount
        })

        previous_block = self.get_previous_block()
        return previous_block['index']+1

    """
    
    This method adds a new node to the network (ip mostly) using the urlparse function
    
    """

    def add_node(self,address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    """
    
    This method replaces the chain on the nodes with the longest chain on the network,
    it checks the current chain on that current node then tries to find a node with a longer chain, 
    if found it checks the validity and replaces the local one(Consensus) else it keeps that local one.
    
    """

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            # gets the node's ip and build a route using it
            response = requests.get(f"http://{node}/get_chain")
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                # check length and validity of node's chain
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain

        if longest_chain:
            # Update the global chain with the longest
            self.chain = longest_chain
            return True
        # Basically return false in case its not the longest chain
        return False



# Mining a blockchain

# ------------------------------------------------- Flask Web app --------------------------------------------------

app = Flask(__name__)


"""

Creating uuid addresses of the nodes, actually this creates a uuid str of the node on port 5000 of flask

"""
node_address = str(uuid4()).replace('-','')
# instance of the blockchain class

blockchain = Blockchain()

"""

1. return the proof of the previous block
2. calculate the proof_of_work of the new block
3. hash the previous_block
4. create a block with the data in hand
5. return the block data in json + response code

"""


@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender=node_address,receiver='Hamada',amount=1)

    # because it returns the content of that block after creating it
    block = blockchain.create_block(proof, previous_hash)

    response = {'message': 'Omedetou, you mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions':block['transactions']
                }
    return jsonify(response), 200


"""

Return all the chain

"""


@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200


"""

Checking if the chain is valid via api request

"""


@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'The chain is valid'}
    else:
        response = {'message': 'Abunai, the chain is invalid!!!'}

    return jsonify(response), 200


"""

Create transactions given via a post request after validation

"""
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender','receiver','amount']
    # validate if the needed keys from the list above are all given
    if not all(key in json for key in transaction_keys):
        return 'Abunai the transaction is incomplete', 400
    # in case all is well insert our transaction
    index = blockchain.add_transaction(json['sender'],json['receiver'],json['amount'])
    response = {'message': f'The transaction has been recorded successfully, it will be added in block no. {index}'}
    return jsonify(response), 201



# Decentralizing the blockchain


"""

Run the flask app

"""

app.run(host='0.0.0.0', port=5000)
