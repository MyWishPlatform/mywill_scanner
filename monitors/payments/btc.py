import json
import requests

from base import BlockEvent, BaseMonitor
from models import UserSiteBalance, session
from settings import CONFIG


class BTCPaymentMonitor(BaseMonitor):
    event_type = 'payment'
    currency: str
    tx_status_url: str

    def __init__(self, network):
        super().__init__(network)
        config = CONFIG['networks'][self.network_type]
        currency = config.get('currency')
        tx_status_url = config.get('tx_status_url')
        # currency = 'BTC'
        if not currency:
            raise TypeError(f'currency field should be specified for {self.network_type} network.')
        self.currency = currency
        if not tx_status_url:
            raise TypeError(f'tx_status_url field should be specified for {self.network_type} network.')
        self.tx_status_url = tx_status_url

    def get_sent_from_address(self, tx_hash):
        res = requests.get(self.tx_status_url.format(tx_hash))
        try:
            return res.json()['inputs'][0]['address']
        except (KeyError, IndexError):
            return None
        except Exception as err:
            logger.debug(f'requested tx_status_info returned unknown error: {err}')
            return None

    def get_sent_to_address(self, model):
        s = self.currency.lower() + '_address'
        return getattr(model, s)

    def on_new_block_event(self, block_event: BlockEvent):
        addresses = block_event.transactions_by_address.keys()
        user_site_balances = session.query(UserSiteBalance).filter(
            self.get_sent_to_address(UserSiteBalance).in_(addresses)).all()
        for user_site_balance in user_site_balances:
            address = self.get_sent_to_address(user_site_balance)
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
                        'fromAddress': self.get_sent_from_address(transaction.tx_hash),
                        'address': address,
                        'transactionHash': transaction.tx_hash,
                        'currency': self.currency,
                        'amount': output.value,
                        'success': True,
                        'status': 'COMMITTED'
                    }
                self.send_to_backend(message)

