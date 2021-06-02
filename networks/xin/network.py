
import http.client
import json

from hexbytes import HexBytes

from base import Block, Output, Transaction, TransactionReceipt, Network
from networks.xin.xin_scan_api import XinFinScanAPI
from settings import CONFIG


class XinNetwork(Network):
    def __init__(self, type):
        super().__init__(type)
        config = CONFIG['networks'][type]

        self.xinscan_api_key = CONFIG['networks'][type].get('xinscan_api_key')
        self.is_testnet = CONFIG['networks'][type].get('is_testnet')
        self.xinscan = XinFinScanAPI(self.xinscan_api_key,
                                     self.is_testnet) if self.xinscan_api_key else None  # тут было (xinscan_api_key, .. )

    #
    # self.erc20_contracts_dict = {t_name: self.rpc.eth.contract(
    #     self.rpc.toChecksumAddress(t_address),
    #     abi=erc20_abi
    # ) for t_name, t_address in CONFIG['erc20_tokens'].items()}
    def get_last_block(self):
        conn = http.client.HTTPSConnection("rpc.xinfin.network")

        payload = "{\"jsonrpc\":\"2.0\",\"method\":\"eth_blockNumber\",\"params\":[],\"id\":83}"

        headers = {'content-type': "application/json"}

        conn.request("POST", "//blockNumber", payload, headers)
        response = conn.getresponse()
        data_str = response.read().decode("utf-8")
        data_dictionary = json.loads(data_str)
        # print(data_dictionary)
        # print(type(data_dictionary))
        data_int = int(data_dictionary['result'], 16)
        # print(data_int)
        return data_int

    def get_tx_receipt(self, hash):
        conn = http.client.HTTPSConnection("rpc.xinfin.network")

        payload = f"{{\"jsonrpc\":\"2.0\",\"method\":\"eth_getTransactionReceipt\",\"params\":[\"{hash}\"],\"id\":1}} "

        headers = {'content-type': "application/json"}

        conn.request("POST", "//getTransactionReceipt", payload, headers)

        response = conn.getresponse()
        data_str = response.read().decode("utf-8")
        tx_data = json.loads(data_str)

        return TransactionReceipt(
            tx_data["result"]["hash"],
            tx_data['contractAddress'],
            tx_data['logs'],
            bool(tx_data['status']),
        )

    def get_block(self, number: int) -> Block:
        hex_number = hex(number)
        print(hex_number)
        conn = http.client.HTTPSConnection("rpc.xinfin.network")
        payload = f"{{\"jsonrpc\":\"2.0\",\"method\":\"eth_getBlockByNumber\",\"params\":[\"{hex_number}\", true],\"id\":1}}"

        headers = {'content-type': "application/json"}

        conn.request("POST", "//getBlockByNumber", payload, headers)

        response = conn.getresponse()
        data_str = response.read().decode("utf-8")
        data_dictionary = json.loads(data_str)
        # print(data_dictionary)
        # print(type(data_dictionary))
        number_integer = int(data_dictionary['result']['number'], 16)
        # block = self.rpc.eth.getBlock(number, full_transactions=True)
        data_dictionary = Block(
            data_dictionary['result']['hash'],
            number_integer,
            data_dictionary['result']['timestamp'],
            [self._build_transaction(t) for t in (data_dictionary['result']['transactions'])],
        )
        print(data_dictionary)

        if self.xinscan:
            internal_txs = [self._build_transaction(t) for t in self.xinscan.get_internal_txs(number)]
            data_dictionary.transactions += internal_txs

        return data_dictionary

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

    def get_processed_tx_receipt(self, tx_hash, token_name):
        tx_res = self.rpc.eth.getTransactionReceipt(tx_hash)
        processed = self.erc20_contracts_dict[token_name].events.Transfer().processReceipt(tx_res)
        return processed
