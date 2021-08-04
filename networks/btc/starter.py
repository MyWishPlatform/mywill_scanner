from networks.btc.network import BTCNetwork
from base.scanner import LastBlockPersister
from networks.btc.scanner import BTCScanner


class BTCMaker:
    def __init__(self, network_name: str, polling_interval: int, commitment_chain_length: int):
        network = BTCNetwork(network_name)
        last_block_persister = LastBlockPersister(network)
        self.scanner = BTCScanner(network, last_block_persister,
                                  polling_interval, commitment_chain_length
                                  )
