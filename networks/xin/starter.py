from base.scanner import LastBlockPersister
from networks.xin.network import XinNetwork
from networks.xin.scanner import XinScanner


class XinMaker:

    def __init__(self, network_name: str, polling_interval: int, commitment_chain_length: int):
        network = XinNetwork()
        last_block_persister = LastBlockPersister(network)
        self.scanner = XinScanner(network, last_block_persister,
                                  polling_interval, commitment_chain_length)
