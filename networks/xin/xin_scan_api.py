import time

import requests

from networks.eth.network import APILimitError


class XinFinScanAPI:
    """
            Interface for EtherScan API.

            We can't get internal transactions from ETH RPC, cause they aren't actual transactions.
            But EtherScan allow us to get this info.

            Makes request with considering the limit. Without API key it's only one request per 3 sec.
            """

    default_api_key = 'YourApiKeyToken'

    # Used for beat CloudFire protection on etherscan-ropsten
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Geko/20100101 Firefox/69.0'}

    def __init__(self, api_key=None, testnet=False):
        url_prefix = 'api-ropsten' if testnet else 'api'
        self.url = f'https://{url_prefix}.xinscan.io/api'

        if self._validate_api_key(api_key):
            self.api_key = api_key
            self.requests_per_second = 5.0
        else:
            self.api_key = self.default_api_key
            self.requests_per_second = 0.3

        self.last_request_time = 0.0

    def _validate_api_key(self, key):
        is_success = True
        error_message = ''
        if not key or key == self.default_api_key:
            error_message = 'Missing ETHERSCAN API Key or it same as default'
            is_success = False

        if key:
            params = {
                'module': 'block',
                'action': 'getblockreward',
                'blockno': 1,
                'apikey': key
            }

            r = requests.get(self.url, headers=self.headers, params=params)
            data = r.json()
            if data['result'] == 'Invalid API Key':
                error_message = 'Invalid etherscan api key, will use default instead'
                is_success = False

        if not is_success:
            print('WARNING!', error_message)
            print('Without API key request limit will be set to `one request per 3 seconds`')

        return is_success

    def get_internal_txs(self, block_number, attempt=0):
        """
                Return internal transactions by block number

                Compare API limit with last request time.
                If requests over limits - wait and try again after.
                """
        if attempt >= 5:
            raise TimeoutError(f'Too many attempts to get internal txs from {block_number} block')
        attempt += 1

        seconds_for_request = 1 / self.requests_per_second
        now = time.time()
        time_diff = now - self.last_request_time

        if time_diff >= seconds_for_request:
            try:
                self.last_request_time = now
                return self._get_internal_txs(block_number)
            except APILimitError as e:
                time.sleep(5)
                return self.get_internal_txs(block_number, attempt)
        else:
            time.sleep(seconds_for_request - time_diff)
            return self.get_internal_txs(block_number, attempt)

    def _get_internal_txs(self, block_number):
        params = {
            'module': 'account',
            'action': 'txlistinternal',
            'startblock': block_number,
            'endblock': block_number,
            'apikey': self.api_key
        }

        r = requests.get(self.url, headers=self.headers, params=params)
        data = r.json()

        if r.status_code == 200 and data['status'] == '1':
            txs = data.get('result')
            return txs
        else:
            if data['message'] == 'No transactions found':
                return []
            raise APILimitError(data['message'])

    class APILimitError(Exception):
        ...
