from base import BlockEvent, BaseMonitor, Transaction
from models import session, CommonDetails


class EthSendingMonitor(BaseMonitor):
    event_type = 'launched'

    def on_new_block_event(self, block_event: BlockEvent):

        deploy_hashes = {}
        for transactions_list in block_event.transactions_by_address.values():

            for transaction in transactions_list:
                deploy_hashes[transaction.tx_hash.lower()] = transaction

        details_whitelabel = session.query(CommonDetails) \
            .filter(CommonDetails.white_label_hash.in_(deploy_hashes.keys())) \

        for detail in details_whitelabel:
            print("contract_id", detail.contract.id, detail.white_label_hash)
            transaction: Transaction = deploy_hashes[detail.white_label_hash]
            tx_receipt = block_event.network.get_tx_receipt(transaction.tx_hash)

            message = {
                'contractId': detail.contract.id,
                'transactionHash': transaction.tx_hash,
                'address': transaction.creates,
                'success': tx_receipt.success,
                'status': 'COMMITTED'
            }

            self.send_to_backend(message)