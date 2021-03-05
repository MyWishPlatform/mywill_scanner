from base import BlockEvent, BaseMonitor
from models import UserSiteBalance, session
from eventscanner.queue.pika_handler import send_to_backend


class EthPaymentMonitor(BaseMonitor):
    event_type = 'payment'

    def on_new_block_event(self, block_event: BlockEvent):
        addresses = block_event.transactions_by_address.keys()
        user_site_balances = session.query(UserSiteBalance).filter(UserSiteBalance.eth_address.in_(addresses)).all()
        for user_site_balance in user_site_balances:
            transactions = block_event.transactions_by_address[user_site_balance.eth_address.lower()]

            if not transactions:
                print('{}: User {} received from DB, but was not found in transaction list (block {}).'.format(
                    block_event.network.type, user_site_balance, block_event.block.number))

            for transaction in transactions:
                if user_site_balance.eth_address.lower() != transaction.outputs[0].address.lower():
                    print('{}: Found transaction out from internal address. Skip it.'.format(block_event.network.type),
                          flush=True)
                    continue

                tx_receipt = block_event.network.get_tx_receipt(transaction.tx_hash)

                message = {
                    'userId': user_site_balance.user_id,
                    'transactionHash': transaction.tx_hash,
                    'currency': 'ETH',
                    'amount': transaction.outputs[0].value,
                    'siteId': user_site_balance.subsite_id,
                    'success': tx_receipt.success,
                    'status': 'COMMITTED'
                }

                send_to_backend(self.monitor_name, self.event_type, self.queue, message)
