import time

import requests
from hexbytes import HexBytes
from web3 import Web3

from blockchain_common.eth_tokens import erc20_abi
from blockchain_common.wrapper_block import WrapperBlock
from blockchain_common.wrapper_network import WrapperNetwork
from blockchain_common.wrapper_output import WrapperOutput
from blockchain_common.wrapper_transaction import WrapperTransaction
from blockchain_common.wrapper_transaction_receipt import WrapperTransactionReceipt
from settings.settings_local import NETWORKS, ERC20_TOKENS


class EthNetwork(WrapperNetwork):

    def __init__(self, type):
        super().__init__(type)
        url = NETWORKS[type]['url']
        self.web3 = Web3(Web3.HTTPProvider(url))
        self.etherscan = EtherScanAPI()

        self.erc20_contracts_dict = {t_name: self.web3.eth.contract(
            self.web3.toChecksumAddress(t_address),
            abi=erc20_abi
        ) for t_name, t_address in ERC20_TOKENS.items()}

    def get_last_block(self):
        return self.web3.eth.blockNumber

    def get_block(self, number: int) -> WrapperBlock:
        block = self.web3.eth.getBlock(number, full_transactions=True)
        block = WrapperBlock(
            block['hash'].hex(),
            block['number'],
            block['timestamp'],
            [self._build_transaction(t) for t in block['transactions']],
        )

        internal_txs = self.etherscan.get_internal_txs(number)
        block.transactions = block.transactions + internal_txs

        return block

    @staticmethod
    def _build_transaction(tx):
        tx_hash = tx['hash']
        if isinstance(tx_hash, HexBytes):
            tx_hash = tx_hash.hex()

        output = WrapperOutput(
            tx_hash,
            0,
            tx['to'],
            tx['value'],
            tx['input']
        )

        tx_creates = tx.get('creates', None)

        # 'creates' is None when tx dont create any contract
        t = WrapperTransaction(
            tx_hash,
            [tx['from']],
            [output],
            bool(tx_creates),
            tx_creates
        )
        return t

    def get_tx_receipt(self, hash):
        tx_res = self.web3.eth.getTransactionReceipt(hash)
        return WrapperTransactionReceipt(
            tx_res['transactionHash'].hex(),
            tx_res['contractAddress'],
            tx_res['logs'],
            bool(tx_res['status']),
        )

    def get_processed_tx_receipt(self, tx_hash, token_name):
        tx_res = self.web3.eth.getTransactionReceipt(tx_hash)
        processed = self.erc20_contracts_dict[token_name].events.Transfer().processReceipt(tx_res)
        return processed


class EtherScanAPI:
    """
    Interface for EtherScan API.

    We can't get internal transactions from ETH RPC, cause they aren't actual transactions.
    But EtherScan allow us to get this info.

    Makes request with considering the limit. Without API key it's only one request per 3 sec.
    """

    def __init__(self):
        self.requests_per_second = 0.3
        self.last_request_time = 0.0

    def get_internal_txs(self, block_number):
        """
        Compare API limit with last request time.
        If requests over limits - wait and try again after.
        """
        seconds_for_request = 1 / self.requests_per_second
        now = time.time()
        time_diff = now - self.last_request_time

        if time_diff >= seconds_for_request:
            self.last_request_time = now
            return self._get_internal_txs(block_number)
        else:
            time.sleep(seconds_for_request - time_diff)
            return self.get_internal_txs(block_number)

    @staticmethod
    def _get_internal_txs(block_number):
        params = {
            'module': 'account',
            'action': 'txlistinternal',
            'startblock': block_number,
            'endblock': block_number,
        }

        r = requests.get('https://api.etherscan.io/api', params=params)
        data = r.json()

        txs = data.get('result')

        answer = []
        for tx in txs:
            t = EthNetwork._build_transaction(tx)
            answer.append(t)

        return answer
