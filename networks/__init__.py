from .eth import EthMaker
from .tron import TronMaker

scanner_makers = {
    'EthMaker': EthMaker,
    'TronMaker': TronMaker,
}
