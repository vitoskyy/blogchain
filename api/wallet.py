from web3 import Web3


w3 = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/5ba1f03edd79439a8b3205097943e498'))
account = w3.eth.account.create()
privateKey = account.privateKey.hex()
address = account.address

print(f"You address: {address}\nYour key: {privateKey}")
