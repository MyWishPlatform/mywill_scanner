from eventscanner.queue.pika_handler import send_to_backend
from mywish_models.models import UserSiteBalance, session
from scanner.events.block_event import BlockEvent


class ERC20PaymentMonitor:

    network_types = ['ETHEREUM_MAINNET']
    event_type = 'payment'

    tokenAddressSwap = ''

    address_to_currency = [
        tokenAddressSwap
    ]

    @classmethod
    def on_new_block_event(cls, block_event: BlockEvent):
        if block_event.network.type not in cls.network_types:
            return

        addresses = block_event.transactions_by_address.keys()
        for token_address in cls.address_to_currency:
            if token_address in addresses:
                transactions = block_event.transactions_by_address[token_address]
                return cls.handle(token_address, transactions, block_event.network)

    @classmethod
    def handle(cls, token_address: str, transactions, network):
        for tx in transactions:
            if token_address.lower() != tx.outputs[0].address:
                continue

            tx_receipt = network.get_tx_receipt(tx.tx_hash)

            processed_receipt = network.get_processed_tx_receipt(tx_receipt)
            transfer_to = processed_receipt[0].args.to
            tokens_amount = processed_receipt[0].args.value

            user_site_balance = session.query(UserSiteBalance).\
                filter(UserSiteBalance.eth_address == transfer_to).all()
            if not user_site_balance:
                return

            message = {
                "transaction": tx.tx_hash,
                "address": user_site_balance.eth_address,
                "amount": tokens_amount,
                "currency": 'SWAP',
                "success": True
            }

            send_to_backend(cls.event_type, 'notification-ducatusx-mainnet', message)
