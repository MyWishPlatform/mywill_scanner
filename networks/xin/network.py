import http.client
import json

from hexbytes import HexBytes

from base import Block, Output, Transaction, TransactionReceipt, Network

from settings import CONFIG


class XinNetwork(Network):
    def __init__(self, type):
        super().__init__(type)
        config = CONFIG['networks'][type]

    def get_last_block(self):
        conn = http.client.HTTPSConnection("rpc.xinfin.network")

        payload = "{\"jsonrpc\":\"2.0\",\"method\":\"eth_blockNumber\",\"params\":[],\"id\":83}"

        headers = {'content-type': "application/json"}

        conn.request("POST", "//blockNumber", payload, headers)
        response = conn.getresponse()
        data_str = response.read().decode("utf-8")
        data_dictionary = json.loads(data_str)

        data_int = int(data_dictionary['result'], 16)

        return data_int

    def get_tx_receipt(self, hash):
        conn = http.client.HTTPSConnection("rpc.xinfin.network")

        payload = f"{{\"jsonrpc\":\"2.0\",\"method\":\"eth_getTransactionReceipt\",\"params\":[\"{hash}\"],\"id\":1}}"

        headers = {'content-type': "application/json"}

        conn.request("POST", "//getTransactionReceipt", payload, headers)

        response = conn.getresponse()
        data_str = response.read().decode("utf-8")
        tx_data = json.loads(data_str)

        return TransactionReceipt(
            tx_data['result']['transactionHash'],
            tx_data['result']['contractAddress'],
            tx_data['result']['logs'],
            bool(tx_data['result']['status']),
        )

    def get_block(self, number: int) -> Block:
        hex_number = hex(number)
        conn = http.client.HTTPSConnection("rpc.xinfin.network")
        payload = f"{{\"jsonrpc\":\"2.0\",\"method\":\"eth_getBlockByNumber\",\"params\":[\"{hex_number}\", true]," \
                  f"\"id\":1}} "

        headers = {'content-type': "application/json"}

        conn.request("POST", "//getBlockByNumber", payload, headers)

        response = conn.getresponse()
        data_str = response.read().decode("utf-8")
        data_dictionary = json.loads(data_str)

        number_integer = int(data_dictionary['result']['number'], 16)

        data_dictionary = Block(
            data_dictionary['result']['hash'],
            number_integer,
            data_dictionary['result']['timestamp'],
            [self._build_transaction(t) for t in (data_dictionary['result']['transactions'])],
        )

        return data_dictionary

    @staticmethod
    def _build_transaction(tx):
        tx_hash = tx['hash']
        if isinstance(tx_hash, HexBytes):
            tx_hash = tx_hash.hex()

        addr_to = tx['to']
        if addr_to[:3] == 'xdc':
            addr_to = addr_to.replace('xdc', '0x')

        output = Output(
            tx_hash,
            0,
            addr_to,
            tx['value'],
            tx['input']
        )

        contract_creation = tx['to'] is None
        tx_creates = tx.get('creates', None)

        addr_from = tx['from']
        if addr_from[:3] == 'xdc':
            addr_from = addr_from.replace('xdc', '0x')

        t = Transaction(
            tx_hash,
            addr_from,
            [output],
            contract_creation,
            tx_creates
        )
        return t

    def get_processed_tx_receipt(self, tx_hash, token_name):
        tx_res = self.rpc.eth.getTransactionReceipt(tx_hash)
        processed = self.erc20_contracts_dict[token_name].events.Transfer().processReceipt(tx_res)
        return processed