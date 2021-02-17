from eventscanner.queue.pika_handler import send_to_backend
from mywish_models.models import UserSiteBalance, session
from scanner.events.block_event import BlockEvent
from settings import CONFIG


class ERC20PaymentMonitor:

    network_types = ['ETHEREUM_MAINNET']
    event_type = 'payment'
    queue = CONFIG['networks'][network_types[0]]['queue']

    tokens = CONFIG['erc20_tokens']

    @classmethod
    def on_new_block_event(cls, block_event: BlockEvent):
        if block_event.network.type not in cls.network_types:
            return

        addresses = block_event.transactions_by_address.keys()
        for token_name, token_address in cls.tokens.items():
            token_address = token_address.lower()
            if token_address in addresses:
                transactions = block_event.transactions_by_address[token_address]
                return cls.handle(token_address, token_name, transactions, block_event.network)

    @classmethod
    def handle(cls, token_address: str, token_name, transactions, network):
        for tx in transactions:
            if token_address.lower() != tx.outputs[0].address.lower():
                continue

            processed_receipt = network.get_processed_tx_receipt(tx.tx_hash, token_name)
            transfer_to = processed_receipt[0].args.to
            tokens_amount = processed_receipt[0].args.value

            user_site_balance = session.query(UserSiteBalance).\
                filter(UserSiteBalance.eth_address == transfer_to.lower()).first()
            if not user_site_balance:
                return

            message = {
                "userId": user_site_balance.user_id,
                "siteId": user_site_balance.subsite_id,
                "transactionHash": tx.tx_hash,
                "address": user_site_balance.eth_address,
                "amount": tokens_amount,
                "currency": token_name,
                "status": "COMMITTED",
                "success": True
            }

            send_to_backend(cls.event_type, cls.queue, message)
