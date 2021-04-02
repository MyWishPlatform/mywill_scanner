from tronapi import Tron

from base import Block, Network
from settings import CONFIG
from .services import TronTransaction


class TronNetwork(Network):

    def __init__(self, type):
        super().__init__(type)
        config = CONFIG['networks'][type]
        node_url = config['url']
        pk = config['private_key']

        tron = Tron(
            full_node=node_url,
            solidity_node=node_url,
            event_server=node_url,
            private_key=pk
        )
        self.add_rpc(tron)

    def get_last_block(self):
        return self.rpc.trx.get_block('latest')['block_header']['raw_data']['number']

    def get_block(self, number: int):
        block = self.rpc.trx.get_block(number)
        transactions = block.get('transactions', [])
        return Block(
            block['blockID'],
            block['block_header']['raw_data']['number'],
            block['block_header']['raw_data']['timestamp'],
            [TronTransaction.build(t) for t in transactions],
        )

    def get_tx_receipt(self, hash: str):
        return self.rpc.get_event_transaction_id(hash)
