import sys

import pandas as pd

sys.path.append("../")
import shared
shared.init()
from Utils.eth_utils import *
from Utils.api import *

tokens = pd.read_csv("../data/tokens.csv")
tokens_dic = dict.fromkeys(tokens["token_address"], 0)

_,web3 = connect_to_web3()

decimals_json = []
token_contract = {}
for subset_token in chunks(tokens_dic,50):
    for token in subset_token:
        token_contract[token] = web3.eth.contract(token,abi = shared.ABI)
    decimals_json += get_decimals_multicall(token_contract,10)
    token_contract = {}

token_decimals = {Web3.toChecksumAddress(element['contract_address']):element['results'][0] for element in decimals_json}

pd.DataFrame({'token_address': token_decimals.keys(), 'decimal': token_decimals.values()}).to_csv(
    "../data/decimals.csv", index=False)