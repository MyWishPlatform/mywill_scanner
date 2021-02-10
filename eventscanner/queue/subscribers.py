from pubsub import pub

from settings import CONFIG, MONITORS

for monitor in CONFIG["monitors"].items():
    name = monitor[0]

    if name in MONITORS:
        method = monitor[1].get("method", None)
        networks = monitor[1]["networks"]

        for network in networks:
            pub.subscribe(MONITORS[name].on_new_block_event, network)
