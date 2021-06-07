from base import Block
from networks.eth.scanner import EthScanner


class XinScanner(EthScanner):

    def process_block(self, block: Block):
        pass

    def _check_tx_from(self, tx, addresses):
        pass

    def _check_tx_to(self, tx, address):
        pass

    def _check_tx_creates(self, tx, address):
        pass

    def _find_event(self, block: Block) -> dict:
        pass
