from bs4 import BeautifulSoup
import requests


def obtain_tx_creation(token_address):
    """
    Gets token tx creation hash via web scrapping.

    Parameters
    ----------
    token_address: str
        string corresponding to token address

    Returns
    -------
        tx_creation hash if success, "Not found" otherwise.
    """

    tx_hash_creation = "Not found"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/'
                             '537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

    r = requests.get(f'https://etherscan.io/address/{token_address}', headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    soup2 = soup.find_all('div', 'col-md-8')
    for element in soup2:
        if "Creator Txn Hash" in str(element):
            for element2 in str(element).split():
                if 'href' and 'tx' in str(element2):
                    tx_hash_creation = str(element2[10:]).replace('"', '')
    if tx_hash_creation != "Not found":
        return tx_hash_creation
    return "Not found"


