
def daily_pool_events(events):
    Mint, Burn, Transfer = 0, 0, 0
    i = 0
    features = []
    while i < len(events):
        if events[i]['type'] == "Mint":
            Mint += 1
        if events[i]['type'] == "Burn":
            Burn += 1
        if events[i]['type'] == "Transfer":
            Transfer += 1
        i += 1
    features = {
        'num_transactions': Mint,
        'n_unique_addresses': Burn,
        'cluster_coeff': Transfer
    }


    return features


