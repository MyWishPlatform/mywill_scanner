from base import BlockEvent, BaseMonitor
from models import UserSiteBalance, session
from settings import CONFIG


class EthPaymentMonitor(BaseMonitor):
    event_type = 'payment'
    currency: str

    def __init__(self, network):
        super().__init__(network)
        currency = CONFIG['networks'][self.network_type].get('currency')
        if not currency:
            raise TypeError(f'currency field should be specified for {self.network_type} network.')
        self.currency = currency
        self.address_field_name = '{}_address'.format(self.currency.lower())

    def on_new_block_event(self, block_event: BlockEvent):
        addresses = block_event.transactions_by_address.keys()
        user_site_balances = session.query(UserSiteBalance).filter(
            getattr(UserSiteBalance, self.address_field_name).in_(addresses)
        ).all()
        for user_site_balance in user_site_balances:
            address = getattr(user_site_balance, self.address_field_name)
            transactions = block_event.transactions_by_address[address.lower()]

            if not transactions:
                print('{}: User {} received from DB, but was not found in transaction list (block {}).'.format(
                    block_event.network.type, user_site_balance, block_event.block.number))

            for transaction in transactions:
                if address.lower() != transaction.outputs[0].address.lower():
                    print('{}: Found transaction out from internal address. Skip it.'.format(block_event.network.type),
                          flush=True)
                    continue

                tx_receipt = block_event.network.get_tx_receipt(transaction.tx_hash)

                message = {
                    'exchangeId': user_site_balance.id,
                    'address' : address,
                    'transactionHash': transaction.tx_hash,
                    'currency': self.currency,
                    'amount': transaction.outputs[0].value,
                    'success': tx_receipt.success,
                    'status': 'COMMITTED'
                }

                self.send_to_backend(message)
