from pubsub import pub

from eventscanner.monitors.payments.eth_payment_monitor import EthPaymentMonitor

pub.subscribe(EthPaymentMonitor.on_new_block_event, 'ETHEREUM_MAINNET')
