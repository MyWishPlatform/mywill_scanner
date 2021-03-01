from scanner.events.block_event import BlockEvent
from blockchain_common.eth_tokens import token_abi
from eventscanner.queue.pika_handler import send_to_backend
from blockchain_common.wrapper_transaction import WrapperTransaction
from mywish_models.models import ETHContract, Contract, Network, session

from settings.settings_local import NETWORKS


class OwnershipMonitor:
    network_types = ['MATIC_MAINNET', 'MATIC_TESTNET']
    event_type = 'ownershipTransferred'

    @classmethod
    def on_new_block_event(cls, block_event: BlockEvent):
        if block_event.network.type not in cls.network_types:
            return

        to_addresses = {}
        for transactions_list in block_event.transactions_by_address.values():
            for transaction in transactions_list:
                to_addresses[transaction.outputs[0].address] = transaction

        eth_contracts = session.query(ETHContract, Contract, Network)\
            .filter(Contract.id == ETHContract.contract_id, Contract.network_id == Network.id)\
            .filter(ETHContract.address.in_(to_addresses.keys()))\
            .filter(Network.name == block_event.network.type).all()
        
        for contract in eth_contracts:
            transaction: WrapperTransaction = to_addresses[contract[0].address]

            crowdsale_contract = block_event.network.web3.eth.contract(abi=token_abi)
            tx_res = block_event.network.web3.eth.getTransactionReceipt(transaction.tx_hash)
            tx_receipt = crowdsale_contract.events.OwnershipTransferred().processReceipt(tx_res)

            print(tx_receipt[0])
            print(tx_receipt[0]['args']['newOwner'],  contract[0].address)

            if tx_receipt[0]['event'] != 'OwnershipTransferred':
                continue

            message = {
                'contractId': contract[0].id,
                'crowdsaleId': contract[0].id,
                'transactionHash': transaction.tx_hash,
                'new owner': tx_receipt[0]['args']['newOwner'],
                'address': transaction.creates,
                'success': True,
                'status': 'COMMITTED'
            }

            send_to_backend(cls.event_type, NETWORKS[block_event.network.type]['queue'], message)
