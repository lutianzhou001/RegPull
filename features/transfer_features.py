import networkx as nx
from collections import defaultdict

import pandas as pd

import shared
shared.init()


def get_transfer_features(transfers):
    """
    Computes features based on token transfers.

    Parameters
    ----------
    transfers: Dataframe
        Dataframe with columns: "transactionHash", "block_number", "from", "to", "value".

    Returns
    -------
    features: Dict[str, float]
        Dictionary that contains all computed features.
    """
    transfers = pd.DataFrame(transfers)
    from_, to_, values = 2, 3, 4
    num_transactions_list = len(transfers)
    n_unique_addresses = len(set(transfers[from_].tolist() + transfers[to_].tolist()))
    G = nx.Graph()
    transfers = transfers.iloc[:10000]
    for From, To, Value in zip(transfers[from_], transfers[to_], transfers[values]):
       G.add_edge(From, To, weight=Value)
    try:
        cluster_coeffs = nx.average_clustering(G)
    except:
        cluster_coeffs = 0

    features = {
        'num_transactions': num_transactions_list,
        'n_unique_addresses': n_unique_addresses,
        'cluster_coeff': cluster_coeffs
    }
    return features


def distribution_metric(balances, total_supply):
    """ HHIndex actual computation"""
    g1 = sum([(value/total_supply)**2 for holder,value in balances.items()
              if holder not in [shared.ETH_ADDRESS,shared.DEAD_ADDRESS]])
    return g1


def get_curve(transfers):
    """
    Computes HHIndex.

    Parameters
    ----------
    transfers: Dataframe
        Dataframe with columns: "transactionHash", "block_number", "from", "to", "value".
    Returns
    -------
    Dictionary that contains the computed HHI
    """

    balances = defaultdict(lambda: 0)
    from_, to_, values = 2, 3, 4
    total_supply, total_supply_ans = 0, 0

    for i in range(len(transfers)):
        balances[transfers[i][from_]] -= float(transfers[i][values])
        balances[transfers[i][to_]] += float(transfers[i][values])
        if transfers[i][from_] == shared.ETH_ADDRESS:
            total_supply += float(transfers[i][values])
            balances[transfers[i][from_]] = 0
        if transfers[i][to_] == shared.ETH_ADDRESS:
            total_supply -= float(transfers[i][values])
            balances[transfers[i][to_]] = 0
    if total_supply != 0:
        curve = distribution_metric(balances, total_supply)
    else:
        curve = 1
    return {'tx_curve': curve}



