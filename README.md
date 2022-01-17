# RugPullDetection


### TODO
- shared i un config.ini.
- Utils.
- Data (No se si es necasri).
- Folder ABIs: normal token abi, ABI_pool.
- Folder get_data: get_token_pools, get_source_code, get_decimals, tx_creation&get_block_creation, get_logs-> pool, get_transfers, lock_contrats.
- Features: curves_lp, curves_transfer, contract_features, lock_features, transfer_features, pool_features, pool_events.
- ML: XGBOOST i FT-Transformer
- Notebooks: Labels, Missing analysis, Features_track, Interpretability.

### Introduction

In this repository we will find the necessary tools to replicate the work made in "url_here". This repository, allows to download all the necessary data of UniswapV2 pools in the Ethereum blockchain. That is, all the PairPools, with their liquidity, prices and Add/remove events, all the source codes of the tokens,...
Moreover, in the folder ML we will find the tools to predict with high accurracy and sensibility if a token will eventually become a scam or not.

### Abstract

Uniswap, like other DEXs, has gained much attention this year because it is a non-custodial and publicly verifiable exchange that allows users to trade digital assets without trusted third parties. However, its simplicity and lack of regulation also makes it easy to execute initial coin offering scams by listing non-valuable tokens. This method of performing scams is known as rug pull, a phenomenon that already existed in traditional finance but has become more relevant in DeFi. Various projects such as \cite{rugpulldetector,tokensniffer}  have contributed to detecting rug pulls in EVM compatible chains. However, the first longitudinal and academic step to detecting and characterizing scam tokens on Uniswap was made in \cite{demystifying}. The authors collected all the transactions related to the Uniswap V2 exchange and proposed a machine learning algorithm to label tokens as scams. However, the algorithm is only valuable for detecting scams accurately after they have been executed. This paper increases their data set by 20K tokens and proposes a new methodology to label tokens as scams. After manually analyzing the data, we devised a theoretical classification of different malicious maneuvers in Uniswap protocol. We propose various machine-learning-based algorithms with new relevant features related to the token propagation and smart contract heuristics to detect potential rug pulls before they occur. In general, the models proposed achieved similar results. The best model obtained an accuracy of 0.9936, recall of 0.9540, and precision of 0.9838 in distinguishing  non-malicious tokens from scams prior to the malicious maneuver.

### Requirements

---
**NOTE**

It works with almost all markdown flavours (the below blank line matters).

---

### How to use it



### Example


### Results


### Reference




