import json

import web3
from solcx import compile_standard
from web3 import Web3

# from solcx import install_solc
# install_solc('v0.6.0')

with open('./SimpleStorage.sol', 'r') as file:
    simple_storage_file = file.read()

# compile our solidity

compile_sol = compile_standard({
    'language': 'Solidity',
    'sources': {'SimpleStorage.sol': {
        'content': simple_storage_file
    }},
    'settings': {
        'outputSelection': {
            '*': {
                '*': [
                    'abi', 'metadata', 'evm.bytecode', 'evm.sourceMap'
                ]
            }
        }
    }, },
    solc_version="0.6.0",
)

with open('compiled_code.json', 'w') as file:
    json.dump(compile_sol, file)

#  get byte code
bytecode = compile_sol['contracts']['SimpleStorage.sol'][
    'SimpleStorage']['evm']['bytecode']['object']

#  get abi
abi = compile_sol['contracts']['SimpleStorage.sol']['SimpleStorage']['abi']

#  for connecting to rinkeby
w3 = Web3(web3.HTTPProvider(
    'https://rinkeby.infura.io/v3/50b0661870f44f2fa07c60805a88ed19'))

chain_id = 4
my_address = "0x49A6C33E7C6Ac40E5568353c389899834590Cb86"
private_key = "0x474f6e23f1f4eb2aeab7285fccb46c1cd985f6a299232b40af1561b4c5c83118"

#  Create contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
#  get  latest transaction count
nonce = w3.eth.getTransactionCount(my_address)

#  1 build a transaction
#  2 sign a transaction
#  3 send a transaction
transaction = SimpleStorage.constructor().buildTransaction({
    "chainId": chain_id, 'from': my_address, 'nonce': nonce
})

#  sing the transaction
signed_txn = w3.eth.account.sign_transaction(
    transaction, private_key=private_key
)
print('Deploying Contract ....')
#  send this signed transaction
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print('Deployed!')

#  working with contract, you always need
#  contract address
#  contract abi
simple_storage = w3.eth.contract(
    address=tx_receipt.contractAddress,
    abi=abi
)

#  call -> simulate making a call  and getting a return value which does
#  not make a state change
#  Transact -> Actually when we make a state change

#  Initial value of favorite number
print(simple_storage.functions.retrieve().call())
print('Updating Contract...')
store_transaction = simple_storage.functions.store(15).buildTransaction(
    {'chainId': chain_id, 'from': my_address, 'nonce': nonce + 1}
)

signed_store_txn = w3.eth.account.sign_transaction(store_transaction,
                                                   private_key=private_key)
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print('Updated!')
print(simple_storage.functions.retrieve().call())
