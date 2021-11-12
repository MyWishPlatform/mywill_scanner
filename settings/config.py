import json
import pathlib
import os
from dotenv import load_dotenv

import yaml

env_path = pathlib.Path.cwd() / "secret" / ".env"
print(f"is .env exist on path {env_path.as_posix()} ? ", env_path.exists())
load_dotenv(dotenv_path=env_path.as_posix())

CONFIG = {}


def from_file(file_obj):
    CONFIG.update(yaml.load(file_obj, Loader=yaml.FullLoader))


if not CONFIG:
    print("trying to load config...")
    print(f"config path is {os.getenv('CONFIG')}")
    from_file(open(os.getenv("CONFIG")))
    conf = json.dumps(CONFIG).replace(',', ',\n')
    print(f"config:\n{conf}")
