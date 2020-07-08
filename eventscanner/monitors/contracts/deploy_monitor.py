from scanner.events.block_event import BlockEvent
from mywish_models.models import DUCXContract, Contract, Network, session
from blockchain_common.wrapper_transaction import WrapperTransaction
from eventscanner.queue.pika_handler import send_to_backend

from logger import logger
from settings.settings_local import NETWORKS


class DeployMonitor:
    network_types = ['DUCATUSX_MAINNET', 'DUCATUSX_TESTNET']
    event_type = 'deployed'

    @classmethod
    def on_new_block_event(cls, block_event: BlockEvent):
        if block_event.network.type not in cls.network_types:
            return

        # addresses = block_event.transactions_by_address.keys()
        #
        # deploy_hashes = {transaction.tx for transaction in block_event.transactions_by_address.values()}
        deploy_hashes = {}
        for transactions_list in block_event.transactions_by_address.values():
            for transaction in transactions_list:
                if transaction.contract_creation:
                    deploy_hashes[transaction.tx_hash.lower()] = transaction

        contracts = session.query(DUCXContract, Contract, Network)\
            .filter(Contract.id == DUCXContract.contract_id, Contract.network_id == Network.id)\
            .filter(DUCXContract.tx_hash.in_(deploy_hashes.keys()))\
            .filter(Network.name == block_event.network.type).all()

        for contract in contracts:
            transaction: WrapperTransaction = deploy_hashes[contract[0].tx_hash]
            tx_receipt = block_event.network.get_tx_receipt(transaction.tx_hash)

            message = {
                'contractId': contract[0].id,
                'transactionHash': transaction.tx_hash,
                'address': transaction.creates,
                'success': tx_receipt.success,
                'status': 'COMMITTED'
            }

            send_to_backend(cls.event_type, NETWORKS[block_event.network.type]['queue'], message)
