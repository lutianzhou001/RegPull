from get_data.get_tokens_pools import *
from get_data.get_contract_creation import *
from get_data.get_decimals import *
from get_data.get_pool_events import *
from get_data.get_contract_creation import *
from Utils.eth_utils import *
from Utils.api import *
from get_data.get_transfers import *
from ML.Labelling.extract_pool_heuristics import *
import csv
from tempfile import NamedTemporaryFile
import shutil
import pandas as pd
from tqdm import tqdm

tokens = './data/tokens.csv'
decimals = './data/decimals.csv'
countries = './data/countries.csv'
header = ['token_address', 'decimal']


if __name__ == '__main__':
    # Step1: we need to get tokens and pools first.
    # get_token_and_pools("./data", dex='uniswap_v2')
    # # Step2: we need to get the decimals;
    # with open(tokens, "r") as tokens_file:
    #     reader = csv.DictReader(tokens_file)
    #     with open(decimals, "w") as decimals_file:
    #         writer = csv.writer(decimals_file)
    #         writer.writerow(header)
    #     for token in reader:
    #         temp_token_address = token['token_address']
    #         token["decimal"] = get_decimal_token(token['token_address'])
    #         with open(decimals, "a") as decimals_file:
    #             writer = csv.writer(decimals_file)
    #             writer.writerow([token['token_address'], token['decimal']])

    # Step3: get transfers
    #with open('./data/tokens.csv', 'r') as tokens_file:
    #    reader = csv.DictReader(tokens_file)
    #    for token in tqdm(reader):
    #        token["decimal"] = get_decimal_token(token['token_address'])
    #        with open(decimals, "a") as decimals_file:
    #            writer = csv.writer(decimals_file)
    #            writer.writerow([token['token_address'], token['decimal']])
    #        create_tx = obtain_tx_creation(token['token_address'])
    #        receipt = get_rpc_response("eth_getTransactionReceipt",[[create_tx]])
    #        get_transfers(token['token_address'], './data/transfers',int(receipt[0]['result']['blockNumber'],16),14860000, token['decimal'])

    # # Step4: extract pool heuristics
    print("Step4: get sync events and token features ")
    with open('./data/pools_of_token.json', 'r') as f:
        pool_of_token = json.loads(f.read())

    decimals = pd.read_csv('./data/decimals.csv', index_col="token_address")
    token_features = {}
    WETH_pools = pool_of_token[shared.WETH]

    for pool in tqdm(WETH_pools):
        print("executing pool", pool)
        # with this pool address, we need to get the events
        try:
            get_pool_events("Sync", "0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1", pool['address'],"./data",pool['creation'],14860000)
        except:
            print("Error in getting sync events for pool: ", pool['address'])
        try:
            WETH_position = 1 if shared.WETH == pool['token1'] else 0
            reserves_dict = get_dict_reserves(decimals.loc[pool[f'token{1 - WETH_position}']].iloc[0],pool['address'], WETH_position)
            if reserves_dict:
                features = get_features(reserves_dict, pool[f'token{1 - WETH_position}'], pool['address'])
                token_features[pool[f'token{1 - WETH_position}']] = features
                with open('./data/token_features', "a") as token_features_file:
                    writer = csv.writer(decimals_file)
                    writer.writerow(token_features)
        except Exception as err:
            print(err)
            pass
    df = pd.DataFrame(token_features).transpose()
    df.to_csv("./data/pool_heuristics.csv", index=False)
