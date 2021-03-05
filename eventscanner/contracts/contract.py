from base import BlockEvent
from eventscanner.queue.pika_handler import send_to_backend

from settings import CONFIG


class ContractEventMonitor:
    network_types = ["ETHEREUM_MAINNET"]
    # TODO: можно перенести в сеттингс
    event_types = {
        "OwnershipTransferred": "ownershipTransferred",
        "MintFinished": "finalized",
        "Initialized": "initialized",
    }
    queue = "notification-ethereum"

    def __init__(self):
        pass
        # TODO: сделать автозаполнение queue для всех сетей у этого монитора
        # for monitor in CONFIG["monitors"]:
        #     ContractEventMonitor.queue = ...

    @classmethod
    def on_new_block_event(cls, block_event: BlockEvent):
        if not block_event.events:
            return

        for event, transactions in block_event.events.items():
            for transaction in transactions:
                message = {
                    "status": "COMMITTED",
                    "txHash": transaction["transactionHash"].hex(),
                }
                send_to_backend(
                    cls.event_types[event], cls.queue, message
                )
