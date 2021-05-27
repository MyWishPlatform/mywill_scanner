import requests
import http.client

class XinFinApi:



    def __init__(self):
        self.set_base_url()

    def set_base_url(self):
        self.base_url = f'https://rpc.xinfin.network'

    def get_block_by_number(self):
        conn = http.client.HTTPSConnection('https://rpc.xinfin.network')
        payload = "{\"jsonrpc\":\"2.0\",\"method\":\"eth_getBlockByNumber\",\"params\":[\"0x0\",true],\"id\":1}"
        headers = {'content-type': "application/json"}
        res = conn.request("POST", "//getBlockByNumber", payload, headers)
