from base.network import Network
from networks.btc import BTCInterface
from base.block import Block
from base.output import Output
from base.transaction import Transaction
from bitcoinrpc.authproxy import JSONRPCException


class BTCNetwork(Network):
    ignore_output_types = ['nulldata', 'nonstandard', 'pubkey', 'multisig']

    def __init__(self, type: str):
        super().__init__(type)
        self.interface = BTCInterface.BTCInterface(type)

    def get_last_block(self):
        return self.interface.rpc.getblockcount()

    def get_block(self, number: int) -> Block:
        block_hash = self.interface.rpc.getblockhash(number)

        # For BTC we can obtain block with filled tx objects,
        # but some rpc don't support this, and we need to obtain all tx manually
        try:
            block = self.interface.rpc.getblock(block_hash, 2)
        except JSONRPCException:
            block = self.interface.rpc.getblock(block_hash, True)
            block['tx'] = [self.interface.rpc.getrawtransaction(t, 1) for t in block['tx']]

        transactions = [Transaction(
            t['txid'],
            [i for i in t['vin']],
            self._build_outputs(t),
            False,
            ""
        ) for t in block['tx']]

        wb = Block(
            block['hash'],
            block['height'],
            block['time'],
            transactions
        )
        return wb

    def _build_outputs(self, tx) -> [Output]:
        vout = tx['vout']
        out_list = []
        for o in vout:
            if o['scriptPubKey']['type'] not in self.ignore_output_types:
                out_list.append(Output(tx['hash'], o['n'], o['scriptPubKey']['addresses'], self.interface.dec_to_int(o['value']), None))
        return out_list
    #    return [Output(
      #      tx['hash'],
     #       o['n'],
      #      o['scriptPubKey']['addresses'],
       #     self.interface.dec_to_int(o['value']),
       #     None
       # ) for o in vout if o['scriptPubKey']['type'] in self.ignore_output_types]


class APILimitError(Exception):
    ...
