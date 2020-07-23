from blockchain_common.litecoin_rpc import DucatuscoreInterface
from blockchain_common.wrapper_block import WrapperBlock
from blockchain_common.wrapper_network import WrapperNetwork
from blockchain_common.wrapper_output import WrapperOutput
from blockchain_common.wrapper_transaction import WrapperTransaction


class BTCNetwork(WrapperNetwork):

    def __init__(self, net_type: str):
        super().__init__(net_type)
        self.interface = DucatuscoreInterface(net_type)

    def get_last_block(self):
        return self.interface.rpc.getblockcount()

    def get_block(self, number: int) -> WrapperBlock:
        block_hash = self.interface.rpc.getblockhash(number)
        block = self.interface.rpc.getblock(block_hash, 2)
        # block['tx'] = [self.interface.rpc.getrawtransaction(t, 1) for t in block['tx']]

        transactions = [WrapperTransaction(
            t['txid'],
            [i for i in t['vin']],
            self._build_outputs(t),
            False,
            ""
        ) for t in block['tx']]

        wb = WrapperBlock(
            block['hash'],
            block['height'],
            block['time'],
            transactions
        )
        return wb

    def _build_outputs(self, tx) -> [WrapperOutput]:
        vout = tx['vout']
        return [WrapperOutput(
            tx['hash'],
            o['n'],
            o['scriptPubKey']['addresses'],
            int(o['value']),
            None
        ) for o in vout if o['scriptPubKey']['type'] != 'nulldata']
