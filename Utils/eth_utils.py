from web3 import Web3, HTTPProvider
import shared
shared.init()
from shared import web3, multicall
from Utils.api import get_logs
from itertools import islice


def connect_to_web3():
    """
    Connect to Web3 server.
    Args:
    Returns:
      res: Boolean indicating that connection was succeed or not.
      web3: Web3 Object
    """
    web3 = Web3(HTTPProvider('https://mainnet.infura.io/v3/d6243bb783b44485ad6636b6c3411377'))
    res = web3.isConnected()
    return res, web3

def split_chunks(data,n_elements):
    '''
    splitting the calls to aggregate them properly
    Args:
        data = array containing calls
        n_elements = Int. Calls we want to aggregate
    Returns:
        calls in chunks 
    '''
    chunks = []
    n = len(data)
    
    if(n % n_elements!=0):
        n_chunks = int(n/n_elements)+1

    else:
        n_chunks = int(n/n_elements)
            
    for  i in range(n_chunks-1):
        chunk = data[i*n_elements:(i+1)*n_elements]
        chunks.append(chunk)

    chunks.append(data[(n_chunks-1)*n_elements:]) 
    return chunks

def get_decimals(tokens_contracts,number_agg):
    'Get decimals of tokens'
    json_results = []
    calls = []
    for _,contract in tokens_contracts.items():
            calls.append(contract.functions.decimals())
    calls_splited = split_chunks(calls,int(len(calls)/number_agg))
    for call in calls_splited:
        try:
            json_results += multicall.aggregate(call,shared.BLOCKSTUDY).json['results']
        except:         
            json_results += multicall_aggregator(call)

    return json_results

def multicall_aggregator(call):
    try:
        result = multicall.aggregate(call,shared.BLOCKSTUDY).json['results']
    except:
        if len(call) > 1:
            split_call = split_chunks(call,int(len(call)/2))
            result1 = multicall_aggregator(split_call[0])
            result2 = multicall_aggregator(split_call[1])
            result = result1+result2
        else:
            try:
                result = multicall.aggregate(call,shared.BLOCKSTUDY).json['results']
            except:
                result = []
    return result

def get_decimal_token(token_address):
    try:
        contract = web3.eth.contract(token_address,abi = shared.ABI)
        decimals = contract.functions.decimals().call()
    except:
        decimals = None
    return decimals

def chunks(data, SIZE=10000):
    it = iter(data)
    for i in range(0, len(data), SIZE):
        yield {k:data[k] for k in islice(it, SIZE)}

def get_pools(dex, factory): #v2 or sushi
    '''
    Args:
        dex = String. Choose the DEX you want to get the pools from
        factory = factory get_contracts of dex
    Returns:
        pool dictionary with the attributes 'address','dex','token0','token1','reserves0','reserves1','creation'
    '''
    # _,web3 = connect_to_web3()
    hash_create = '0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9'
    if dex == 'uniswap_v2':
        from_block = 10008355
        #from_block = get_latest_block()-1000
        to_block = shared.BLOCKSTUDY
        number_batches = 20
        pools = get_logs(factory,'PairCreated',hash_create,from_block,to_block,number_batches)
    
    if dex == 'sushiswap':
        from_block = from_block = 10822038
        to_block = shared.BLOCKSTUDY
        number_batches = 20
        pools = get_logs(factory,'PairCreated',hash_create,from_block,to_block,number_batches)

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

    return pool_dic,tokens


def clean_transfers(transfer_list):
    clean_transfer_list = []
    for transfer in transfer_list:
        dictionary  = {
            'from': transfer.args._from,
            'to'  : transfer.args._to,
            'value': transfer.args._value,
            'logIndex': transfer.logIndex,
            'transactionIndex': transfer.transactionIndex,
            'transactionHash': transfer.transactionHash,
            'blockHash':transfer.blockHash,
            'blockNumber': transfer.blockNumber
        }
        clean_transfer_list.append(dictionary)
    return clean_transfer_list

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