import pandas as pd
import json

import shared
from Utils.eth_utils import get_pools
shared.init()


def get_token_and_pools(out_path, dex='uniswap_v2'):
    """
    Get tokens and pools from sushiswap or uniswap_v2.

    Parameters
    ----------
    out_path : str
        Path to output directory.
    dex : str
        sushiswap or uniswap_v2 are currently allowed.
    """

    factory = shared.web3.eth.contract(shared.UNISWAP_FACTORY, abi=shared.ABI_FACTORY)
    pool_dic, tokens = get_pools(dex, factory)
    pd.DataFrame(tokens.keys(), columns=["token_address"]).to_csv(f"{out_path}/tokens.csv", index=False)

    with open(f"{out_path}/pool_dict.json", "w") as outfile:
        json.dump(pool_dic, outfile)

    inverted_pool_dict = dict()
    for pool in pool_dic.keys():
        try:
            inverted_pool_dict[pool_dic[pool]['token0']].append(pool_dic[pool])
        except:
            inverted_pool_dict[pool_dic[pool]['token0']] = [pool_dic[pool]]
        try:
            inverted_pool_dict[pool_dic[pool]['token1']].append(pool_dic[pool])
        except:
            inverted_pool_dict[pool_dic[pool]['token1']] = [pool_dic[pool]]

    with open(f"{out_path}/pools_of_token.json", "w") as outfile:
        json.dump(inverted_pool_dict, outfile)

    print('Tokens and Pools downloaded!')


# get_token_and_pools("../data", dex='uniswap_v2')