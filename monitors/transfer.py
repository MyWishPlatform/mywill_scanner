from base import BlockEvent, BaseMonitor
from models import Transfers, session
from settings import CONFIG


class TransferMonitor(BaseMonitor):
    network_type = []
    event_type = 'transferred'
    currency: str

    def __init__(self, network):
        super().__init__(network)
        currency = CONFIG['networks'][self.network_type].get('currency')
        if not currency:
            raise TypeError(f'currency field should be specified for {self.network_type} network.')
        self.currency = currency

    def on_new_block_event(self, block_event: BlockEvent):
        print('message')
        if block_event.network.type not in self.network_type:
            return

        tx_hashes = set()
        for address_transactions in block_event.transactions_by_address.values():
            for transaction in address_transactions:
                tx_hashes.add(transaction.tx_hash)

        transfers = session \
            .query(Transfers) \
            .filter(Transfers.tx_hash.in_(tx_hashes), Transfers.currency == self.currency) \
            .distinct(Transfers.tx_hash) \
            .all()
        for transfer in transfers:
            print('transfer')
            message = {
                'transactionHash': transfer.tx_hash,
                'transferId': transfer.id,
                'currency': self.currency,
                'amount': int(transfer.amount),
                'success': True,
                'status': 'COMMITTED',
            }
            self.send_to_backend(message)

