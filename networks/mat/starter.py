from scanner.services.last_block_persister import LastBlockPersister

from .network import MatNetwork
from .scanner import MatScanner


class MatMaker:

    def __init__(self, network_name: str, polling_interval: int, commitment_chain_length: int):
        network = MatNetwork(network_name)
        last_block_persister = LastBlockPersister(network)
        self.scanner = MatScanner(network, last_block_persister,
                                  polling_interval, commitment_chain_length)
