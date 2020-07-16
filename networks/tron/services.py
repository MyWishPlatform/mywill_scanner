from blockchain_common.wrapper_output import WrapperOutput
from blockchain_common.wrapper_transaction import WrapperTransaction


class TronWrapperOutput(WrapperOutput):
    def __init__(self, parent_tx, address, value, contract):
        super().__init__(parent_tx, 0, address, value, None)
        self.contract = contract

    @classmethod
    def build(cls, tx) -> 'TronWrapperOutput':
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

        return cls(tx['txID'], output_address, value, contract)


class TronWrapperTransaction(WrapperTransaction):
    def __init__(self, tx_hash, inputs, outputs: ['TronWrapperOutput'], contract_creation, contracts, status):
        creates = contracts[0] if contracts else None
        super().__init__(tx_hash, inputs, outputs, contract_creation, creates)
        self.contracts = contracts
        self.status = status


    @classmethod
    def build(cls, tx):
        _hash = tx['txID']
        contract_wrapper = tx['raw_data']['contract'][0]
        contract = contract_wrapper['parameter']['value']
        owner_address = contract['owner_address']
        inputs = [owner_address]
        outputs = [TronWrapperOutput.build(tx)]
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
