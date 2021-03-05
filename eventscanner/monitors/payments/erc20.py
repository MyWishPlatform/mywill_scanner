from settings import CONFIG
from base import BlockEvent, BaseMonitor
from models import UserSiteBalance, session
from eventscanner.queue.pika_handler import send_to_backend


class ERC20PaymentMonitor(BaseMonitor):
    event_type = 'payment'
    tokens = CONFIG['erc20_tokens']

    def on_new_block_event(self, block_event: BlockEvent):
        addresses = block_event.transactions_by_address.keys()
        for token_name, token_address in self.tokens.items():
            token_address = token_address.lower()
            if token_address in addresses:
                transactions = block_event.transactions_by_address[token_address]
                return self.handle(token_address, token_name, transactions, block_event.network)

    def handle(self, token_address: str, token_name, transactions, network):
        for tx in transactions:
            if token_address.lower() != tx.outputs[0].address.lower():
                continue

            processed_receipt = network.get_processed_tx_receipt(tx.tx_hash, token_name)
            transfer_to = processed_receipt[0].args.to
            tokens_amount = processed_receipt[0].args.value

            user_site_balance = session.query(UserSiteBalance).\
                filter(UserSiteBalance.eth_address == transfer_to.lower()).first()
            if not user_site_balance:
                continue

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

            send_to_backend(self.monitor_name, self.event_type, self.queue, message)
