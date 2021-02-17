import collections
from web3 import Web3
from web3.exceptions import LogTopicError

from settings import WEB3_URL
from eventscanner.queue.subscribers import pub
from scanner.events.block_event import BlockEvent
from blockchain_common.wrapper_block import WrapperBlock
from scanner.services.scanner_polling import ScannerPolling
from blockchain_common.eth_tokens import abi_airdrop, token_abi

web3 = Web3(Web3.HTTPProvider(WEB3_URL))


class EthScanner(ScannerPolling):

    def process_block(self, block: WrapperBlock):
        print('{}: new block received {} ({})'.format(self.network.type, block.number, block.hash), flush=True)

        if not block.transactions:
            print('{}: no transactions in {} ({})'.format(self.network.type, block.number, block.hash), flush=True)
            return

        address_transactions = collections.defaultdict(list)
        for transaction in block.transactions:
            self._check_tx_from(transaction, address_transactions)
            self._check_tx_to(transaction, address_transactions)

        print('{}: transactions'.format(self.network.type), address_transactions, flush=True)

        events = self._find_event(block)
        block_event = BlockEvent(self.network, block=block, events=events, transactions=address_transactions)
        pub.sendMessage(self.network.type, block_event=block_event)

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
        if tx.creates:
            address[tx.creates.lower()].append(tx)
        else:
            try:
                tx_receipt = self.network.get_tx_receipt(tx.tx_hash)
                contract_address = tx_receipt.contracts[0]
                tx.creates = contract_address
                address[contract_address.lower()].append(tx)
            except Exception:
                print('{}: Error on getting transaction {} receipt.'.format(self.network.type,
                                                                            tx.tx_hash))
                print('{}: Empty to and creates field for transaction {}. Skip it.'.format(self.network.type,
                                                                                           tx.tx_hash))

    def _find_event(self, block: WrapperBlock) -> dict:
        find_events = {}
        events = {
            "OwnershipTransferred": abi_airdrop,
            "MintFinished": token_abi,
            "Initialized": token_abi,
        }
        for event, abi in events.items():
            try:
                contract = web3.eth.contract(abi=abi)
                event_filter = contract.events.__getitem__(event).createFilter(fromBlock=block.number, toBlock=block.number)
                entries = event_filter.get_all_entries()
                if entries:
                    find_events[event] = entries
            except LogTopicError as err:
                print(str(err))

        return find_events
