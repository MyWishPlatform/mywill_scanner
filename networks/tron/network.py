from tronapi import Tron

from blockchain_common.wrapper_block import WrapperBlock
from blockchain_common.wrapper_network import WrapperNetwork
from networks.tron.services import TronWrapperTransaction
from settings.settings_local import NETWORKS


class TronNetwork(WrapperNetwork):

    def __init__(self, type):
        super().__init__(type)
        settings = NETWORKS[type]

        node_url = settings['host']
        pk = settings['private_key']

        self.tron = Tron(
            full_node=node_url,
            solidity_node=node_url,
            event_server=node_url,
            private_key=pk
        )

    def get_last_block(self):
        return self.tron.trx.get_block('latest')['block_header']['raw_data']['number']

    def get_block(self, number: int):
        block = self.tron.trx.get_block(number)
        transactions = block.get('transactions', [])
        return WrapperBlock(
            block['blockID'],
            block['block_header']['raw_data']['number'],
            block['block_header']['raw_data']['timestamp'],
            [TronWrapperTransaction.build(t) for t in transactions],
        )

    def get_tx_receipt(self, hash: str):
        return self.tron.get_event_transaction_id(hash)
