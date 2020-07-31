from pubsub import pub

from eventscanner.monitors.payments import EthPaymentMonitor, ERC20PaymentMonitor
from eventscanner.monitors.payments.tron_payment_monitor import TronPaymentMonitor

pub.subscribe(EthPaymentMonitor.on_new_block_event, 'ETHEREUM_MAINNET')
pub.subscribe(ERC20PaymentMonitor.on_new_block_event, 'ETHEREUM_MAINNET')
pub.subscribe(TronPaymentMonitor.on_new_block_event, 'TRON_MAINNET')
