import threading

from settings import CONFIG
from networks import scanner_makers


class ScanEntrypoint(threading.Thread):

    def __init__(self, network_name, network_maker, polling_interval, commitment_chain_length):
        super().__init__()
        self.network = network_maker(network_name, polling_interval, commitment_chain_length)

    def run(self):
        self.network.scanner.poller()


if __name__ == "__main__":
    for net_name, net_conf in CONFIG["networks"].items():
        maker_names = net_conf["scanner_makers"]
        for maker_name in maker_names:
            maker = scanner_makers[maker_name]
            scan = ScanEntrypoint(
                net_name,
                maker,
                net_conf["polling_interval"],
                net_conf["commitment_chain_length"],
            )
            scan.start()
