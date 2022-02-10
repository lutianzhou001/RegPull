import json
import requests
import shared
shared.init()


def get_source_code(token_address, out_path):
    """
    Obtains token source code/abi and saves in json format.

    Parameters
    ----------
    token_address: str
        token address in checksum format.
    out_path : str
        Path to output directory.
    """

    source_code_endpoint = "https://api.etherscan.io/api?" \
                           "module=contract" \
                           "&action=getsourcecode" \
                           f"&address={token_address}" \
                           f"&apikey={shared.API_KEY}"
    source_code = json.loads(requests.get(source_code_endpoint).text)['result']

    with open(f"{out_path}/{token_address}.json", "w") as outfile:
        json.dump(source_code, outfile)
    outfile.close()
