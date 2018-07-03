"""
Operations that are being facilitated are :
    - creating transaction
    - mining a block
    - adding nodes to blockchain
    - update chain in decentralised system
Facilitates not available :
    - nodes not sync. when new nodes are added
    - transactions are not sync when new transactions are added

"""


# Libararies
import datetime
import hashlib
import json
from urllib.parse import urlparse
import requests

# Create Blockchain
class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.nodes = set()
        self.create_block(proof = 1, previous_hash = 0)
    
    # bloc created and appended to chain, but not mined
    def create_block(self, proof, previous_hash):
        block = {'index' : len(self.chain)+1,
                 'timestamp' : str(datetime.datetime.now()),
                 'proof' : proof,
                 'previous_hash' : previous_hash,
                 'transactions' : self.transactions
                 }
        self.transactions = [] # all transactions are copied to block, lets remove it 
        self.chain.append(block)
        return block
    
    def get_last_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        valid_proof = False
        while valid_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                valid_proof = True
            else:
                new_proof+=1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block,sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
        
    def is_chain_valid(self, chain): # chain as param cus want to check validity of chains of other nodes
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index+=1      
        return True
        
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender' : sender,
                                  'receiver' : receiver,
                                  'amount (in OPC)' : amount})
        last_block_index = self.get_last_block()['index']
        return last_block_index + 1

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            # make a request to get chain length of diff nodes
            url = 'http://%s/get_chain'%node
            response = requests.get(url)
            if response.status_code  ==200 :
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False