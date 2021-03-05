import json

with open("tokens/ico_abi.json") as f:
    ico_abi = json.load(f)
with open("tokens/token_abi.json") as f:
    token_abi = json.load(f)
with open("tokens/erc20_abi.json") as f:
    erc20_abi = json.load(f)
with open("tokens/airdrop_abi.json") as f:
    airdrop_abi = json.load(f)
