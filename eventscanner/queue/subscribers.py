from pubsub import pub

from eventscanner.monitors.payments import EthPaymentMonitor, ERC20PaymentMonitor
from eventscanner.monitors.lock import AddressLockMonitor

pub.subscribe(EthPaymentMonitor.on_new_block_event, 'ETHEREUM_MAINNET')
pub.subscribe(ERC20PaymentMonitor.on_new_block_event, 'ETHEREUM_MAINNET')
pub.subscribe(AddressLockMonitor.on_new_block_event, 'ETHEREUM_MAINNET')
