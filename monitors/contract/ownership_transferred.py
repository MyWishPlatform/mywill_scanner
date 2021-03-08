from base import BlockEvent, BaseMonitor, Transaction
from models import ETHContract, Contract, Network, session
from contracts import token_abi


class OwnershipMonitor(BaseMonitor):
    event_type = 'ownershipTransferred'

    def on_new_block_event(self, block_event: BlockEvent):
        to_addresses = {}
        for transactions_list in block_event.transactions_by_address.values():
            for transaction in transactions_list:
                to_addresses[transaction.outputs[0].address] = transaction

        eth_contracts = session.query(ETHContract, Contract, Network)\
            .filter(Contract.id == ETHContract.contract_id, Contract.network_id == Network.id)\
            .filter(ETHContract.address.in_(to_addresses.keys()))\
            .filter(Network.name == block_event.network.type).all()
        
        for contract in eth_contracts:
            transaction: Transaction = to_addresses[contract[0].address]

            con = block_event.network.rpc.eth.contract(abi=token_abi)
            tx_res = block_event.network.rpc.eth.getTransactionReceipt(transaction.tx_hash)
            tx_receipt = con.events.OwnershipTransferred().processReceipt(tx_res)

            if not tx_receipt or tx_receipt[0]['event'] != 'OwnershipTransferred':
                continue

            message = {
                'contractId': contract[0].id,
                'crowdsaleId': contract[0].id,
                'transactionHash': transaction.tx_hash,
                'new owner': tx_receipt[0]['args']['newOwner'],
                'address': transaction.creates,
                'success': True,
                'status': 'COMMITTED'
            }

            self.send_to_backend(message)
