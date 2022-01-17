import os
import time

from Utils.abi_info import obtain_hash_event
from Utils.eth_utils import *
from Crypto.Hash import keccak
from Utils.api import *
import pandas as pd
import concurrent.futures
import shared


def dict_to_df(transfers, decimal):
    """
    Args:
        transfers: list with token transfer log
        decimal: int corresponding to token decimals

    Returns:
        dataframe containing logs
    """
    txs = []
    for trans in transfers:
        keys = list(trans["args"].keys())
        txs.append([trans['transactionHash'].hex(), trans["blockNumber"], trans["args"][keys[0]], trans["args"][keys[1]],
                    trans["args"][keys[2]] / 10 ** decimal])
    return pd.DataFrame(txs, columns=["transactionHash", "block_number", "from", "to", "value"])


def get_transfers(token_addr, token_info, abi):
    """

    Args:
        token_addr:
        token_info:
        abi:

    Returns:

    """
    decimal = token_info.loc[token_info['token_address'] == token_addr]["decimal"].iloc[0]
    block_creation = int(token_info.loc[token_info['token_address'] == token_addr]["block_creation"].iloc[0])

    #Inicialitzem objecte contracte i busquem demanem les transaccions
    try:
        contract = web3.eth.contract(Web3.toChecksumAddress(token_addr), abi=abi)
        transfers = get_logs(contract, "Transfer", hash_log, block_creation, shared.BLOCKSTUDY, 15)
    except Exception as err:
        print(f"Exception occured: {err}")
        return

    #Imprimim transaccions csv
    dict_to_df(transfers, decimal).to_csv("/media/victor/Elements/Token_tx/" + str(token_addr) + ".csv", index=False)
    return


start_time = time.time()

res, web3 = connect_to_web3()
token_info = pd.read_csv("../data/raw_table_data.csv") #obrim csv amb info de tots els tokens

hash_log = obtain_hash_event('Transfer(address,address,uint256)')

files = os.listdir('/media/victor/Elements/Huge_token_tx/')
token_transfers_list = [file.split(".")[0] for file in files]
healthy_tokens = pd.read_csv("../data/healthy_tokens.csv")['Address'].tolist()

Uniswap_token_address = '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984'
f = open(f'../data/Contract_abis/{Uniswap_token_address}.json')  # obrim json abis
abi = json.load(f)

huge_tokens = ['0xdac17f958d2ee523a2206206994597c13d831ec7', '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
               '0x6b175474e89094c44da98b954eedeac495271d0f', '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984',
               '0x6b3595068778dd592e39a122f4f5a5cf09c90fe2', '0x514910771af9ca656af840dff83e8264ecf986ca',
               '0x8e870d67f660d95d5be530380d0ec0bd388289e1']

features = []
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as exec:
    for i, token_addr in enumerate(token_info['token_address'].tolist()):
        if token_addr not in token_transfers_list and token_addr not in healthy_tokens \
                and token_addr.lower() not in huge_tokens:
            # Assignem worker diferent per a cada token
            features.append(exec.submit(get_transfers, token_addr, token_info, abi))

for i, feat in enumerate(features):
    feat.result()


