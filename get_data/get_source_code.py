import os
import time
import concurrent.futures

import json
import requests
import pandas as pd
import shared
shared.init()


def make_call(addr, apikey):
    """
        execute etherscan call
    Args:
        addr: token address in string format
        apikey: etherscan apikey

    Returns:
        dict with source code
    """
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
    """
        obtains token source code and saves in json format
    Args:
        addr: token address in string format
        apikey: etherscan apikey

    """
    abi = make_call(addr, apikey)
    with open("../data/Source_codes/" + str(addr) + ".json", "w") as outfile:
       json.dump(abi, outfile)
    outfile.close()


# Open csv with all tokens
address = []
tokens = pd.read_csv("../data/tokens.csv")["token_address"].tolist()

# Get files in Contract abis Folder
files = os.listdir("../data/Source_codes")
contract_source_code = [file.split(".")[0] for file in files]

# Set all workers with diferent api keys
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as exec:
    for token in tokens:
        if token not in contract_source_code:
            address.append(exec.submit(get_source_code, token, shared.ETHERSCAN_API_KEY))
    exec.shutdown(False)  # workers will terminate as soon as all features finish

for j, add in enumerate(address):
    # Start new worker
        add.result()
