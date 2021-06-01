from base import BlockEvent, BaseMonitor, Transaction
from models import ETHContract, Contract, Network, session


class DeployMonitor(BaseMonitor):
    event_type = 'deployed'

    def on_new_block_event(self, block_event: BlockEvent):
        print(block_event)
        print('евент блок 1')
        deploy_hashes = {}
        for transactions_list in block_event.transactions_by_address.values():
            transactions_list_dic = transactions_list.__dict__
            print(transactions_list_dic)
            print("лист транзакций")
            print(block_event)
            print("блок эвент 2")

            for transaction in transactions_list:
                if transaction.contract_creation:
                    print("зашел в иф")
                    deploy_hashes[transaction.tx_hash.lower()] = transaction
                    print(deploy_hashes)
                    print('deploy hash')

        eth_contracts = session.query(ETHContract, Contract, Network)\
            .filter(Contract.id == ETHContract.contract_id, Contract.network_id == Network.id)\
            .filter(ETHContract.tx_hash.in_(deploy_hashes.keys()))\
            .filter(Network.name == block_event.network.type).all()
        print(block_event)
        print("блок эвент 3")
        print(eth_contracts)
        print("контракты после фильтра")

        for contract in eth_contracts:
            print("eth_id:", contract[0].id, "contract_id", contract[0].contract_id, contract[0].tx_hash)
            transaction: Transaction = deploy_hashes[contract[0].tx_hash]
            tx_receipt = block_event.network.get_tx_receipt(transaction.tx_hash)

            message = {
                'contractId': contract[0].id,
                'transactionHash': transaction.tx_hash,
                'address': transaction.creates,
                'success': tx_receipt.success,
                'status': 'COMMITTED'
            }

            self.send_to_backend(message)
