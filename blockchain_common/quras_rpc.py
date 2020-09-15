import json

import requests

from settings.settings_local import NETWORKS

class QurasConnectionError(Exception):
    pass


class QurasResponseError(Exception):
    pass


class QurasInterface:

    def __init__(self, network):
        self.endpoint = NETWORKS[network]['url']
        print('quras interface configured', flush=True)

    def __getattr__(self, method):
        def wrapper(*args):
            params = {
                'jsonrpc': '2.0',
                'method': method,
                'params': args,
                'id': 1234,
            }

            try:
                response = requests.post(self.endpoint, json=params, verify=False)
            except requests.exceptions.ConnectionError as err:
                raise QurasConnectionError(str(err))

            answer = json.loads(response.content)

            if answer.get('error'):
                raise QurasResponseError(answer['error']['message'])
            return answer['result']

        return wrapper
