from pubsub import pub

from settings import CONFIG
from .. import monitors

for name, monitor_config in CONFIG["monitors"].items():
    monitor = getattr(monitors, name, None)
    if monitor:
        method = monitor_config.get("method", None)
        networks = monitor_config["networks"]

        for network in networks:
            pub.subscribe(monitor.on_new_block_event, network)
