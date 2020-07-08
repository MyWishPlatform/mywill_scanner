from scanner.events.block_event import BlockEvent
from mywish_models.models import UserSiteBalance, session
from eventscanner.queue.pika_handler import send_to_backend
from logger import logger


class EthPaymentMonitor:

    network_types = ['ETHERIUM_MAINNET']
    event_type = 'payment'

    @classmethod
    def on_new_block_ewent(cls, block_event: BlockEvent):
        if block_event.network.type not in cls.network_types:
            return

        addresses = block_event.transactions_by_address.keys()
        user_site_balances = session.query(UserSiteBalance).filter(UserSiteBalance.eth_address.in_(addresses)).all()
        for user_site_balance in user_site_balances:
            transactions = block_event.transactions_by_address[user_site_balance.eth_address.lower()]

            if not transactions:
                logger.error('{}: User {} received from DB, but was not found in transaction list (block {}).'.format(
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

                send_to_backend(cls.event_type, 'notification-ducatusx-mainnet', message)
