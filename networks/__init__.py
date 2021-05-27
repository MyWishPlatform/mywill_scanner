from .eth import EthMaker
from .tron import TronMaker
from .xin import XinMaker

scanner_makers = {
    'EthMaker': EthMaker,
    'TronMaker': TronMaker,
    'XinMaker': XinMaker,
}
