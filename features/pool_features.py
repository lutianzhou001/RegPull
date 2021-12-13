
def get_pool_features(syncs, position, decimal, timestamp_limit, timestamp_creation):

    syncs = syncs.loc[syncs.timestamps < timestamp_limit]
    syncs['reserve0'] = syncs['reseve0']
    WETH = syncs[f'reserve{position}']/10 ** 18
    TOKEN = syncs[f'reserve{1-position}']/10 ** decimal
    PRICES = WETH/TOKEN
    LIQUIDITY = WETH * TOKEN
    BLOCKS = syncs["block_number"]

    features = {
        'blocks': len(BLOCKS),
        'wmatic': WETH.iloc[-1],
        'prices': PRICES.iloc[-1],
        'liquidity': LIQUIDITY.iloc[-1],
        'difference_creation_sync': timestamp_creation - syncs['timestamps'].iloc[0]
    }
    return features
