from pubsub import pub

from settings import CONFIG
from .. import monitors

subscribe_list = []
for name, monitor_config in CONFIG["monitors"].items():
    monitor_class = getattr(monitors, name, None)
    if monitor_class:
        networks = monitor_config["networks"]

        for network in networks:
            monitor = monitor_class(network)
            subscribe_list.append((monitor.process, network))
    else:
        print(f'Monitor {name} not found.')

# pubsub lib do not remember variables, created inside loop.
# So, we create list of variables in one loop, and then push it to pubsub
for elem in subscribe_list:
    pub.subscribe(*elem)
