from web3 import Web3

from blockchain_common.eth_tokens import erc20_abi
from blockchain_common.wrapper_block import WrapperBlock
from blockchain_common.wrapper_network import WrapperNetwork
from blockchain_common.wrapper_output import WrapperOutput
from blockchain_common.wrapper_transaction import WrapperTransaction
from blockchain_common.wrapper_transaction_receipt import WrapperTransactionReceipt
from settings.settings_local import NETWORKS, ERC20_TOKENS


class EthNetwork(WrapperNetwork):

    def __init__(self, type):
        super().__init__(type)
        url = NETWORKS[type]['url']
        self.w3_interface = Web3(Web3.HTTPProvider(url))

        self.erc20_contracts_dict = {t_name: self.w3_interface.eth.contract(
            self.w3_interface.toChecksumAddress(t_address),
            abi=erc20_abi
        ) for t_name, t_address in ERC20_TOKENS.items()}

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

        tx_creates = tx.get('creates', None)

        # 'creates' is None when tx dont create any contract
        t = WrapperTransaction(
            tx['hash'].hex(),
            [tx['from']],
            [output],
            bool(tx_creates),
            tx_creates
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

    def get_processed_tx_receipt(self, tx_hash, token_name):
        tx_res = self.w3_interface.eth.getTransactionReceipt(tx_hash)
        processed = self.erc20_contracts_dict[token_name].events.Transfer().processReceipt(tx_res)
        return processed
