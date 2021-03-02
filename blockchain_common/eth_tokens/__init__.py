import json

with open("blockchain_common/eth_tokens/erc20_abi.json") as f:
    erc20_abi = json.load(f)
with open("blockchain_common/eth_tokens/airdrop_abi.json") as f:
    abi_airdrop = json.load(f)
# with open("blockchain_common/eth_tokens/ico_abi.json") as f:
#     ico_abi = json.load(f)
with open("blockchain_common/eth_tokens/token_abi.json") as f:
    token_abi = json.load(f)
