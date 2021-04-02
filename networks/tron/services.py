from base import Output, Transaction


class TronTransaction(Transaction):
    def __init__(self, tx_hash, inputs, outputs, contract_creation, contracts, status):
        creates = contracts[0] if contracts else None
        super().__init__(tx_hash, inputs, outputs, contract_creation, creates)
        self.contracts = contracts
        self.status = status

    @classmethod
    def build(cls, tx) -> 'TronTransaction':
        _hash = tx['txID']
        contract_wrapper = tx['raw_data']['contract'][0]
        contract = contract_wrapper['parameter']['value']
        owner_address = contract['owner_address']
        inputs = [owner_address]
        outputs = [cls._build_output(tx)]
        contract_creation = contract_wrapper['type'] == "CreateSmartContract"
        contracts = [tx.get('contract_address')] or []

        return cls(
            _hash,
            inputs,
            outputs,
            contract_creation,
            contracts,
            tx['ret'][0]['contractRet']
        )

    @classmethod
    def _build_output(cls, tx) -> 'Output':
        contract_wrapper = tx['raw_data']['contract'][0]
        contract_type = contract_wrapper['type']
        contract = contract_wrapper['parameter']['value']

        output_address = None
        value = None

        if contract_type == 'TriggerSmartContract':
            output_address = contract['contract_address']
            value = contract.get('call_value', 0)
        elif contract_type == 'TransferContract':
            output_address = contract['to_address']
            value = contract['amount']
        else:
            output_address = contract['owner_address']

        return Output(tx['txID'], 0, output_address, value, None)
