from base import BlockEvent, BaseMonitor
from logging import getLogger

from models import UserSiteBalance, session
from logging import getLogger

LOGGER = getLogger()
LOGGER.info("starting initialization")


class TronPaymentMonitor(BaseMonitor):
    event_type = 'payment'

    def on_new_block_event(self, block_event: BlockEvent):
        addresses = block_event.transactions_by_address.keys()
        user_site_balances = session.query(UserSiteBalance).filter(UserSiteBalance.tron_address.in_(addresses)).all()

        for usb in user_site_balances:
            transactions = block_event.transactions_by_address[usb.tron_address.lower()]

            if not transactions:
                LOGGER.info('{}: User {} received from DB, but was not found in transaction list (block {}).'.format(
                    block_event.network.type, usb, block_event.block.number))
                print('{}: User {} received from DB, but was not found in transaction list (block {}).'.format(
                    block_event.network.type, usb, block_event.block.number))

            for tx in transactions:
                if usb.tron_address != tx.outputs[0].address:
                    LOGGER.info('{}: Found transaction out from internal address. Skip it.'\
                                .format(block_event.network.type))
                    print('{}: Found transaction out from internal address. Skip it.'.format(block_event.network.type),
                          flush=True)
                    continue

                amount = tx.outputs[0].value if usb.tron_address == tx.outputs[0].address else 0

                success = tx.status == 'SUCCESS'
                message = {
                    'userId': usb.user_id,
                    "transactionHash": tx.tx_hash,
                    "address": usb.tron_address,
                    "currency": "TRX",
                    "amount": amount,
                    'siteId': usb.subsite_id,
                    "success": success,
                    'status': 'COMMITTED'
                }

                self.send_to_backend(message)
