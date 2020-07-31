import os

import yaml

config = {}


def from_file(file_obj):
    config.update(yaml.load(file_obj))


if not config:
    from_file(open(os.environ['CONFIG']))
