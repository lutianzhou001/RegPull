import pandas as pd
import shared
shared.init()
from tqdm import tqdm

tokens = pd.read_csv("../../data/tokens.csv")['token_address']

features = []
for token in tqdm(tokens):
    try:
        transfers = pd.read_csv(f"/media/victor/Elements/data/Token_tx/{token}.csv")
        last_block = transfers['block_number'].iloc[-1]
        features.append({'token_address': token,
                         'inactive_transfers': 1 if shared.BLOCKSTUDY - last_block > 160000 else 0})

    except Exception as err:
        pass

pd.DataFrame(features).to_csv("../../data/transfer_heuristics.csv", index=False)
