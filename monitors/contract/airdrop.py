from web3 import Web3
from sqlalchemy import func

from base import BlockEvent, BaseMonitor, Transaction
from models import ETHContract, Contract, Network, session
from settings import ContractTypes
from contracts import token_abi


class AirdropMonitor(BaseMonitor):
    event_type = 'airdrop'

    airdrop_contract_types = [
        ContractTypes.Airdrop.value,
        ContractTypes.TronAirdrop.value,
        ContractTypes.BinanceAirdrop.value,
        ContractTypes.MaticAirdrop.value,
    ]

    def __init__(self, network):
        super().__init__(network)
        # Creating empty provider for easy contract class reference
        web3 = Web3()
        self.token_contract = web3.eth.contract(abi=token_abi)

    def on_new_block_event(self, block_event: BlockEvent):
        to_addresses = {}
        for transactions_list in block_event.transactions_by_address.values():
            for transaction in transactions_list:
                address = transaction.outputs[0].address
                if not address:
                    continue
                to_addresses[address.lower()] = transaction

        eth_contracts = (session.query(ETHContract, Contract, Network)
                         .filter(Contract.id == ETHContract.contract_id, Contract.network_id == Network.id)
                         .filter(func.lower(ETHContract.address).in_(to_addresses.keys()))
                         .filter(Network.name == block_event.network.type)
                         # Filter only contracts with 'airdrop' contract_type
                         .filter(Contract.contract_type.in_(self.airdrop_contract_types))
                         .all())

        for contract in eth_contracts:
            transaction: Transaction = to_addresses[contract[0].address.lower()]
            tx_rec = block_event.network.rpc.eth.getTransactionReceipt(transaction.tx_hash)
            processed_logs = self.token_contract.events.Transfer().processReceipt(tx_rec)

            message = {
                'contractId': contract[0].id,
                'transactionHash': transaction.tx_hash,
                'success': bool(tx_rec.status),
                'status': 'COMMITTED',
                "type": "airdrop",
                'airdroppedAddresses': [
                    {"address": i.args['to'].lower(), "value": i.args['value']}
                    for i in processed_logs]
            }

            self.send_to_backend(message)
