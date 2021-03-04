from web3 import Web3

from blockchain_common.base_monitor import BaseMonitor
from blockchain_common.eth_tokens import token_abi
from blockchain_common.wrapper_transaction import WrapperTransaction
from eventscanner.queue.pika_handler import send_to_backend
from mywish_models.models import ETHContract, Contract, Network, session
from scanner.events.block_event import BlockEvent
from settings import ContractTypes


class AirdropMonitor(BaseMonitor):
    event_type = 'airdrop'

    airdrop_contract_types = [
        ContractTypes.AIRDROP.value,
        ContractTypes.TRON_AIRDROP.value,
        ContractTypes.BINANCE_AIRDROP.value,
        ContractTypes.MATIC_AIRDROP.value,
    ]

    def __init__(self, network):
        super().__init__(network)
        # Creating empty provider for easy contract class reference
        web3 = Web3()
        self.token_contract = web3.eth.contract(abi=token_abi)

    def on_new_block_event(self, block_event: BlockEvent):
        if block_event.network.type != self.network_type:
            return

        to_addresses = {}
        for transactions_list in block_event.transactions_by_address.values():
            for transaction in transactions_list:
                to_addresses[transaction.outputs[0].address.lower()] = transaction

        eth_contracts = (session.query(ETHContract, Contract, Network)
                         .filter(Contract.id == ETHContract.contract_id, Contract.network_id == Network.id)
                         .filter(ETHContract.address.in_(to_addresses.keys()))
                         .filter(Network.name == block_event.network.type)
                         # Filter only contracts with 'airdrop' contract_type
                         .filter(Contract.contract_type.in_(self.airdrop_contract_types))
                         .all())

        for contract in eth_contracts:
            transaction: WrapperTransaction = to_addresses[contract[0].address]
            tx_rec = block_event.network.rpc.eth.getTransactionReceipt(transaction.tx_hash)
            processed_logs = self.token_contract.events.Transfer().processReceipt(tx_rec)

            message = {
                'contractId': contract[0].id,
                'transactionHash': transaction.tx_hash,
                'success': bool(tx_rec.status),
                'status': 'COMMITTED',
                "type": "airdrop",
                'airdroppedAddresses': [
                    {"address": i.args['to'], "value": i.args['value']}
                    for i in processed_logs]
            }

            send_to_backend(self.event_type, self.queue, message)
