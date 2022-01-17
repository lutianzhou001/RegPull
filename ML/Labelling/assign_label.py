import pandas as pd

df_pool = pd.read_csv("../../data/pool_heuristics.csv", index_col="token_address")
df_transfers = pd.read_csv("../../data/transfer_heuristics.csv").drop_duplicates(subset=['token_address'])
df_transfers = df_transfers.set_index("token_address")
label_list = []

df = pd.concat([df_transfers, df_pool], axis=1, join='inner')
df['inactive'] = df['inactive'] * df['inactive_transfers']
df = df.drop(['inactive_transfers'], axis=1)

healthy_tokens = pd.read_csv("../../data/healthy_tokens.csv")['token_address']

for token in healthy_tokens:
    try:
        label_list.append([token, df_pool.loc[token]['pool_address'], 1, 0])
    except:
        pass

df_inactius = df.loc[(df["inactive"] == 1) & (df['late_creation'] == 0)]
rug_pull    = df_inactius.loc[(df_inactius["liq_MDD"] == -1)]
rug_pull_1  = rug_pull.loc[rug_pull['liq_RC'] <= 0.2]

for token in rug_pull_1.index:
    label_list.append([token, df_pool.loc[token]['pool_address'], 0, 1])

df_inactius = df.loc[(df["inactive"] == 1) & (df['late_creation'] == 0)]
rug_pull    = df_inactius.loc[(df_inactius["liq_MDD"] == 0)]
rug_pull    = rug_pull.loc[(rug_pull['price_MDD'] >= -1) & (rug_pull['price_MDD'] <= -0.9)]
rug_pull_2  = rug_pull.loc[(rug_pull['price_RC'] >= 0) & (rug_pull['price_RC'] <= 0.01)]

for token in rug_pull_2.index:
    label_list.append([token, df_pool.loc[token]['pool_address'], 0, 2])

pd.DataFrame(label_list, columns=["token_address", "pool_address", "label", "type"])\
    .to_csv("labeled_list.csv", index=False)