from scanner.events.block_event import BlockEvent
from mywish_models.models import ETHContract, Contract, Network, session
from blockchain_common.wrapper_transaction import WrapperTransaction
from eventscanner.queue.pika_handler import send_to_backend

from settings.settings_local import NETWORKS


class AirdropMonitor:
    network_types = ['MATIC_MAINNET', 'MATIC_TESTNET']
    event_type = 'airdrop'

    @classmethod
    def on_new_block_event(cls, block_event: BlockEvent):
        if block_event.network.type not in cls.network_types:
            return
        return

        to_addresses = dict()
        for transactions_list in block_event.transactions_by_address.values():
            for transaction in transactions_list:
                to_addresses[transaction.outputs[0].address] = transaction

        eth_contracts = session.query(ETHContract, Contract, Network) \
            .filter(Contract.id == ETHContract.contract_id, Contract.network_id == Network.id) \
            .filter(ETHContract.address.in_(to_addresses.keys())) \
            .filter(Network.name == block_event.network.type).all()

        for contract in eth_contracts:
            transaction: WrapperTransaction = to_addresses[contract[0].address]
            tx_receipt = block_event.network.get_ownership_transfer_receipt(transaction.tx_hash)

            if tx_receipt[0]['event'] != 'Airdrop':
                continue

            message = {
                'contractId': contract[0].id,
                'status': 'COMMITTED',
                'airdroppedAddresses': None
            }

            print("AIRDROP AAAAAAA", transaction.tx_hash)
            print("AIRDROP BBBBBBB", transaction.creates)

            send_to_backend(cls.event_type, NETWORKS[block_event.network.type]['queue'], message)
