from sqlalchemy import or_
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

    def on_new_block_event(self, block_event: BlockEvent):
        addresses = block_event.transactions_by_address.keys()
        user_site_balances = session.query(UserSiteBalance).filter(
            or_(
                UserSiteBalance.eth_address.in_(addresses),
                UserSiteBalance.ducx_address.in_(addresses),
            )
        ).all()
        for user_site_balance in user_site_balances:
            transactions = block_event.transactions_by_address[user_site_balance.eth_address.lower()]

            if not transactions:
                print('{}: User {} received from DB, but was not found in transaction list (block {}).'.format(
                    block_event.network.type, user_site_balance, block_event.block.number))

            for transaction in transactions:
                if user_site_balance.eth_address.lower() != transaction.outputs[0].address.lower():
                    print('{}: Found transaction out from internal address. Skip it.'.format(block_event.network.type),
                          flush=True)
                    continue

                tx_receipt = block_event.network.get_tx_receipt(transaction.tx_hash)

                message = {
                    'exchangeId': user_site_balance.id,
                    'address' : user_site_balance.eth_address,
                    'transactionHash': transaction.tx_hash,
                    'currency': self.currency,
                    'amount': transaction.outputs[0].value,
                    'success': tx_receipt.success,
                    'status': 'COMMITTED'
                }

                self.send_to_backend(message)
