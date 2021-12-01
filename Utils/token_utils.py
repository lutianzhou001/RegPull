from collections import defaultdict
from decimal import Decimal

# transfers are ordered by block and transactionIndex (default downloading). 
# Assegurar que no pasa(e1,e2,e2,e3)

def get_balances(transfers, block, bottom_limit=0):
    balances = defaultdict(Decimal)
    for t in transfers:
        if int(t['blockNumber'],0)<= block:
            balances[t["from"]] -= t["amount"]
            balances[t["to"]] += t["amount"]
    balances = {k: balances[k] for k in balances if balances[k] > bottom_limit}
    return balances


def get_balances_list(transfers, block,bottom_limit):
    balances = get_balances(transfers, block, bottom_limit)
    balances = [{"address": a, "amount": b} for a, b in balances.items()]
    balances = sorted(balances, key=lambda b: -abs(b["amount"]))
    return balances


def subset_transfers(transfers,from_block, to_block):
    subset_trans = []
    for trans in transfers:
        if from_block <= int(trans['blockNumber'],0) <= to_block:
            subset_trans.append(trans)
    return subset_trans