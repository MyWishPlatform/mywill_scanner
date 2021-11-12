import threading
import time

from logging import getLogger, basicConfig
import logging

from pubsub import pub

logging.basicConfig(filename='last_log.log', filemode='w', level=logging.INFO)
LOGGER = getLogger()
LOGGER.info("starting initialization")

print("[main] import monitors")
import monitors
print("[main] import networks")
from networks import scanner_makers
print("[main] import server")
from server import run_server
print("[main] import settings")
from settings import CONFIG
print("[main] import all imported")


LOGGER.info("all stuff are imported successfully")


subscribe_list = []
for name, monitor_config in CONFIG["monitors"].items():
    print(f"settuping monitor {name}...")

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
    print("db already setuped")
    LOGGER.info("running main...")

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

    run_server()

