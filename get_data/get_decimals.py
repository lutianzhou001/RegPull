import shared
shared.init()


def get_decimal_token(token_address):
    """
    Gets token decimal given a token address.

    Parameters
    ----------
    token_address: str
        String containing token address.

    Returns
    -------
    decimal: int
        Int corresponding to token decimal.
    """

    contract = shared.web3.eth.contract(token_address, abi=shared.ABI)
    decimals = contract.functions.decimals().call()

    return decimals
