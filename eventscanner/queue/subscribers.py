from pubsub import pub

from eventscanner.monitors.payments import MatPaymentMonitor, ERC20PaymentMonitor
from eventscanner.monitors.contract.deploy import DeployMonitor
from eventscanner.monitors.contract.ownership_transferred import OwnershipMonitor
from eventscanner.monitors.contract.initialized import InitializedMonitor


pub.subscribe(MatPaymentMonitor.on_new_block_event, 'MATIC_MAINNET')
pub.subscribe(ERC20PaymentMonitor.on_new_block_event, 'MATIC_MAINNET')
pub.subscribe(DeployMonitor.on_new_block_event, 'MATIC_MAINNET')
pub.subscribe(OwnershipMonitor.on_new_block_event, 'MATIC_MAINNET')
pub.subscribe(InitializedMonitor.on_new_block_event, 'MATIC_MAINNET')


pub.subscribe(MatPaymentMonitor.on_new_block_event, 'MATIC_TESTNET')
pub.subscribe(ERC20PaymentMonitor.on_new_block_event, 'MATIC_TESTNET')
pub.subscribe(DeployMonitor.on_new_block_event, 'MATIC_TESTNET')
pub.subscribe(OwnershipMonitor.on_new_block_event, 'MATIC_TESTNET')
pub.subscribe(InitializedMonitor.on_new_block_event, 'MATIC_TESTNET')

