from base import BlockEvent, BaseMonitor
from models import UserSiteBalance, session
from settings import CONFIG


class ERC20PaymentMonitor(BaseMonitor):
    event_type = 'payment'
    tokens = CONFIG['erc20_tokens']

    def on_new_block_event(self, block_event: BlockEvent):
        print('erc20 start')
        addresses = block_event.transactions_by_address.keys()

        for token_name, token_address in self.tokens.items():
            token_address = token_address.lower()
            print(token_address)
            print('addresses:',addresses)
            if token_address in addresses:
                transactions = block_event.transactions_by_address[token_address]
                self.handle(token_address, token_name, transactions, block_event.network)

    def handle(self, token_address: str, token_name, transactions, network):
        print('handle start')
        for tx in transactions:
            if token_address.lower() != tx.outputs[0].address.lower():
                continue
            print('first if end')
            processed_receipt = network.get_processed_tx_receipt(tx.tx_hash, token_name)
            transfer_to = processed_receipt[0].args.to
            tokens_amount = processed_receipt[0].args.value

            user_site_balance = session.query(UserSiteBalance).\
                filter(UserSiteBalance.eth_address == transfer_to.lower()).first()
            if not user_site_balance:
                continue
            print('second if end')
            message = {
                "exchangeId": user_site_balance.id,
                "transactionHash": tx.tx_hash,
                "address": user_site_balance.eth_address,
                "amount": tokens_amount,
                "currency": token_name,
                "status": "COMMITTED",
                "success": True
            }
            print('self.send_to_back(message) start')
            self.send_to_backend(message)
