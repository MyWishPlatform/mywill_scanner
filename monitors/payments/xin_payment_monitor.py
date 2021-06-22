from base import BlockEvent
from monitors import EthPaymentMonitor


class XinPaymentMonitor(EthPaymentMonitor):
    def on_new_xin_block_event(self, block_event: BlockEvent):
        addresses = block_event.transactions_by_address.values()
        for address in addresses:
            if address[:3] == 'xdc':
                address[:3]['0x'] = addresses.pop[:3]('xdc')

        return super().on_new_block_event(block_event)
