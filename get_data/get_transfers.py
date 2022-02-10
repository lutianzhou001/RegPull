
import pandas as pd
from web3 import Web3

from Utils.abi_info import obtain_hash_event
from Utils.api import get_logs
import shared
shared.init()


def get_transfers(token_address, out_path, start_block, end_block, decimal=18):
    """
    Get transfer logs for a given token and period.
    This function saves transfers as a csv in out_path.

    Parameters
    ----------
    token_address : str
        Token address.
    out_path : str
        Path to output directory.
    decimal: float
        Token decimal (usually 18).
    start_block: int
        Starting block.
    end_block: int
        Ending block.
    """

    # Initialise contract objects and get the transactions.
    try:
        contract = shared.web3.eth.contract(Web3.toChecksumAddress(token_address), abi=shared.ABI)
        transfers = get_logs(contract, "Transfer", hash_log, start_block, end_block, number_batches=1)
    except Exception as err:
        print(f"Exception occured: {err}")
        return

    # Save txs in a Dataframe.
    txs = [[transaction['transactionHash'].hex(), transaction["blockNumber"], transaction["args"]['from'],
            transaction["args"]['to'], transaction["args"]['value'] / 10 ** decimal] for transaction in transfers]
    transfers = pd.DataFrame(txs, columns=["transactionHash", "block_number", "from", "to", "value"])
    transfers.to_csv(out_path + "/" + token_address + ".csv", index=False)
    return


hash_log = obtain_hash_event('Transfer(address,address,uint256)')
# get_transfers('0xa150Db9b1Fa65b44799d4dD949D922c0a33Ee606', './', 11000000, 11025824) # example
