import typing

from blockchain_common.wrapper_block import WrapperBlock
from blockchain_common.wrapper_transaction_receipt import WrapperTransactionReceipt


class WrapperNetwork:
    def __init__(self, type: str):
        self.type = type

        # Base for list of rpc
        self._rpc = []
        self._rpc_counter = 0

    def add_rpc(self, o):
        self._rpc.append(o)

    @property
    def rpc(self):
        """
        Split up requests to providers equally.
        """
        if len(self._rpc) == 0:
            return self._rpc[0]

        self._rpc_counter += 1
        if self._rpc_counter >= len(self._rpc):
            self._rpc_counter = 0
        return self._rpc[self._rpc_counter]

    def get_last_block(self):
        pass

    def get_balance(self):
        pass

    def get_block(self, number: int) -> WrapperBlock:
        pass

    def get_tx_receipt(self, hash: str) -> WrapperTransactionReceipt:
        pass

    def get_balance_async(self):
        pass

    def getTxReceiptAsync(self):
        pass

    def is_pending_transactions_supported(self):
        pass

    def fetch_pending_transactions(self):
        pass
