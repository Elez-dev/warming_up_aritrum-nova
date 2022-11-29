from web3 import Web3
import time
import random
import threading
import abi

# Option
factor = 1  # purchase volume
flag_approve = 0  # if you need approve
number_of_repetitions = 1
number_of_threads = 1
slippage = 1  # %
# -------------------------

swap_ARB = [
    {'symbol': 'USDC',
     'address': '0x750ba8b76187092B0D1E87E28daaf484d1b5273b',
     'amount': (round(random.uniform(0.0009, 0.00095), 8))*factor},

    {'symbol': 'DAI',
     'address': '0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1',
     'amount': (round(random.uniform(0.0009, 0.00095), 8)) * factor}
]

eth = Web3.toChecksumAddress('0x722e8bdd2ce80a4422e880164f2079488e115365')  # ETH
contract_ARB = Web3.toChecksumAddress('0xee01c0cd76354c383b8c7b4e65ea88d00b06f36f')  # ARB swap
gasLimit = 4000000


def intToDecimal(qty, decimal):
    return int(qty * int("".join(["1"] + ["0"] * decimal)))


def web_arb_buy(privatekey, amount, tokenToBue, symbol):
    global eth, contract_ARB, gasLimit
    account = web3.eth.account.privateKeyToAccount(privatekey)
    address_wallet = account.address
    try:
        ABI = abi.ARB
        contract = web3.eth.contract(address=contract_ARB, abi=ABI)
        gasPrice = intToDecimal(0.0000000001, 18)
        nonce = web3.eth.get_transaction_count(address_wallet)
        amount_out = contract.functions.getAmountsOut(Web3.toWei(amount, 'ether'), [eth, tokenToBue]).call()
        price = amount_out[1] / 1000000
        min_tokens = int(float(price) * (1 - slippage / 100))
        contract_txn = contract.functions.swapExactETHForTokens(
            min_tokens,  # amountOutMin
            [eth, tokenToBue],  # TokenSold, TokenBuy
            address_wallet,  # receiver
            (int(time.time()) + 10000)  # deadline
        ).buildTransaction({
            'from': address_wallet,
            'value': web3.toWei(amount, 'ether'),
            'gas': gasLimit,
            'gasPrice': gasPrice,
            'nonce': nonce,
        })
        signed_txn = web3.eth.account.sign_transaction(contract_txn, private_key=privatekey)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print(f'\n>>> swap {symbol} | https://nova-explorer.arbitrum.io/tx/{web3.toHex(tx_hash)}', flush=True)
        print(f'    {address_wallet}', flush=True)
    except Exception as error:
        print(f'\n>>> swap {symbol} error | {error}', flush=True)
        print(f'    {address_wallet}', flush=True)


def approve(privatekey, tokenToApprove, symbol):
    global contract_ARB, gasLimit
    account = web3.eth.account.privateKeyToAccount(privatekey)
    address_wallet = account.address
    try:
        contractToken = Web3.toChecksumAddress(tokenToApprove)
        ABI = abi.USDT
        token = web3.eth.contract(address=contractToken, abi=ABI)
        max_amount = web3.toWei(2 ** 64 - 1, 'ether')
        nonce = web3.eth.getTransactionCount(address_wallet)
        gasPrice = intToDecimal(0.0000000001, 18)
        tx = token.functions.approve(contract_ARB, max_amount).buildTransaction({
            'from': address_wallet,
            'value': 0,
            'gas': gasLimit,
            'gasPrice': gasPrice,
            'nonce': nonce
        })
        signed_txn = web3.eth.account.sign_transaction(tx, private_key=privatekey)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print(f'\n>>> {symbol} approve | https://nova-explorer.arbitrum.io/tx/{web3.toHex(tx_hash)}', flush=True)
        print(f'    {address_wallet}', flush=True)
    except Exception as error:
        print(f'\n>>> {symbol} approve error | {error}', flush=True)
        print(f'    {address_wallet}', flush=True)


def web_arb_sold(privatekey, tokenToSold, symbol):
    global contract_ARB, eth
    account = web3.eth.account.privateKeyToAccount(privatekey)
    address_wallet = account.address
    try:
        token = Web3.toChecksumAddress(tokenToSold)
        ABI = abi.ARB
        contract = web3.eth.contract(address=contract_ARB, abi=ABI)
        gasPrice = intToDecimal(0.0000000001, 18)
        nonce = web3.eth.get_transaction_count(address_wallet)
        token_sold = web3.eth.contract(address=tokenToSold, abi=abi.USDT)
        token_balance = token_sold.functions.balanceOf(address_wallet).call()
        amount_out = contract.functions.getAmountsOut(token_balance, [tokenToSold, eth]).call()
        price = Web3.fromWei(amount_out[1], 'ether')
        min_tokens = int(float(price) * (1 - slippage / 100))
        contract_txn = contract.functions.swapExactTokensForETH(
            token_balance,
            min_tokens,
            [token, eth],
            address_wallet,
            (int(time.time()) + 100000)
        ).buildTransaction({
            'from': address_wallet,
            'gas': gasLimit,
            'gasPrice': gasPrice,
            'nonce': nonce,
        })
        signed_txn = web3.eth.account.sign_transaction(contract_txn, private_key=privatekey)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print(f'\n>>> sold {symbol} | https://nova-explorer.arbitrum.io/tx/{web3.toHex(tx_hash)}', flush=True)
        print(f'    {address_wallet}', flush=True)
    except Exception as error:
        print(f'\n>>> {symbol} sold error | {error}', flush=True)
        print(f'    {address_wallet}', flush=True)


if __name__ == '__main__':
    print(f'\n============================================ Wiedzmin.eth =============================================')
    print(f'\nSubscribe to us : https://t.me/developercode1')
    print(f'\nПоддержи автора : 0xaC5d3F9f74c77821B624EC0830481E0608974fF7')
    with open("private_key.txt", "r") as f:
        keys_list = [row.strip() for row in f]
    RPC = "https://nova.arbitrum.io/rpc"
    web3 = Web3(Web3.HTTPProvider(RPC))

    def main():
        while keys_list:
            privatekey = keys_list.pop(0)
            if flag_approve == 1:
                for swap in swap_ARB:
                    approve(privatekey, swap['address'], swap['symbol'])
                    time.sleep(random.randint(20, 30))
            for _ in range(number_of_repetitions):
                for swap in swap_ARB:
                    web_arb_buy(privatekey, swap['amount'], swap['address'], swap['symbol'])
                    time.sleep(random.randint(20, 30))
                    web_arb_sold(privatekey, swap['address'], swap['symbol'])
                    time.sleep(random.randint(20, 30))
            print('\n' + web3.eth.account.privateKeyToAccount(privatekey).address + ' закончил работу', flush=True)

    for i in range(number_of_threads):
        thred = threading.Thread(target=main).start()
