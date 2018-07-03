from flask import Flask, jsonify , request, render_template
from uuid import uuid4
from blockchain import Blockchain

# Create a web app
app = Flask(__name__)

# Create an address for the node on port 5001
node_address = str(uuid4()).replace('-', '')

# Create a blockchain object
blockchain = Blockchain()

# Render html on /
@app.route('/')
def root():
    return render_template('index.html')

# Get the chain
@app.route('/get_chain', methods = ['GET'])
def get_blockchain():
    response = {'chain' : blockchain.chain,
                'length' :len(blockchain.chain)}
    return jsonify(response), 200

# Check if blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    if blockchain.is_chain_valid(blockchain.chain):
        response = 'Nothing to worry!! Chain is valid'
    else:
        response = 'Something is wrong.. Check it asap'
    return jsonify(response), 200

# Add a new transaction
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of transaction are missing' , 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message' : 'This transaction will probably be added to block %s'%index}
    return jsonify(response), 201  

# Mining a block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_last_block()
    previous_proof = previous_block['proof']
    
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    
    # Reward for mining
    blockchain.add_transaction(sender = node_address,receiver = 'Somesh', amount = 1)
    block = blockchain.create_block(proof,previous_hash)
     
    response = {'message' : 'Congrats! You created a block',
                'index' : block['index'],
                'timestamp' : block['timestamp'],
                'proof' : block['proof'],
                'previous_hash' : block['previous_hash'],
                'transaction': block['transactions']}
    return jsonify(response), 200


##### Decentralizing the blockchain or Opencoin

# Adding new nodes to blockchain
@app.route('/add_node', methods = ['POST'])
def add_node():
    json = request.get_json()
    node = json.get('node')
    if node is None:
        return 'No Node' , 400
    blockchain.add_node(node)
    response =  {'message' : 'The Node is added. The Opencoin Blockchain contains the following nodes.',
                 'total_nodes' : list(blockchain.nodes)}
    return jsonify(response), 201


# Replacing the chain by longest chain if needed.
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message' : 'Nodes had different chain. Now they got replaced by the longest one.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message' : 'All good. You\'ve got longest chain.',
                    'new_chain' : blockchain.chain}
    return jsonify(response), 200

# Running the app
app.run(host = '0.0.0.0', port = 5001)
