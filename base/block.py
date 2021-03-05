import typing

from base.transaction import Transaction


class Block:
    def __init__(self, hash: str, number: int, timestamp: int, transactions: typing.List[Transaction]):
        self.hash = hash
        self.number = number
        self.timestamp = timestamp
        self.transactions = transactions
