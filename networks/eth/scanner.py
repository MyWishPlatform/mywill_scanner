import collections
import traceback
import sys
from pubsub import pub
from web3.exceptions import LogTopicError

from contracts import token_abi
from base import Block, Scanner, BlockEvent


class EthScanner(Scanner):

    def process_block(self, block: Block):
        print('{}: new block received {} ({})'.format(self.network.type, block.number, block.hash), flush=True)

        if not block.transactions:
            print('{}: no transactions in {} ({})'.format(self.network.type, block.number, block.hash), flush=True)
            return

        address_transactions = collections.defaultdict(list)
        for transaction in block.transactions:
            self._check_tx_from(transaction, address_transactions)
            self._check_tx_to(transaction, address_transactions)

        block_event = BlockEvent(self.network, block=block, events=None, transactions_by_address=address_transactions)
        try:
            pub.sendMessage(self.network.type, block_event=block_event)
        except Exception:
            print('{}: exception handled while message publising. Continue.'.format(self.network.type))
            print('\n'.join(traceback.format_exception(*sys.exc_info())), flush=True)

    def _check_tx_from(self, tx, addresses):
        from_address = tx.inputs[0]
        if from_address:
            addresses[from_address.lower()].append(tx)
        else:
            print('{}: Empty from field for transaction {}. Skip it.'.format(self.network.type, tx.tx_hash))

    def _check_tx_to(self, tx, address):
        to_address = tx.outputs[0]
        if to_address and to_address.address:
            address[to_address.address.lower()].append(tx)
        else:
            self._check_tx_creates(tx, address)

    def _check_tx_creates(self, tx, address):
        if not tx.contract_creation:
            return
        if tx.creates:
            address[tx.creates.lower()].append(tx)
        else:
            try:
                tx_receipt = self.network.get_tx_receipt(tx.tx_hash)

                # This field can be str and list, but list must be deprecated from java
                if isinstance(tx_receipt.contracts, list):
                    contract_address = tx_receipt.contracts[0]
                else:
                    contract_address = tx_receipt.contracts
                tx.creates = contract_address
                address[contract_address.lower()].append(tx)
            except Exception:
                print('{}: Error on getting transaction {} receipt.'.format(self.network.type,
                                                                            tx.tx_hash))
                print('{}: Empty to and creates field for transaction {}. Skip it.'.format(self.network.type,
                                                                                           tx.tx_hash))

    def _find_event(self, block: Block) -> dict:
        find_events = {}
        events = {
            "OwnershipTransferred": token_abi,
            "MintFinished": token_abi,
            "Initialized": token_abi,
        }
        for event, abi in events.items():
            try:
                contract = self.network.rpc.eth.contract(abi=abi)
                event_filter = contract.events.__getitem__(event).createFilter(fromBlock=block.number,
                                                                               toBlock=block.number)
                entries = event_filter.get_all_entries()
                if entries:
                    find_events[event] = entries
            except LogTopicError as err:
                print(str(err))
        print('find events',find_events)
        return find_events
