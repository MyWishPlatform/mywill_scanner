import ast
import http.client


from hexbytes import HexBytes

from base import Block, Output, Transaction, TransactionReceipt, Network
from networks.xin.xin_api import XinFinScanAPI
from settings import CONFIG


def get_last_block():
    conn = http.client.HTTPSConnection("rpc.xinfin.network")

    payload = "{\"jsonrpc\":\"2.0\",\"method\":\"eth_blockNumber\",\"params\":[latest, true],\"id\":1}"

    headers = {'content-type': "application/json"}

    conn.request("POST", "//getBlockByNumber", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
    return data


def get_tx_receipt():
    conn = http.client.HTTPSConnection("rpc.xinfin.network")

    payload = "{\"jsonrpc\":\"2.0\",\"method\":\"eth_getTransactionReceipt\",\"params\":[" \
              "\"0xa3ece39ae137617669c6933b7578b94e705e765683f260fcfe30eaa41932610f\"],\"id\":1} "

    headers = {'content-type': "application/json"}

    conn.request("POST", "//getTransactionReceipt", payload, headers)

    res = conn.getresponse()
    tx_res = res.read()
    tx_dict = tx_res.decode("UTF-8")
    tx_data = ast.literal_eval(tx_dict)

    return TransactionReceipt(
        tx_data['transactionHash'].hex(),
        tx_data['contractAddress'],
        tx_data['logs'],
        bool(tx_data['status']),
    )


class XinNetwork(Network):

    def __init__(self, type):
        print('1Xin ' + type)
        super().__init__(type)
        print('2Xin ' + type)

        xinscan_api_key = CONFIG['networks'][type].get('xinscan_api_key')
        is_testnet = CONFIG['networks'][type].get('is_testnet')
        xinscan = XinFinScanAPI(xinscan_api_key, is_testnet) if xinscan_api_key else None

    #
    # self.erc20_contracts_dict = {t_name: self.rpc.eth.contract(
    #     self.rpc.toChecksumAddress(t_address),
    #     abi=erc20_abi
    # ) for t_name, t_address in CONFIG['erc20_tokens'].items()}

    def get_block(self, number: int) -> Block:
        conn = http.client.HTTPSConnection("rpc.xinfin.network")
        payload = "{\"jsonrpc\":\"2.0\",\"method\":\"eth_getBlockByNumber\",\"params\":[true, latest],\"id\":}"

        headers = {'content-type': "application/json"}

        conn.request("POST", "//getBlockByNumber", payload, headers)

        res = conn.getresponse()
        block = res.read()
        dict_block = block.decode("UTF-8")
        block_data = ast.literal_eval(dict_block)

        # block = self.rpc.eth.getBlock(number, full_transactions=True)
        block_data = Block(
            block_data['hash'].hex(),
            block_data['number'],
            block_data['timestamp'],
            [self._build_transaction(t) for t in block_data['transactions']],
        )

        if self.xinscan:
            internal_txs = [self._build_transaction(t) for t in self.xinscan.get_internal_txs(number)]
            block_data.transactions += internal_txs

        return block_data

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

    # def get_processed_tx_receipt(self, tx_hash, token_name):
    #     tx_data = get_tx_receipt(tx_hash)
    #     processed = self.erc20_contracts_dict[token_name].events.Transfer().processReceipt(tx_data)
    # return processed
