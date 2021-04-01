from base.scanner import LastBlockPersister
from .network import TronNetwork
from .scanner import TronScanner


class TronMaker:

    def __init__(self, network_name: str, polling_interval: int, commitment_chain_length: int):
        network = TronNetwork(network_name)
        last_block_persister = LastBlockPersister(network)
        self.scanner = TronScanner(network, last_block_persister,
                                  polling_interval, commitment_chain_length)
