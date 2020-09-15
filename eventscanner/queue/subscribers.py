from pubsub import pub

from eventscanner.monitors.payments import ERC20PaymentMonitor
from eventscanner.monitors import transfer


pub.subscribe(ERC20PaymentMonitor.on_new_block_event, 'ETHEREUM_MAINNET')
pub.subscribe(transfer.QurasTransferMonitor.on_new_block_event, 'QURAS_MAINNET')
