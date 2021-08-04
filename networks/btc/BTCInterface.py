from bitcoinrpc.authproxy import AuthServiceProxy
from settings import CONFIG
from settings.consts import DECIMALS


class BTCInterfaceException(Exception):
    pass


class BTCInterface:
    endpoint = None
    settings = None

    def __init__(self, type):

        self.settings = CONFIG['networks'][type]
        self.decimal = DECIMALS['BTC']
        self.setup_endpoint()
        self._rpc = AuthServiceProxy
        self.check_connection()

    @property
    def rpc(self):
        return self._rpc(self.endpoint)

    def setup_endpoint(self):
        self.endpoint = 'http://{user}:{pwd}@{host}:{port}'.format(
            user=self.settings['user'],
            pwd=self.settings['password'],
            host=self.settings['host'],
            port=self.settings['port']
        )
        print(self.endpoint)
        return

    def check_connection(self):
        block = self.rpc.getblockcount()
        if block and block > 0:
            return True
        else:
            raise Exception('Ducatus node not connected')

    def dec_to_int(self, value):
        return int(value * self.decimal)
