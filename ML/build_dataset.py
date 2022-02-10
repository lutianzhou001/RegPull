import pandas as pd
import json
from numpy.random import choice

import shared
shared.init()
from features.pool_features import get_pool_features
from features.transfer_features import get_transfer_features, get_curve

df = pd.read_csv("Labelling/labeled_list.csv", index_col="token_address")
pool_features = pd.read_csv("../data/pool_heuristics.csv", index_col="token_address")
decimals = pd.read_csv("../data/decimals.csv", index_col="token_address")
with open('../data/pools_of_token.json', 'r') as f:
    pool_of_token = json.loads(f.read())
WETH_pools = pool_of_token[shared.WETH]
WETH_pool_address = {pool_info['address']: pool_info for pool_info in WETH_pools}  # Set pool address as key

iteration = 0
final_dataset = []
for address, label, _type in zip(df.index.tolist(), df['label'], df['type']):

    try:
        features = pool_features.loc[address]
        pool_address = features['pool_address']
        pool_info = WETH_pool_address[pool_address]

        first_block, last_block = int(features['first_sync_block']), features['max_liq_block'] if _type == 1 else \
            features['max_price_block'] if _type == 2 else features['last_sync_block']

        list_of_blocks = list((range(first_block, last_block, 1)))
        eval_blocks = sorted(choice(list_of_blocks, 5)) if label == 1 else sorted(choice(list_of_blocks, 1))

        try:
            transfers = pd.read_csv(f"/media/victor/Elements/data/Token_tx/{address}.csv")
            with open(f'/media/victor/Elements/data/pool_lptransfers/{pool_features.loc[address]["pool_address"]}.json',
                      'r') as f:
                lp_transfers = json.loads(f.read())
                lp_transfers = pd.DataFrame([[info['transactionHash'], info['blockNumber']] + list(info['args'].values())
                                             + [info['type']] for info in lp_transfers])

            lp_transfers.columns = list(transfers.columns) + ['type']
            # Pool features
            with open(f'/media/victor/Elements/data/pool_sync_events/{pool_address}.json', 'r') as f:
                syncs = json.loads(f.read())
            syncs = pd.DataFrame([[info['blockNumber']] + list(info['args'].values()) for info in syncs])
            syncs.columns = ['blockNumber', 'reserve0', 'reserve1']

        except Exception as err:
            print(err)
            continue

        WETH_position = 1 if shared.WETH == pool_info['token1'] else 0
        decimal = decimals.loc[address].iloc[0]

        for eval_block in eval_blocks:
            computed_features = {}

            # Transfer Features
            computed_features.update({'token_address': address, 'eval_block': eval_block})
            computed_features.update(get_transfer_features(transfers.loc[transfers.block_number < eval_block].values))
            computed_features.update(get_curve(transfers.loc[transfers.block_number < eval_block].values))

            computed_features.update({'liq_curve': get_curve(
                lp_transfers.loc[lp_transfers.block_number < eval_block].values)['tx_curve']})

            transfer_types = lp_transfers.loc[lp_transfers.block_number < eval_block]['type'].value_counts()
            computed_features.update({'Mint': 0, 'Burn': 0, 'Transfer': 0})
            for type_ in transfer_types.index:
                computed_features[type_] = transfer_types[type_]
            computed_features.update(
                {'difference_token_pool': lp_transfers['block_number'].iloc[0] - transfers['block_number'].iloc[0]}
            )
            computed_features.update(get_pool_features(syncs.loc[syncs.blockNumber < eval_block], WETH_position, decimal))

            final_dataset.append(computed_features)
        iteration += 1
        print(iteration, len(df))
    except:
        pass

pd.DataFrame(final_dataset).to_csv("X.csv", index=False)
