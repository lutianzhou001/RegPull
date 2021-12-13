import pandas as pd
import json
from numpy.random import choice

from features.transfer_features import get_transfer_features, get_curve

df = pd.read_csv("Labelling/labeled_list.csv", index_col="token_address")
pool_features = pd.read_csv("../data/pool_heuristics.csv", index_col="token_address")
decimals = pd.read_csv('/media/victor/Elements/data/decimals.csv', index_col="token_address")
with open('../data/pools_of_token.json', 'r') as f:
    pool_of_token = json.loads(f.read())

X = []
iteration = 0
for address, label, type in zip(df.index.tolist(), df['label'], df['type']):
    try:
        features = pool_features.loc[address]
        first_block, last_block = int(features['first_sync_block']), features['max_liq_block'] if type == 1 else features['max_price_block'] if type == 2 else features['last_sync_block']
        list_of_blocks = list((range(first_block, last_block, 1)))
        eval_blocks = sorted(choice(list_of_blocks, 3))
        for eval_block in eval_blocks:
            transfers = pd.read_csv(f"/media/victor/Elements/data/Token_tx/{address}.csv")
            #get_transfer_features(transfers.loc[transfers.block_number < eval_block].values)
            get_curve(transfers.loc[transfers.block_number < eval_block].values)

            with open(f'/media/victor/Elements/data/pool_lptransfers/{pool_features.loc[address]["pool_address"]}.json', 'r') as f:
                lp_transfers = json.loads(f.read())
                lp_transfers = [transfer['args'] for transfer in lp_transfers]
                lp_transfers = pd.DataFrame(lp_transfers)
            print(transfers)
        iteration += 1

    except Exception as err:
        print(err)

pd.DataFrame(X).to_csv("X.csv", index=False)