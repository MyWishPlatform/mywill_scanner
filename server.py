import requests
import uvicorn as uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict

from base.scanner import ScannerManager
from settings import CONFIG

class Response(BaseModel):
    prices: Dict[str, float]


app = FastAPI()


# response_model=Response
@app.get('/', description='')
async def log_networks():
    print("test")
    response = {}
    for stack in ScannerManager.stacks:
        speed = ScannerManager.get_network_speed(stack.name)
        response.update({stack.name: speed,
                         "last_block_time": stack.scanner.last_block_time,
                         "last_block_id": stack.scanner.network.get_last_block(),
                         })

    return response


def run_server():
    log_config = uvicorn.config.LOGGING_CONFIG
    uvicorn.run("server:app", host=CONFIG["server"]["ip"], port=CONFIG["server"]["port"], log_level="info")

