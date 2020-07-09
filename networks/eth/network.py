from web3 import Web3

from blockchain_common.wrapper_block import WrapperBlock
from blockchain_common.wrapper_network import WrapperNetwork
from blockchain_common.wrapper_transaction import WrapperTransaction
from blockchain_common.wrapper_output import WrapperOutput
from blockchain_common.wrapper_transaction_receipt import WrapperTransactionReceipt

from settings.settings_local import NETWORKS


class EthNetwork(WrapperNetwork):

    def __init__(self, type):
        super().__init__(type)
        url = NETWORKS[type]['url']
        self.w3_interface = Web3(Web3.HTTPProvider(url))

    def get_last_block(self):
        return self.w3_interface.eth.blockNumber

    def get_block(self, number: int) -> WrapperBlock:
        block = self.w3_interface.eth.getBlock(number, full_transactions=True)
        block = WrapperBlock(
            block['hash'].hex(),
            block['number'],
            block['timestamp'],
            [self._build_transaction(t) for t in block['transactions']],
        )
        return block

    @staticmethod
    def _build_transaction(tx):
        output = WrapperOutput(
            tx['hash'],
            0,
            tx['to'],
            tx['value'],
            tx['input']
        )

        # 'creates' is None when tx dont create any contract
        t = WrapperTransaction(
            tx['hash'].hex(),
            [tx['from']],
            [output],
            bool(tx['creates']),
            tx['creates']
        )
        return t

    def get_tx_receipt(self, hash):
        tx_res = self.w3_interface.eth.getTransactionReceipt(hash)
        return WrapperTransactionReceipt(
            tx_res['transactionHash'].hex(),
            tx_res['contractAddress'],
            tx_res['logs'],
            bool(tx_res['status']),
        )
