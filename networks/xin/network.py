import time
import http.client
import requests
from hexbytes import HexBytes


from base import Block, Network, Output, Transaction, TransactionReceipt

from settings import CONFIG


class XinNetwork(Network):

    def __init__(self, type):
        super().__init__(type)
        config = CONFIG['networks'][type]

        urls = config['url']
        # Old config support
        # if not isinstance(urls, list):
        # if config.get('use_xin_api'):
        #     rpc =
        # urls = [urls]
        # for url in urls:
        # rpc = Web3(Web3.HTTPProvider(url))
        # Disable ethereum special checks, if network used for non-eth chain
        # if config.get('remove_middleware'):
        #     rpc.middleware_onion.inject(geth_poa_middleware, layer=0)
        # self.add_rpc(rpc)

        # etherscan_api_key = CONFIG['networks'][type].get('etherscan_api_key')
        # is_testnet = CONFIG['networks'][type].get('is_testnet')
        self.xinscan = XinFinScanAPI(etherscan_api_key, is_testnet) if etherscan_api_key else None

        # self.erc20_contracts_dict = {t_name: self.rpc.eth.contract(
        #     self.rpc.toChecksumAddress(t_address),
        #     abi=erc20_abi
        # ) for t_name, t_address in CONFIG['erc20_tokens'].items()}

    def get_last_block(self):
        conn = http.client.HTTPSConnection("rpc.xinfin.network")

        payload = "{\"jsonrpc\":\"2.0\",\"method\":\"eth_blockNumber\",\"params\":[],\"id\":1}"

        headers = {'content-type': "application/json"}

        conn.request("POST", "//blockNumber", payload, headers)
        res = conn.getresponse()
        data = res.read()
        print(data.decode("utf-8"))

    def get_block(self, number: int) -> Block:
        conn = http.client.HTTPSConnection("rpc.xinfin.network")
        payload = "{\"jsonrpc\":\"2.0\",\"method\":\"eth_getBlockByNumber\",\"params\":[\"0x0\",true],\"id\":1}"

        headers = {'content-type': "application/json"}

        conn.request("POST", "//getBlockByNumber", payload, headers)

        res = conn.getresponse()
        block = res.read().__dict__

        # block = self.rpc.eth.getBlock(number, full_transactions=True)
        block = Block(
            block['hash'].hex(),
            block['number'],
            block['timestamp'],
            [self._build_transaction(t) for t in block['transactions']],
        )

        if self.xinscan:
            internal_txs = [self._build_transaction(t) for t in self.xinscan.get_internal_txs(number)]
            block.transactions += internal_txs

        return block

    @staticmethod
    def _build_transaction(tx):
        tx_hash = tx['hash']
        if isinstance(tx_hash, HexBytes):
            tx_hash = tx_hash.hex()

        output = Output(
            tx_hash,
            0,
            tx['to'],
            tx['value'],
            tx['input']
        )

        # Field 'to' is empty when tx creates contract
        contract_creation = tx['to'] is None
        tx_creates = tx.get('creates', None)

        # 'creates' is None when tx dont create any contract
        t = Transaction(
            tx_hash,
            [tx['from']],
            [output],
            contract_creation,
            tx_creates
        )
        return t

    def get_tx_receipt(self, hash):
        conn = http.client.HTTPSConnection("rpc.xinfin.network")

        payload = "{\"jsonrpc\":\"2.0\",\"method\":\"eth_getTransactionReceipt\",\"params\":[" \
                  "\"0xa3ece39ae137617669c6933b7578b94e705e765683f260fcfe30eaa41932610f\"],\"id\":1} "

        headers = {'content-type': "application/json"}

        conn.request("POST", "//getTransactionReceipt", payload, headers)

        res = conn.getresponse()
        tx_res = res.read().__dict__

        return TransactionReceipt(
            tx_res['transactionHash'].hex(),
            tx_res['contractAddress'],
            tx_res['logs'],
            bool(tx_res['status']),
        )

    # def get_processed_tx_receipt(self, tx_hash, token_name):
    #     tx_res = self.get_tx_receipt(tx_hash)
    #     processed = self.erc20_contracts_dict[token_name].events.Transfer().processReceipt(tx_res)
    #     return processed


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

    def __init__(self, testnet=False):
        url_prefix = 'api-ropsten' if testnet else 'api'
        self.url = f'https://{url_prefix}.etherscan.io/api'

        # if self._validate_api_key(api_key):
        #     self.api_key = api_key
        #     self.requests_per_second = 5.0
        # else:
        self.api_key = self.default_api_key
        self.requests_per_second = 0.3

        self.last_request_time = 0.0

    def _validate_api_key(self, key):
        is_success = True
        error_message = ''
        if not key or key == self.default_api_key:
            error_message = 'Missing XinFin API Key or it same as default'
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
                error_message = 'Invalid xinfin api key, will use default instead'
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
