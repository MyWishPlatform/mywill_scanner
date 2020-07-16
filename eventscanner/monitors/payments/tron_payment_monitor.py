from eventscanner.queue.pika_handler import send_to_backend
from mywish_models.models import UserSiteBalance, session
from scanner.events.block_event import BlockEvent
from settings.settings_local import NETWORKS


class TronPaymentMonitor:

    network_types = ['TRON_MAINNET']
    event_type = 'payment'
    queue = NETWORKS[network_types[0]]['queue']

    @classmethod
    def on_new_block_event(cls, block_event: BlockEvent):
        if block_event.network.type not in cls.network_types:
            return

        addresses = block_event.transactions_by_address.keys()
        user_site_balances = session.query(UserSiteBalance).filter(UserSiteBalance.tron_address.in_(addresses)).all()

        for usb in user_site_balances:
            transactions = block_event.transactions_by_address[usb.tron_address.lower()]

            if not transactions:
                print('{}: User {} received from DB, but was not found in transaction list (block {}).'.format(
                    block_event.network.type, usb, block_event.block.number))

            for tx in transactions:
                if usb.tron_address != tx.outputs[0].address:
                    print('{}: Found transaction out from internal address. Skip it.'.format(block_event.network.type),
                          flush=True)
                    continue

                amount = tx.outputs[0].value if usb.tron_address == tx.outputs[0].address else 0

                # fixme In java this checking like get_tx_receipt -> EventByTx,
                #  but it contains same with tx field `status`,
                #  so idk did i need copy event_check from java?
                success = tx.status == 'SUCCESS'
                message = {
                    "transactionHash": tx.tx_hash,
                    "address": usb.tron_address,
                    "amount": amount,
                    "currency": "TRX",
                    "success": success,
                }

                send_to_backend(cls.event_type, cls.queue, message)
