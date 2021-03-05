from settings import CONFIG


class BaseMonitor:
    network_type: str
    event_type: str
    queue: str

    def __init__(self, network):
        self.network_type = network
        self.queue = CONFIG['networks'][self.network_type]['queue']
        self.monitor_name = self.__class__.__name__

    def process(self, block_event):
        if block_event.network.type != self.network_type:
            return

        self.on_new_block_event(block_event)

    def on_new_block_event(self, block_event):
        raise NotImplementedError("WARNING: Function on_new_block_event must be overridden.")
