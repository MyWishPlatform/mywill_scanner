from scanner.services.last_block_persister import LastBlockPersister

from .network import QurasNetwork
from .scanner import QurasScanner

class QurasMaker:

    def __init__(self, network_name: str, polling_interval: int, commitment_chain_length: int):
        network = QurasNetwork(network_name)
        last_block_persister = LastBlockPersister(network)
        self.scanner = QurasScanner(network, last_block_persister,
                                  polling_interval, commitment_chain_length)
