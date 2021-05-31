import typing

from base import Block, Transaction


class XinBlock:
    def __init__(self, number: int, transactions: typing.List[Transaction]):
        self.number = number
        self.transactions = transactions
