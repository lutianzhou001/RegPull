import os
import sys
sys.path.append("../")
import shared
shared.init()
from Utils.eth_utils import *
from Utils.abi_info import *
import json
import concurrent.futures


def get_events(event_string,_hash,pool_address, pool_info, cont, len_pool_dic):
    print(cont, len_pool_dic)
    try:
        creation = pool_info['creation']
        pool = web3.eth.contract(pool_address, abi=shared.ABI_POOL)
        add_events = get_logs(pool, event_string, _hash, creation, shared.BLOCKSTUDY, 10)
        json_events = events_to_json(add_events)
        with open(f'./../data/pool_add_events/{pool_address}.json', 'w+') as f:
            json.dump(json_events, f)
        f.close()

    except Exception as err:
        print(f"Exception occured: {err}")

        pool_exceptions.append(pool_address)
        with open(f'./../data/pool_{event_string}_exceptions/pool_exceptions.json', 'w') as f:
            json.dump(pool_exceptions, f)
        f.close()


list_events = ['Mint','Burn','Transfer','Sync']

print(f"Which event of the Uniswap pools you want to obtain from {list_events}\n")
event_string = str(input())
assert(event_string in list_events)


res, web3 = connect_to_web3()
pool_exceptions = []

factory = web3.eth.contract(shared.UNISWAP_FACTORY, abi=shared.ABI_FACTORY)
pool_dic, _ = get_pools('uniswap_v2',factory)

#uni = web3.eth.get_contracts('0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc', abi=shared.ABI_POOL)
events = obtain_events_from_abi(shared.ABI_POOL)
_hash = [event for event in events if event_string in events][0]

features = []
cont = 0
pools_in_list = [pool.split(".")[0] for pool in os.listdir(f'../data/pool_{event_string}_events/')]

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as exec:
    for pool_address, pool_info in pool_dic.items():
        cont += 1
        if pool_address not in pools_in_list:
            features.append(exec.submit(get_events, event_string,_hash, pool_address, pool_info, cont, len(pool_dic)))

for i, feat in enumerate(features):
    feat.result()