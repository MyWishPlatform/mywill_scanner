import os
import sys
import time
import datetime as dt
import traceback
import typing
from threading import Lock, Thread

from base.network import Network


ScannerT = typing.TypeVar("Scanner")


class Block:
    def __init__(self, id: int, datetime: dt.datetime = None):
        self.id = id
        self.datetime = datetime if datetime else dt.datetime.now()


class ScannerManager:
    MAX_STACK_SIZE = 1000

    class StackGarbageCollector:
        _ALIVE = True

        @classmethod
        def run(cls):
            StackGarbageCollectorTH = Thread(target=cls._run,
                                             name="StackGarbageCollectorThread")
            StackGarbageCollectorTH.start()

        @staticmethod
        def _run() -> None:
            time.sleep(60 * 2)
            while ScannerManager.StackGarbageCollector._ALIVE:
                ScannerManager.check_and_clear()
                time.sleep(5)

    class Stack:
        def __init__(self, name: str):
            self.lock = Lock()
            self.name = name
            # слева самые старые по времени блоки, справа самые молодые
            self.stack = []
            self.scanner: Scanner = None

        def add_block(self, block: Block):
            self.lock.acquire()
            self.stack.append(block)
            self.stack.sort(key=lambda b: b.datetime)
            self.lock.release()

    stacks: typing.List[Stack] = []
    StackGarbageCollector.run()

    @staticmethod
    def get_network_speed(network_name):
        try:
            stack = list(filter(lambda stack: stack.name == network_name, ScannerManager.stacks))[0]

            stack.lock.acquire()
            first_block: Block = stack.stack[0]
            last_block: Block = stack.stack[-1]

            try:
                blocks_per_last_minute = len(stack.stack) / ((last_block.datetime - first_block.datetime).seconds / 60)
            except ZeroDivisionError:
                return 0

            stack.lock.release()
            return blocks_per_last_minute

        except IndexError:
            raise KeyError("Such network doesn't registered in StackManager")

    @staticmethod
    def add_scanner(scanner: ScannerT) -> Stack:
        new_stack = ScannerManager.Stack(name=scanner.network.type)
        ScannerManager.stacks.append(new_stack)
        new_stack.scanner = scanner
        return new_stack

    @staticmethod
    def check_and_clear():
        """
        позволяет удалять ненужные блоки, дабы не засорять память
        """
        for stack in ScannerManager.stacks:
            stack.lock.acquire()
            print("check_and_clear acquired lock")

            if not stack.stack:
                continue

            else:
                select_from: int = len(stack.stack) - 1 - ScannerManager.MAX_STACK_SIZE
                select_from = select_from if select_from >= 0 else 0
                stack.stack = stack.stack[select_from: -1]

            stack.lock.release()


class LastBlockPersister:
    # TODO move into database
    base_dir = 'block_numbers'

    def __init__(self, network: Network):
        self.network_name: str = network.type
        os.makedirs(self.base_dir, exist_ok=True)

    def get_last_block(self) -> int:
        try:
            with open(os.path.join(self.base_dir, self.network_name), 'r') as file:
                last_block_number = file.read()
        except FileNotFoundError:
            return 1
        return int(last_block_number)

    def save_last_block(self, last_block_number: int):
        with open(os.path.join(self.base_dir, self.network_name), 'w') as file:
            file.write(str(last_block_number))


class Scanner:
    INFO_INTERVAL = 60000
    WARN_INTERVAL = 120000

    def __init__(self, network: Network, last_block_persister: LastBlockPersister, polling_interval: int,
                 commitment_chain_length: int, reach_interval: int = 0):

        self.network = network
        self.last_block_persister = last_block_persister
        self.polling_interval = polling_interval
        self.commitment_chain_length = commitment_chain_length
        self.reach_interval = reach_interval

        self.stack = ScannerManager.add_scanner(self)

    def process_block(self, block):
        raise NotImplementedError("WARNING: Function process_block must be overridden.")

    def poller(self):
        self.last_block_time = time.time()
        self.next_block_number = self.last_block_persister.get_last_block()
        print('hello from {}'.format(self.network.type), flush=True)
        while True:
            self.polling()

    def polling(self):
        try:
            self.last_block_number = self.network.get_last_block()

            new_block = Block(id=self.last_block_number)
            self.stack.add_block(new_block)

            if self.last_block_number - self.next_block_number > self.commitment_chain_length:
                print('{}: Process next block {}/{} immediately.'.format(self.network.type, self.next_block_number,
                                                                         self.last_block_number), flush=True)
                self.load_next_block()
                time.sleep(self.reach_interval)
                return

            time_interval = self.last_block_time - time.time()
            if time_interval > self.WARN_INTERVAL:
                print('{}: there is no block from {} seconds!'.format(self.network.type, time_interval))
            elif time_interval > self.INFO_INTERVAL:
                print('{}: there is no block from {} seconds.'.format(self.network.type, time_interval), flush=True)

            # pending transactions logic

            print('{}: all blocks processed, wait new one.'.format(self.network.type))
        except Exception:
            print('{}: exception handled in polling cycle. Continue.'.format(self.network.type))
            print('\n'.join(traceback.format_exception(*sys.exc_info())), flush=True)

        time.sleep(self.polling_interval)

    def load_next_block(self):
        block = self.network.get_block(self.next_block_number)

        self.last_block_persister.save_last_block(self.next_block_number)
        self.next_block_number += 1
        self.last_block_time = time.time()

        self.process_block(block)

    def open(self):
        pass

    def close(self):
        pass
