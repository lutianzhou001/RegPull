import time
import pandas as pd
from bs4 import BeautifulSoup
import requests


def _obtain_tx_creation(addr):
    """
        Gets token tx creation hash via scrapping
    Args:
        addr: string corresponding to token address

    Returns:
        Either tx_creation hash or "Not found"
    """

    tx_hash_creation = "Not found"
    MAX_TRIES = 20

    for i in range(MAX_TRIES):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/'
                                     '537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

            r = requests.get('https://etherscan.io/address/' + addr, headers=headers)
            soup = BeautifulSoup(r.content, 'html.parser')
            soup2 = soup.find_all('div', 'col-md-8')
            for element in soup2:
                if "Creator Txn Hash" in str(element):
                    for element2 in str(element).split():
                        if 'href' and 'tx' in str(element2):
                            tx_hash_creation = str(element2[10:]).replace('"', '')
            if tx_hash_creation != "Not found":
                return tx_hash_creation
            else:
                time.sleep(1)

        except Exception as err:
            print(err)

    return "Not found"


# Read csv with all tokens
tokens = pd.read_csv("../data/tokens.csv")["token_address"].tolist()

try:
    tx_creation_df = pd.read_csv("../data/tx_creation.csv")
    tokens_already_checked, tx_creation_list = tx_creation_df["token_address"].tolist(), tx_creation_df.values.tolist()

except:
    tokens_already_checked, tx_creation_list = [], []

for i, token in enumerate(tokens):
    if token not in tokens_already_checked:
        creation_tx = _obtain_tx_creation(token)
        tx_creation_list.append([token, creation_tx])

pd.DataFrame(tx_creation_list, columns=["token_address", "tx_hash_creation"]).\
    to_csv("../data/tx_creation.csv", index=False)