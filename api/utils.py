from web3 import Web3


def sendTransaction(message):
    w3 = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/5ba1f03edd79439a8b3205097943e498'))
    address = '0x2BC01165456E1df58c3B674fe36352250Ea45208'
    privateKey = '0xabd13a7275b349b384e1c276a8e91a1e34ad4fa3e961a28d2587bfa6faf09928'
    nonce = w3.eth.getTransactionCount(address)
    gasPrice = w3.eth.gasPrice
    value = w3.toWei(0, 'ether')
    signedTx = w3.eth.account.signTransaction(dict(
        nonce=nonce,
        gasPrice=gasPrice,
        gas=100000,
        to='0x0000000000000000000000000000000000000000',
        value=value,
        data=message.encode('utf-8')
    ), privateKey)

    tx = w3.eth.sendRawTransaction(signedTx.rawTransaction)
    txId = w3.toHex(tx)
    return txId
