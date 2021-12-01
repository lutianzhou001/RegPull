import sys
sys.path.append("./../")
import shared
shared.init()
from collections import defaultdict
import math



def distribution_metric(balances,total_supply):
    g1 = sum([(value/total_supply)**2 for holder,value in balances.items() if holder not in [shared.ETH_ADDRESS,shared.DEAD_ADDRESS]])
    return g1

def _get_balances(transfers, block, bottom_limit=0):
    total_supply = 0
    curve_distribution = []
    total_number_holders = 0
    balances = defaultdict(lambda:0)
    for t in transfers:
        if t['blockNumber']<= block:
            balances[t["from"]] -= t["value"]
            balances[t["to"]] += t["value"]
            if t['from'] == shared.ETH_ADDRESS:
                total_supply += t["value"]
                balances[t["from"]] = 0
            if t['to'] == shared.ETH_ADDRESS:
                total_supply -= t["value"]
                balances[t["to"]] = 0
        main_supply = sum([balances[k] for k in balances if balances[k]/total_supply*100 > bottom_limit])
        balances2 = {k: balances[k] for k in balances if balances[k]/total_supply*100 > bottom_limit}
        balances2['others'] = total_supply - main_supply
        balances2[shared.ETH_ADDRESS] = 0
        curve_distribution.append(distribution_metric2(balances2,total_supply))
    return balances, total_supply, curve_distribution

def get_flow_block_list(transfers,block_list,bottom_limit = 0):
    # Ordered transfers and block_list. ASSERT?
    max_block = int(max(block_list))
    balances = defaultdict(lambda:0)
    curve_distribution = {}
    total_supply,total_supply_ans = 0,0
    total_balances = {}
    min_block = min(block_list)
    block = min_block
    
    for t in transfers:
        if int(t['blockNumber'])<= max_block:
            balances[t['args']["from"]] -= t['args']["value"]
            balances[t['args']["to"]] += t['args']["value"]
            if t['args']['from'] == shared.ETH_ADDRESS and t['type']!= 'Transfer':
                total_supply += t['args']["value"]
                balances[t['args']["from"]] = 0
            if t['args']['to'] == shared.ETH_ADDRESS and t['type']!= 'Transfer':
                total_supply -= t['args']["value"]
                balances[t['args']["to"]] = 0
        if [b for b in block_list  if b>=int(t["blockNumber"])]:
             new_block = min([b for b in block_list  if b>=int(t["blockNumber"])])
        else:
            break
        if total_supply!=0:
            main_supply = sum([balances[k] for k in balances if balances[k]/total_supply*100 > bottom_limit])
            balances2 = {k: balances[k] for k in balances if balances[k]/total_supply*100 > bottom_limit}
            balances2['others'] = total_supply - main_supply
            balances2[shared.ETH_ADDRESS] = 0
            
            curve_distribution[new_block] = distribution_metric(balances2,total_supply)
            total_balances[new_block] = balances2
    
        if total_supply_ans!=0 and total_supply == 0:
            total_balances[new_block] = {}
            curve_distribution[new_block] = None
            
        total_supply_ans = total_supply

    for index,block in enumerate(block_list):
        if block not in curve_distribution.keys() and block!= min_block:
            if block_list[index-1] in list(curve_distribution.keys()):
                curve_distribution[block] = curve_distribution[block_list[index-1]]
                total_balances[block]     = total_balances[block_list[index-1]]
            else:
                curve_distribution[block] = None
                total_balances[block]     = {}

    return total_balances, curve_distribution

def get_balances(transfers, block,bottom_limit):
    balances,total_supply,curve_distribution = _get_balances(transfers, block, bottom_limit)
    balances = [{"address": a, "amount": b} for a, b in balances.items()]
    balances = sorted(balances, key=lambda b: -abs(b["amount"]))
    return balances,total_supply, curve_distribution