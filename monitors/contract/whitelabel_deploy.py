from base import BlockEvent, BaseMonitor, Transaction
from models import session, tokens_details, Contract, Network
from sqlalchemy.orm import joinedload


class EthSendingMonitor(BaseMonitor):
    event_type = 'launch'

    def on_new_block_event(self, block_event: BlockEvent):

        deploy_hashes = {}
        for transactions_list in block_event.transactions_by_address.values():
            for transaction in transactions_list:
                deploy_hashes[transaction.tx_hash.lower()] = transaction

        whitelabels = []
        for detail in tokens_details:
            result = session.query(detail).options(joinedload(Contract.network)).all()
            filtered = result.filter(detail.white_label_hash.in_(deploy_hashes.keys()))\
                .filter(Contract.id == detail.contract_id & Contract.network.name == block_event.network.type)
            whitelabels.extend(filtered)

        for catched_detail in whitelabels:
            print("contract_id: ", catched_detail.contract_id, 'white_label hash: ', catched_detail.white_label_hash)
            transaction: Transaction = deploy_hashes[catched_detail.white_label_hash]
            tx_receipt = block_event.network.get_tx_receipt(transaction.tx_hash)

            message = {
                'contractId': catched_detail.contract_id,
                'transactionHash': transaction.tx_hash,
                'address': transaction.creates,
                'success': tx_receipt.success,
                'status': 'COMMITTED'
            }

            self.send_to_backend(message)