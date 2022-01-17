import requests
import json
from web3.datastructures import AttributeDict
from hexbytes import HexBytes
import sys
sys.path.append("../")
import shared
shared.init()


def get_rpc_response(method, list_params=[]):
    url = shared.INFURA_URL
    list_params = list_params or []
    data = [{"jsonrpc": "2.0", "method": method, "params": params, "id": 1} for params in list_params]
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=data)
    return response.json()


def change_log_dict(log_dict):
    dictionary = log_dict.copy()
    dictionary['blockHash'] = HexBytes(dictionary['blockHash'])
    dictionary['blockNumber'] = int(dictionary['blockNumber'], 16)
    dictionary['logIndex'] = int(dictionary['logIndex'], 16)
    for i in range(len(dictionary['topics'])):
        dictionary['topics'][i] = HexBytes(dictionary['topics'][i])
    dictionary['transactionHash'] = HexBytes(dictionary['transactionHash'])
    dictionary['transactionIndex'] = int(dictionary['transactionIndex'], 16)
    return AttributeDict(dictionary)


def clean_logs(contract, myevent, log):
    log_dict = AttributeDict({'logs': log})
    eval_string = 'contract.events.{}().processReceipt({})'.format(myevent, log_dict)
    args_event = eval(eval_string)[0]
    return args_event


def get_logs(contract, myevent, hash_create, from_block, to_block, number_batches):
    """
    Get event logs using recursion.

    Args:
        contract: web3 contract object that contains the event
        myevent: string with event name
        hash_create: hash of the event
        from_block: int
        to_block: int
        number_batches: infura returns just 10k logs each call,
        therefore we need to split time series into batches.

    Returns:
        List with all clean blocks.
    """

    events_clean = []
    block_list = [int(from_block + i * (to_block - from_block) / number_batches) for i in range(0, number_batches)] + [
        to_block]

    block_list[0] -= 1
    list_params = [[{"address": contract.address,
                     "fromBlock": hex(block_list[i - 1] + 1),
                     "toBlock": hex(block_list[i]),
                     "topics": [hash_create]}] for i in range(1, number_batches + 1)]

    logs = get_rpc_response("eth_getLogs", list_params)
    for j, log in enumerate(logs):
        if list(log.keys())[-1] == "result":
            for event in log['result']:
                log_dict = change_log_dict(event)
                events_clean += [clean_logs(contract, myevent, [log_dict])]
        else:
            events_clean += get_logs(contract, myevent, hash_create, int(list_params[j][0]["fromBlock"], 16),
                                     int(list_params[j][0]["toBlock"], 16), 15)
    return events_clean
