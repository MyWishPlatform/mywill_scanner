from decimal import Decimal

from blockchain_common.wrapper_network import WrapperNetwork
from blockchain_common.wrapper_block import WrapperBlock
from blockchain_common.wrapper_transaction import WrapperTransaction
from blockchain_common.wrapper_output import WrapperOutput
from blockchain_common.quras_rpc import QurasInterface
from settings.settings_local import DECIMALS, NETWORKS


class QurasNetwork(WrapperNetwork):
    def __init__(self, type):
        super().__init__(type)
        self.rpc = QurasInterface(type)

    def get_last_block(self):
        return self.rpc.getblockcount()

    def get_block(self, number: int) -> WrapperBlock:
        block = self.rpc.getblock(number, 1)

        transactions = [WrapperTransaction(
            t['txid'],
            [i for i in t['vin']],
            self._build_outputs(t),
            False,
            ""
        ) for t in block['tx']]

        wb = WrapperBlock(
            block['hash'],
            block['index'],
            block['time'],
            transactions
        )
        return wb

    def _build_outputs(self, tx) -> [WrapperOutput]:
        vout = tx['vout']
        return [WrapperOutput(
            tx['txid'],
            o['n'],
            o['address'],
            int(Decimal(o['value']) * DECIMALS['XQC_NATIVE']),
            None
        ) for o in vout]
