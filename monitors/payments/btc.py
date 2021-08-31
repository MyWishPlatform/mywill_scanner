from base import BlockEvent, BaseMonitor
from models import UserSiteBalance, session
from settings import CONFIG


class BTCPaymentMonitor(BaseMonitor):
    event_type = 'payment'
    currency: str

    def __init__(self, network):
        super().__init__(network)
        currency = CONFIG['networks'][self.network_type].get('currency')
        # currency = 'BTC'
        if not currency:
            raise TypeError(f'currency field should be specified for {self.network_type} network.')
        self.currency = currency


    def address_from(self, model):
        s = self.currency.lower() + '_address'
        return getattr(model, s)
    

    def on_new_block_event(self, block_event: BlockEvent):
        addresses = block_event.transactions_by_address.keys()
        user_site_balances = session.query(UserSiteBalance).filter(self.address_from(UserSiteBalance).in_(addresses)).all()
        for user_site_balance in user_site_balances:
            address = self.address_from(user_site_balance)
            transactions = block_event.transactions_by_address[address]
            if not transactions:
                print('{}: User {} received from DB, but was not found in transaction list (block {}).'.format(
                    block_event.network.type, user_site_balance, block_event.block.number))

            for transaction in transactions:
                for output in transaction.outputs:
                    if address not in output.address:
                        print('{}: Found transaction out from internal address. Skip it.'
                              .format(block_event.network.type), flush=True)
                        continue

                    message = {
                        'exchangeId': user_site_balance.id,
                        'address': address,
                        'transactionHash': transaction.tx_hash,
                        'currency': self.currency,
                        'amount': output.value,
                        'success': True,
                        'status': 'COMMITTED'
                    }

                self.send_to_backend(message)

