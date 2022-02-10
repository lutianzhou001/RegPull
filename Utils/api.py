import requests
from web3.datastructures import AttributeDict
from hexbytes import HexBytes
import sys
sys.path.append("../")
import shared
shared.init()


def get_rpc_response(method, list_params=[]):
    """
    Parameters
    ----------
    method: str
        Indicates node method.
    list_params: List[Dict[str, Any]]
        List of request parameters.

    Returns
    -------
    args_event: AttributeDict
        Change number basis.

    Example
    -------
        If we want token transfers of 0xa150Db9b1Fa65b44799d4dD949D922c0a33Ee606
        between blocks [11000000, 11025824] then:
        method: 'eth_getLogs'
        list_params: [[{'address': '0xa150Db9b1Fa65b44799d4dD949D922c0a33Ee606',
                    'fromBlock': '0xa7d8c0', 'toBlock': '0xa83da0',
                    'topics': ['0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef']}]]
    """
    url = shared.INFURA_URL
    list_params = list_params or []
    data = [{"jsonrpc": "2.0", "method": method, "params": params, "id": 1} for params in list_params]
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=data)
    return response.json()


def change_log_dict(log_dict):
    """
    Parameters
    ----------
    log_dict: AttributeDict
        Decoded logs.

    Returns
    -------
    args_event: AttributeDict
        Change number basis.
    """
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
    """
    Parameters
    ----------
    contract: web3.eth.contract
        Contract that contains the event.
    myevent: str
        string with event name.
    log: List[AttributeDict]
        List containing raw node response.

    Returns
    -------
    args_event: AttributeDict
        Decoded logs.
    """
    log_dict = AttributeDict({'logs': log})
    eval_string = 'contract.events.{}().processReceipt({})'.format(myevent, log_dict)
    args_event = eval(eval_string)[0]
    return args_event


def get_logs(contract, myevent, hash_create, from_block, to_block, number_batches):
    """
    Get event logs using recursion.

    Parameters
    ----------
    contract: web3.eth.contract
        Contract that contains the event.
    myevent: str
        string with event name.
    hash_create: str
        hash of the event.
    from_block: int
        Starting block.
    to_block: int
        Ending block.
    number_batches: int
        infura returns just 10k logs each call, therefore we need to split time series into batches.

    Returns
    -------
    events_clean: list
        List with all clean logs.
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
