from tronapi import Tron

from blockchain_common.wrapper_network import WrapperNetwork
from blockchain_common.wrapper_block import WrapperBlock
from networks.tron.services import TronWrapperOutput, TronWrapperTransaction


class TronNetwork(WrapperNetwork):

    def __init__(self, type):
        super().__init__(type)

        self.tron = Tron()

    def get_last_block(self):
        return self.tron.trx.get_block('latest')['block_header']['raw_data']['number']

    def get_block(self, number: int):
        block = self.tron.trx.get_block(number)
        return WrapperBlock(
            block['blockID'],
            block['block_header']['raw_data']['number'],
            block['block_header']['raw_data']['timestamp'],
            [TronWrapperTransaction.build(t) for t in block['transactions']],
        )

    def get_tx_receipt(self, hash: str):
        return self.tron.get_event_transaction_id(hash)
