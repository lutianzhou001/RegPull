import sys
import pandas as pd
sys.path.append("../")
import shared
shared.init()
import numpy as np
import json
from tqdm import tqdm


def get_features(reserves_dict, token_address, pool_address):
    liquidity, blocks, prices, weth = [], [], [], []

    for block, info in reserves_dict.items():
        blocks.append(block)
        liquidity.append(info['token'] * info['WETH'])
        prices.append(info['WETH']/info['token'])
        weth.append(info['WETH'])

    liquidity, blocks, price = np.array(liquidity), np.array(blocks), np.array(prices)
    try:
        idx_min_liq = np.argmax(np.maximum.accumulate(liquidity) - liquidity)  # end of the period
        idx_max_liq = np.argmax(liquidity[:idx_min_liq])
        liq_MDD = (liquidity[idx_min_liq] - liquidity[idx_max_liq])/liquidity[idx_max_liq]
        liq_RC = (liquidity[-1] - liquidity[idx_min_liq])/(liquidity[idx_max_liq] - liquidity[idx_min_liq])
    except:
        idx_min_liq, idx_max_liq, liq_MDD, liq_RC = 0, 0, 0, 0

    try:
        idx_min_price = np.argmax(np.maximum.accumulate(price) - price)  # end of the period
        idx_max_price = np.argmax(price[:idx_min_price])
        price_MDD = (price[idx_min_price] - price[idx_max_price])/price[idx_max_price]
        price_RC = (price[-1] - price[idx_min_price])/(price[idx_max_price] - price[idx_min_price])
    except:
        idx_min_price, idx_max_price, price_MDD, price_RC = 0, 0, 0, 0

    features_token = {
        'token_address': token_address,
        'pool_address': pool_address,
        'max_weth': max(weth),
        'first_sync_block': blocks[0],
        'last_sync_block': blocks[-1],
        'max_liq_block': blocks[idx_max_liq],
        'max_price_block': blocks[idx_max_price],
        'total_activity': len(blocks),
        'activity_from_max_to_min': len(liquidity[idx_max_liq:idx_min_liq])/len(liquidity),
        'activity_from_min': len(liquidity[idx_min_liq:])/len(liquidity),
        'inactive': 1 if shared.BLOCKSTUDY - blocks[-1] > 160000 else 0,
        'liq_MDD': liq_MDD,
        'liq_RC': liq_RC,
        'price_MDD': price_MDD,
        'price_RC': price_RC,
        'late_creation': 1 if shared.BLOCKSTUDY - blocks[0] < 160000 else 0
    }

    return features_token


def get_dict_reserves(decimal, pool_address, weth_position):
    with open(f'/media/victor/Elements/data/pool_sync_events/{pool_address}.json') as f:
        events = json.loads(f.read())
    f.close()

    if len(events) < 5:
        return False

    token_position = 1 - WETH_position
    reserves = {}

    for event in events:
        reserves[event['blockNumber']] = {
            'WETH':  event['args'][f'reserve{weth_position}'] / 10 ** 18,
            'token': event['args'][f'reserve{token_position}'] / 10 ** decimal
        }

    return reserves

with open('../../data/pools_of_token.json', 'r') as f:
    pool_of_token = json.loads(f.read())

decimals       = pd.read_csv('../../data/decimals.csv', index_col="token_address")
token_features = {}
WETH_pools     = pool_of_token[shared.WETH]

for pool in tqdm(WETH_pools):
    try:

        WETH_position = 1 if shared.WETH == pool['token1'] else 0
        reserves_dict = get_dict_reserves(decimals.loc[pool[f'token{1 - WETH_position}']].iloc[0],
                                          pool['address'], WETH_position)
        if reserves_dict:
            features = get_features(reserves_dict, pool[f'token{1 - WETH_position}'], pool['address'])
            token_features[pool[f'token{1 - WETH_position}']] = features

    except Exception as err:
        print(err)
        pass

df = pd.DataFrame(token_features).transpose()
df.to_csv("../../data/pool_heuristics.csv", index=False)

