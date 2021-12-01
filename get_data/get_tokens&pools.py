import sys
import pandas as pd
sys.path.append("../")
import shared
shared.init()
from Utils.eth_utils import *
import json

_,web3 = connect_to_web3()

factory = web3.eth.contract(shared.UNISWAP_FACTORY, abi=shared.ABI_FACTORY)
pool_dic, tokens = get_pools('uniswap_v2', factory)
    
pd.DataFrame(tokens.keys(), columns=["token_address"]).to_csv("../data/tokens.csv", index=False)

inverted_pool_dict = dict()
print('Pools downloaded')

for pool in pool_dic.keys():
    try:
        inverted_pool_dict[pool_dic[pool]['token0']].append(pool_dic[pool])
    except:
        inverted_pool_dict[pool_dic[pool]['token0']] = [pool_dic[pool]]
    try:
        inverted_pool_dict[pool_dic[pool]['token1']].append(pool_dic[pool])
    except:
        inverted_pool_dict[pool_dic[pool]['token1']] = [pool_dic[pool]]

with open("../data/pools_of_token.json", "w") as outfile:
    json.dump(inverted_pool_dict, outfile)
print('Inverted Dict')
# for token in inverted_pool_dict:
#     with open("../data/Token_pools/" + token + ".json", "w") as outfile:
#         json.dump(inverted_pool_dict[token], outfile)
# print('job done')