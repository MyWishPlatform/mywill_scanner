from pubsub import pub

from settings import CONFIG
from .. import monitors

for name, monitor_config in CONFIG["monitors"].items():
    monitor_class = getattr(monitors, name, None)
    if monitor_class:
        networks = monitor_config["networks"]

        for network in networks:
            monitor = monitor_class(network)
            pub.subscribe(monitor.on_new_block_event, network)
