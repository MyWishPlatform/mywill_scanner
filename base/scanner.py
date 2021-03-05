import os
import sys
import time
import traceback

from base.network import Network


class LastBlockPersister:
    # TODO move into database
    base_dir = 'settings'

    def __init__(self, network: Network):
        self.network_name: str = network.type

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
        except Exception as e:
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
