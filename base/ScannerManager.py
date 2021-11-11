import typing
import datetime as dt
import time

from threading import Lock, Thread

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
            self.scanner = None

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

            if not stack.stack:
                continue

            else:
                select_from: int = len(stack.stack) - 1 - ScannerManager.MAX_STACK_SIZE
                select_from = select_from if select_from >= 0 else 0
                stack.stack = stack.stack[select_from: -1]

            stack.lock.release()
