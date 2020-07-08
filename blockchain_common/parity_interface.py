import requests
import json

from settings.settings_local import *


class ParConnectExc(Exception):
    def __init__(self, *args):
        self.value = 'can not connect to parity'

    def __str__(self):
        return self.value


class ParErrorExc(Exception):
    pass


class ParityInterface:

    def __init__(self, network: str):

        self.settings = NETWORKS[network]
        self.setup_endpoint()

    def setup_endpoint(self):
        self.endpoint = self.settings['url']
        self.settings['chainId'] = self.eth_chainId()
        print('parity interface', self.settings, flush=True)

    def __getattr__(self, method):
        def f(*args):
            arguments = {
                'method': method,
                'params': args,
                'id': 1,
                'jsonrpc': '2.0',
            }
            try:
                temp = requests.post(
                    self.endpoint,
                    json=arguments,
                    headers={'Content-Type': 'application/json'}
                )
            except requests.exceptions.ConnectionError as e:
                raise ParConnectExc()
            result = json.loads(temp.content.decode())
            if result.get('error'):
                raise ParErrorExc(result['error']['message'])
            return result['result']

        return f
