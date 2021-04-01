"""
Contain contract ABIs in json format.

For each contract, the events of which the scanner must catch, you need to add ABI here.
"""
import json


def _open_abi(name):
    with open(f"contracts/{name}.json") as f:
        result = json.load(f)
    return result


ico_abi = _open_abi('ico_abi')
token_abi = _open_abi('token_abi')
erc20_abi = _open_abi('erc20_abi')
airdrop_abi = _open_abi('airdrop_abi')
