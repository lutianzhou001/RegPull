import concurrent.futures
import json
import time
from itertools import cycle
import requests
import pandas as pd
import os

def make_call(addr, apikey):
    while True:
        try:
            abi_endpoint = "https://api.etherscan.io/api?module=contract&action=getsourcecode&address=" + addr \
                           + "&apikey=" + apikey
            abi = json.loads(requests.get(abi_endpoint).text)['result']
            return abi
        except Exception as err:
            print(err)
            time.sleep(10)

def get_source_code(addr, apikey):
    abi = make_call(addr, apikey)
    with open("../data/Source_codes/" + str(addr) + ".json", "w") as outfile:
       json.dump(abi, outfile)
    outfile.close()

keys = ["TKU2HQIWWAU3ZJ2DCN8MU9Q6Y1ZM5CATD1",
        "BSUU63STBIBBX9MZMCEVUGWFW233SUJ14B",
        "N6V5MSDF8G8PX6QSY9G31RMXGS3Q1AX22D"]
keys_pool = cycle(keys)

# Opoen csv with all tokens
address = []
tokens = pd.read_csv("../data/tokens.csv")["token_address"].tolist()

# Get files in Contract abis Folder
files = os.listdir("../data/Source_codes")
contract_source_code = [file.split(".")[0] for file in files]

# Set all workers with diferent api keys
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as exec:
    for token in tokens:
        if token not in contract_source_code:
            address.append(exec.submit(get_source_code, token, next(keys_pool)))
    exec.shutdown(False)  # workers will terminate as soon as all features finish

for j, add in enumerate(address):
    # Start new worker
        add.result()
