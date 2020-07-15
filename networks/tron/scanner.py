import collections

from blockchain_common.wrapper_block import WrapperBlock
from eventscanner.queue.subscribers import pub
from scanner.events.block_event import BlockEvent
from scanner.services.scanner_polling import ScannerPolling


class TronScanner(ScannerPolling):

    def process_block(self, block: WrapperBlock):
        print('{}: new block received {} ({})'.format(self.network.type, block.number, block.hash), flush=True)

        if not block.transactions:
            print('{}: no transactions in {} ({})'.format(self.network.type, block.number, block.hash), flush=True)
            return

        address_transactions = collections.defaultdict(list)

        for tx in block.transactions:
            for _input in tx.inputs:
                address_transactions[_input].append(tx)

            for output in tx.outputs:
                address_transactions[output.address].append(tx)

        block_event = BlockEvent(self.network, block, address_transactions)
        pub.sendMessage(self.network.type, block_event)
