from eventscanner.queue.pika_handler import send_to_backend
from mywish_models.models import ExchangeRequests, session
from scanner.events.block_event import BlockEvent
from settings.settings_local import NETWORKS
to_address='0x3C83e7fBf9e62fb222d62229DD85016870DCA84F'.lower()

class EthPaymentMonitor:

    network_types = ['ETHEREUM_MAINNET']
    event_type = 'payment'
    queue = NETWORKS[network_types[0]]['queue']

    currency = 'ETH'

    @classmethod
    def address_from(cls, model):
        s = 'from_address'
        return getattr(model, s)

    @classmethod
    def on_new_block_event(cls, block_event: BlockEvent):
        if block_event.network.type not in cls.network_types:
            return
        addresses = block_event.transactions_by_address.keys()
        query_result = session.query(ExchangeRequests).filter(ExchangeRequests.from_address.in_(addresses)).all()
        for model in query_result:
            if model.from_currency not in cls.currency:
                continue
            address = cls.address_from(model)
            transactions = block_event.transactions_by_address[address.lower()]

            if not transactions:
                print('{}: User {} received from DB, but was not found in transaction list (block {}).'.format(
                    block_event.network.type, model, block_event.block.number))
                continue
            
            for transaction in transactions:
                if address.lower() != transaction.inputs[0].lower() or to_address!=transaction.outputs[0].address.lower():
                    print('addresses: {}, {}, {}, {}'.format(address.lower(),transaction.inputs[0].lower(), to_address, transaction.outputs[0].address.lower()))
                    print('{}: Found transaction out from internal address. Skip it.'.format(block_event.network.type),
                          flush=True)
                    continue
            
                tx_receipt = block_event.network.get_tx_receipt(transaction.tx_hash)
            
                message = {
                    'exchangeId': model.id,
                    'transactionHash': transaction.tx_hash,
                    'currency': cls.currency,
                    'amount': transaction.outputs[0].value,
                    'success': tx_receipt.success,
                    'status': 'COMMITTED'
                }

                send_to_backend(cls.event_type, cls.queue, message)