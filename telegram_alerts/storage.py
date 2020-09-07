import os


filename = 'tg_ids'

if not os.path.exists(filename):
    open(filename, 'a').close()


def get_saved_chat_ids():
    with open(filename, 'r+') as f:
        content = f.read()

        return [int(i) for i in content.split(';')] if content else []


def write_new_chat_ids(ids):
    with open(filename, 'w+') as f:
        f.write(';'.join((str(i) for i in ids)))
