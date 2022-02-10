
def get_pool_features(syncs, position, decimal):
    """
    Compute all features from sync events.

    Parameters
    ----------
    syncs: Dataframe
        with pool syncs
    position: int
        1 if WETH is token1 else 0
    decimal: float
        token decimals

    Returns
    -------
        tx_creation hash if success, "Not found" otherwise.
    """

    WETH = syncs[f'reserve{position}']/10 ** 18
    TOKEN = syncs[f'reserve{1-position}']/10 ** decimal
    PRICES = WETH/TOKEN
    LIQUIDITY = WETH * TOKEN
    BLOCKS = syncs["blockNumber"]

    features = {
        'n_syncs': len(BLOCKS),
        'WETH': WETH.iloc[-1],
        'prices': PRICES.iloc[-1],
        'liquidity': LIQUIDITY.iloc[-1],
    }

    return features
