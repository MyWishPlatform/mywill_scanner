from pubsub import pub

from eventscanner.monitors.payments.eth_payment_monitor import EthPaymentMonitor
from eventscanner.monitors.payments.tron_payment_monitor import TronPaymentMonitor

pub.subscribe(EthPaymentMonitor.on_new_block_event, 'ETHEREUM_MAINNET')
pub.subscribe(TronPaymentMonitor.on_new_block_event, 'TRON_MAINNET')
