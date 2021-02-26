from settings import CONFIG


class BaseMonitor:
    network_type: str
    event_type: str
    queue: str

    def __init__(self, network):
        self.network_type = network
        self.queue = CONFIG['networks'][self.network_type]['queue']
