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
        
        for tx in block.transactions:
            for output in tx.outputs:
                for _out in output.address:
                    address_transactions[_out].append(tx)
        block_event = BlockEvent(self.network, block=block, transactions_by_address=address_transactions)
        pub.sendMessage(self.network.type, block_event=block_event)

