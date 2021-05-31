import typing

from base import Block, Transaction


class XinBlock:
    def __init__(self, result: int, transactions: typing.List[Transaction]):
        self.result = result
        self.transactions = transactions
