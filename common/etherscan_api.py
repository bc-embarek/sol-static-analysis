# -*- coding:utf-8 -*-
import json

import requests
from bs4 import BeautifulSoup

from .enums import Networks


def get_proxy_addr(network: Networks, contract: str, api_key: str):
    if network == Networks.ETHEREUM:
        base_url = 'https://api.etherscan.io/api'
    elif network == Networks.BSC:
        base_url = 'https://api.bscscan.com/api'
    elif network == Networks.AVAX:
        base_url = 'https://api.snowtrace.io/api'
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


def _get_page_contracts(base_url, page_no=1):
    url = f'{base_url}contractsVerified/{page_no}?ps=100'
    res = requests.get(url, headers={
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'})
    soup = BeautifulSoup(res.content)
    return [x['title'] for x in soup.find_all('tbody')[0].find_all('a')]


def get_new_verified_contracts(network: Networks):
    if network == Networks.ETHEREUM:
        base_url = 'https://etherscan.io/'
    elif network == Networks.BSC:
        base_url = 'https://bscscan.com/'
    elif network == Networks.AVAX:
        base_url = 'https://snowtrace.io/'
    else:
        raise ValueError(f"unsupported network:{network}")
    contracts = []
    for i in range(1, 6):
        contracts.extend(_get_page_contracts(base_url=base_url, page_no=i))
    return list(set(contracts))
