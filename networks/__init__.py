from .eth import EthMaker
from .tron import TronMaker
from .xin import XinMaker
from .btc import BTCMaker

scanner_makers = {
    'EthMaker': EthMaker,
    'TronMaker': TronMaker,
    'XinMaker': XinMaker,
    'BTCMaker': BTCMaker,
}
