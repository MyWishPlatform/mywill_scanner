from base import BlockEvent, BaseMonitor, Transaction
from models import session, tokens_details, Contract, Network


class EthSendingMonitor(BaseMonitor):
    event_type = 'launch'

    def on_new_block_event(self, block_event: BlockEvent):

        deploy_hashes = {}
        for transactions_list in block_event.transactions_by_address.values():
            for transaction in transactions_list:
                deploy_hashes[transaction.tx_hash.lower()] = transaction

        whitelabels = []
        for detail in tokens_details:
            result = session.query(Contract, Network, detail)\
                .filter(Contract.id == detail.contract_id)\
                .filter(Contract.network_id == Network.id)\
                .filter(detail.white_label_hash.in_(deploy_hashes.keys()))\
                .filter(Network.name == block_event.network.type).all()
            whitelabels.extend(result)

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