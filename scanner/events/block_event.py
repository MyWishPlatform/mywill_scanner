from blockchain_common.wrapper_network import WrapperNetwork


class BlockEvent:
    def __init__(self, network: WrapperNetwork, **kwargs):
        self.network = network
        for key in kwargs.keys():
            self.__setattr__(key, kwargs[key])
