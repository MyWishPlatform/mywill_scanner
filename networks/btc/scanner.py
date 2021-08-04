import collections

from pubsub import pub

from base import Block, Scanner, BlockEvent


class BTCScanner(Scanner):

    def process_block(self, block: Block):
        print('{}: new block received {} ({})'.format(self.network.type, block.number, block.hash), flush=True)

        if not block.transactions or len(block.transactions) <= 2:
            print('{}: no transactions in {} ({})'.format(self.network.type, block.number, block.hash), flush=True)
            return

        address_transactions = collections.defaultdict(list)
        print(len(block.transactions))
        print(block.transactions)

        for tx in block.transactions:
            for _input in tx.inputs:
                address_transactions[_input].append(tx)

            for output in tx.outputs:
                address_transactions[output.address].append(tx)

        block_event = BlockEvent(self.network, block, address_transactions)
        pub.sendMessage(self.network.type, block_event=block_event)

