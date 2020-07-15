from tronapi import Tron

from blockchain_common.wrapper_network import WrapperNetwork
from blockchain_common.wrapper_block import WrapperBlock
from blockchain_common.wrapper_transaction import WrapperTransaction
from blockchain_common.wrapper_output import WrapperOutput


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
            [self._build_transaction(t) for t in block['transactions']],
        )

    @classmethod
    def _build_transaction(cls, tx):
        _hash = tx['txID']
        contract_wrapper = tx['raw_data']['contract'][0]
        contract = contract_wrapper['parameter']['value']
        owner_address = contract['owner_address']
        inputs = [owner_address]
        outputs = cls._build_output(tx)
        contract_creation = contract_wrapper['type'] == "CreateSmartContract"
        contracts = [tx.get('contract_address')] or []

        return TronWrapperTransaction(
            tx['txID'],
            inputs,
            outputs,
            contract_creation,
            contracts,
            tx['ret'][0]['contractRet']
        )

    @classmethod
    def _build_output(cls, tx):
        contract_wrapper = tx['raw_data']['contract'][0]
        contract_type = contract_wrapper['type']
        contract = contract_wrapper['parameter']['value']

        output_address = None
        value = None

        if contract_type == 'TriggerSmartContract':
            output_address = contract['contract_address']
            call_value = contract.get('call_value')
            if call_value:
                value = call_value
        elif contract_type == 'TransferContract':
            output_address = contract['to_address']
            value = contract['amount']
        else:
            output_address = contract['owner_address']

        return TronWrapperOutput(tx['txID'], output_address, value, contract)


class TronWrapperTransaction(WrapperTransaction):
    def __init__(self, tx_hash, inputs, outputs: 'TronWrapperOutput', contract_creation, contracts, status):
        creates = contracts[0] if contracts else None
        super().__init__(tx_hash, inputs, outputs, contract_creation, creates)
        self.contracts = contracts
        self.status = status


class TronWrapperOutput(WrapperOutput):
    def __init__(self, parent_tx, address, value, contract):
        super().__init__(parent_tx, 0, address, value, None)
        self.contract = contract

