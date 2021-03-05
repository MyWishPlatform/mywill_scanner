from base import BlockEvent, BaseMonitor, Transaction
from models import ETHContract, Contract, Network, session


class InitializedMonitor(BaseMonitor):
    event_type = 'initialized'

    def on_new_block_event(self, block_event: BlockEvent):
        to_addresses = {}
        for transactions_list in block_event.transactions_by_address.values():
            for transaction in transactions_list:
                to_addresses[transaction.outputs[0].address] = transaction

        contracts = session.query(ETHContract, Contract, Network)\
            .filter(Contract.id == ETHContract.contract_id, Contract.network_id == Network.id)\
            .filter(ETHContract.address.in_(to_addresses.keys()))\
            .filter(Network.name == block_event.network.type).all()

        for contract in contracts:
            transaction: Transaction = to_addresses[contract[0].address]

            if transaction.outputs[0].raw_output_script != '0xe1c7392a':
                continue

            message = {
                'contractId': contract[0].id,
                'crowdsaleId': contract[0].id,
                'transactionHash': transaction.tx_hash,
                'address': transaction.creates,
                'success': True,
                'status': 'COMMITTED'
            }

            self.send_to_backend(message)
