import json
import requests

from base import BlockEvent, BaseMonitor
from models import DepositModel, session
from models import session
from settings import CONFIG


class BTCPaymentMonitor(BaseMonitor):
    event_type = 'payment'
    currency: str
    bitcore_url: str

    def __init__(self, network):
        super().__init__(network)
        config = CONFIG['networks'][self.network_type]
        currency = config.get('currency')
        bitcore_url = config.get('bitcore_url')
        # currency = 'BTC'
        if not currency:
            raise TypeError(f'currency field should be specified for {self.network_type} network.')
        self.currency = currency
        if not bitcore_url:
            raise TypeError(f'bitcore_url field should be specified for {self.network_type} network.')
        self.bitcore_url = bitcore_url

    def get_sent_from_address(self, tx_hash):
        tx_status_url = self.bitcore_url + f'tx/{tx_hash}/coins'
        res = requests.get(tx_status_url)
        try:
            return res.json()['inputs'][0]['address']
        except (KeyError, IndexError):
            return None
        except Exception as err:
            logger.debug(f'requested tx_status_url returned unknown error: {err}')
            return None

    def get_sent_to_address(self, model):
        return getattr(model, 'hd_wallet_address')

    def on_new_block_event(self, block_event: BlockEvent):
        addresses = block_event.transactions_by_address.keys()
        print(f'ADDRESSES: {addresses}')
        matched_deposits = session.query(DepositModel).filter(
            self.get_sent_to_address(DepositModel).in_(addresses)).all()
        print(f"MATCHED DEPOSITS: {matched_deposits}")
        for deposit in matched_deposits:
            address = self.get_sent_to_address(deposit)
            transactions = block_event.transactions_by_address[address]
            if not transactions:
                print('{}: User {} received from DB, but was not found in transaction list (block {}).'.format(
                    block_event.network.type, user_site_balance, block_event.block.number))

            for transaction in transactions:
                for output in transaction.outputs:
                    print(f"ADDRESS:{address} , OUTPUT.ADDRESS: {output.address}")
                    if address not in output.address:
                        print('{}: Found transaction out from internal address. Skip it.'
                              .format(block_event.network.type), flush=True)
                        continue
                    message = {
                        'depositId': deposit.id,
                        'fromAddress': self.get_sent_from_address(transaction.tx_hash),
                        'address': address,
                        'transactionHash': transaction.tx_hash,
                        'currency': self.currency,
                        'amount': output.value,
                        'success': True,
                        'status': 'COMMITTED'
                    }
                    self.send_to_backend(message)

