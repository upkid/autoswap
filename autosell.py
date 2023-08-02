#!/usr/bin/env python3

import time, json, web3
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from eth_account import Account

url     = "http://3.77.23.204:8545"

# 私钥地址
owner_address  = "0x4da596ED0717Ff64CC307507dDd6BC914245E4b7"
private_key    = ""

# 代币地址
WAITD   = "0xEC4C225F734a614B6d6f61b5Ddf0ae96c8e85E32"
USDT    = "0x848cb1a9770830da575DfD246dF2d4e38c1D40ed"

# 合约地址
router_address  = "0x3320B7E625124910BFad5CaF9DC1767205D91286"

w3 = Web3(HTTPProvider(url))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # 注入poa中间件


class UniswapV2Router02(object):
    url = None

    def __init__(self, contract_address, endpoint):
        if endpoint.find('http://') == -1:
            endpoint = 'http://' + endpoint
        self.url = endpoint
        self.web3 = Web3(Web3.HTTPProvider(endpoint, request_kwargs={'timeout': 60}))

        abi_file = "uniswap-v2-router02.json"
        contract_abi = json.load(open(abi_file))

        ckaddress = web3.Web3.to_checksum_address(contract_address)
        self.contract = self.web3.eth.contract(address=ckaddress, abi=contract_abi)

    def SwapExactETHForTokens(self, privkey, token, amountIn):
        value = amountIn
        amounts = self.getAmountsOut(WAITD, token, value)
        amountOutMin = int(amounts[1] * 0.99519)

        path = []
        path.append(web3.Web3.to_checksum_address(WAITD))
        path.append(web3.Web3.to_checksum_address(token))

        sendfrom = Account.from_key(privkey)
        privateKey = sendfrom._key_obj
        publicKey = privateKey.public_key
        address = publicKey.to_checksum_address()

        deadline = int(time.time()) + 20 * 60
        gasprice = self.web3.eth.gas_price
        nonce = self.web3.eth.get_transaction_count(address, "pending")

        unsigned_tx = self.contract.functions.swapExactETHForTokens(amountOutMin, path, address, deadline) \
            .build_transaction({'gas': 220716, 'gasPrice': gasprice, 'from': address, 'nonce': nonce, 'value': value})
        signed_tx = sendfrom.signTransaction(unsigned_tx)
        txid = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return txid.hex()

    def getAmountsOut(self, tokenA, tokenB, amountIn):
        path = []
        path.append(web3.Web3.to_checksum_address(tokenA))
        path.append(web3.Web3.to_checksum_address(tokenB))

        amounts = self.contract.caller().getAmountsOut(amountIn, path)
        return amounts

def sell():
    r = UniswapV2Router02(router_address, url)

    aitd_amount = w3.eth.get_balance(owner_address)
    limit = 1000000000000000000
    reserve_fee = 510000000000000000
    if aitd_amount > limit:
        amountIn = aitd_amount - reserve_fee
        print("aitd amount: ", aitd_amount, "swap amount: ", amountIn)

        hash = r.SwapExactETHForTokens(private_key, USDT, amountIn)
        print("ts: ", time.time(), "sell success: ", hash)
        return True


if __name__ == '__main__':

    while True:
        sell()
        time.sleep(1)
