from web3 import Web3, HTTPProvider
import shared
shared.init()
from Utils.api import get_logs
from itertools import islice


def connect_to_web3():
    """
    Connect to Web3 server.

    Parameters
    ----------

    Returns
    -------
    res: bool
        True if connection was succeeded, otherwise False
    web3: Web3 Object
    """
    web3 = Web3(HTTPProvider('https://mainnet.infura.io/v3/d6243bb783b44485ad6636b6c3411377'))
    res = web3.isConnected()
    return res, web3


def split_chunks(data, n_elements):
    """
    Splitting the calls to aggregate them properly.

    Parameters
    ----------
    data: np.array
        Containing calls
    n_elements: int
        Calls we want to aggregate

    Returns
    -------
    chunks: list
        Calls in chunks
    """

    chunks = []
    n = len(data)
    
    if n % n_elements != 0:
        n_chunks = int(n/n_elements)+1

    else:
        n_chunks = int(n/n_elements)
            
    for  i in range(n_chunks-1):
        chunk = data[i*n_elements:(i+1)*n_elements]
        chunks.append(chunk)

    chunks.append(data[(n_chunks-1)*n_elements:]) 
    return chunks


def chunks(data, SIZE=10000):
    it = iter(data)
    for i in range(0, len(data), SIZE):
        yield {k:data[k] for k in islice(it, SIZE)}


def get_pools(dex, factory): #v2 or sushi
    """
    Parameters
    ----------
    dex : str
        Choose the DEX you want to get the pools from
    factory : web3.eth.contract
        factory get_contracts of dex

    Returns
    -------
    pool_dic: Dict[str, float]
        pool dictionary with the attributes 'address','dex','token0','token1','reserves0','reserves1','creation'
    """

    hash_create = '0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9'
    if dex == 'uniswap_v2':
        from_block = 10008355
        to_block = shared.BLOCKSTUDY
        number_batches = 20
        pools = get_logs(factory, 'PairCreated', hash_create, from_block, to_block, number_batches)
    
    if dex == 'sushiswap':
        from_block = 10822038
        to_block = shared.BLOCKSTUDY
        number_batches = 20
        pools = get_logs(factory, 'PairCreated', hash_create, from_block, to_block, number_batches)

    pool_dic = {}
    tokens = {}
    for pool in pools:
        pool_address = pool.args.pair
        token0 = pool.args.token0
        token1 = pool.args.token1
        tokens.update({token0:None})
        tokens.update({token1:None})
        pool_dic.update({pool_address:{ 'address':pool_address,
                                        'dex':dex,
                                        'token0':token0,
                                        'token1':token1,
                                        'reserves0':None,
                                        'reserves1':None,
                                        'creation':pool.blockNumber}})   

    return pool_dic, tokens


def events_to_json(events):
    json_events = []
    for event in events:
        event_dict = dict(event)
        # event_dict.pop('transactionHash')
        event_dict['transactionHash'] = event_dict['transactionHash'].hex()
        event_dict.pop('blockHash')
        event_dict['args'] = dict(event.args)
        json_events.append(event_dict)
       
    return json_events