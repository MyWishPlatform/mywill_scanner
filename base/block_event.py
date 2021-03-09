from base.network import Network


class BlockEvent:
    def __init__(self, network: Network, **kwargs):
        self.network = network
        for key in kwargs.keys():
            self.__setattr__(key, kwargs[key])
