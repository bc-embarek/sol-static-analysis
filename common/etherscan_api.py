# -*- coding:utf-8 -*-
import json

import requests

from .enums import Networks


def get_proxy_addr(network: Networks, contract: str, api_key: str):
    if network == Networks.ETHEREUM:
        base_url = 'https://api.etherscan.io/api'
    elif network == Networks.BSC:
        base_url = 'https://api.bscscan.com/api'
    else:
        raise ValueError(f"Unsupported network: {network}")

    url = f'{base_url}?module=contract&' \
          f'action=getsourcecode&address={contract}&' \
          f'apikey={api_key}'
    resp = requests.get(url)
    res = json.loads(resp.content)
    try:
        proxy_addr = res.get('result')[0].get('Implementation')
        return proxy_addr
    except:
        return None
