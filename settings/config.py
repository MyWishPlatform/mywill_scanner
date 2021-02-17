import os

import yaml

CONFIG = {}


def from_file(file_obj):
    CONFIG.update(yaml.load(file_obj, Loader=yaml.FullLoader))


if not CONFIG:
    from_file(open(os.environ['CONFIG']))
