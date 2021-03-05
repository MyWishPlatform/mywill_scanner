import threading

from pubsub import pub

import monitors
from networks import scanner_makers
from settings import CONFIG

subscribe_list = []
for name, monitor_config in CONFIG["monitors"].items():
    monitor_class = getattr(monitors, name, None)
    if monitor_class:
        networks = monitor_config["networks"]

        for network in networks:
            monitor = monitor_class(network)
            subscribe_list.append((monitor.process, network))
    else:

        raise ImportWarning(f'WARNING: Monitor {name} not found. Check config.yaml file.')

# pubsub lib do not remember variables, created inside loop.
# So, we create list of variables in one loop, and then push it to pubsub
for elem in subscribe_list:
    pub.subscribe(*elem)


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
