import concurrent.futures
import sys
sys.path.append("../")
from Utils.eth_utils import *
import pandas as pd

res, web3 = connect_to_web3()
txs_creation = pd.read_csv("../data/tx_creation.csv")
token_list, hash_creation_list = txs_creation["token_address"].tolist(), txs_creation["tx_hash_creation"].tolist()
block_number_creation_list = []

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as exec:
    for token, hash_creation in zip(token_list, hash_creation_list):
        block_number_creation_list.append([token, exec.submit(web3.eth.get_transaction, hash_creation)])
    for i in range(len(block_number_creation_list)):
        print(i, len(block_number_creation_list))
        try:
            block_number_creation_list[i][1] = block_number_creation_list[i][1].result()["blockNumber"]
        except Exception as err:
            print(err)

pd.DataFrame(block_number_creation_list, columns=["token_address","block_creation"]).to_csv(
    "../data/block_creation.csv", index=False)

