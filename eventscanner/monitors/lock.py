from scanner.events.block_event import BlockEvent
from mywish_models.models import AddressLock, Network, session
from eventscanner.queue.pika_handler import send_to_backend

from settings.settings_local import NETWORKS


class AddressLockMonitor:
    network_types = ['ETHEREUM_MAINNET']
    event_type = 'transactionCompleted'

    @classmethod
    def on_new_block_event(cls, block_event: BlockEvent):

        # In Java scanner this monitor scip waves network, but we do not support it yet
        if 'WAVES' in block_event.network.type:
            return

        addresses = []

        for key, value in block_event.transactions_by_address.items():
            if key.lower() == value[0].inputs[0].lower() or None:
                addresses.append(key)

        if not addresses:
            return

        lock_addresses = (session.query(AddressLock)
                          .filter(Network.name == block_event.network.type)
                          .filter(AddressLock.address.in_(addresses)))

        for address_lock in lock_addresses:
            transactions = block_event.transactions_by_address[address_lock.address.lower()]
            for tx in transactions:
                # FIXME Redundant check from Java scanner
                if not tx.inputs[0].lower() == address_lock.address.lower():
                    continue
                receipt = block_event.network.get_tx_receipt(tx.tx_hash)

                message = {
                    "status": 'COMMITTED',
                    "transactionHash": tx.tx_hash,
                    "addressId": address_lock.id,
                    "address": address_lock.address,
                    "lockedBy": address_lock.locked_by,
                    "transactionStatus": receipt.success,
                }

                send_to_backend(cls.event_type, NETWORKS[block_event.network.type]['queue'], message)
