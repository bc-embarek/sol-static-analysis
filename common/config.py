# -*- coding:utf-8 -*-

import json
import os.path
import pathlib
from typing import Dict
from pathlib import Path


class Chain:
    def __init__(self, key, etherscan_api_url: str, etherscan_api_key: str):
        self.key = key
        self.etherscan_api_url = etherscan_api_url
        self.etherscan_api_key = etherscan_api_key


class GlobalConfig:
    def __init__(self, storage_path: str, chains: Dict[str, Chain]):
        self.storage_path = storage_path
        if not os.path.exists(storage_path):
            os.makedirs(storage_path, exist_ok=True)
        self.chains = chains


def load_config(config_filepath) -> GlobalConfig:
    if not config_filepath:
        config_filepath = os.path.join(Path.home(), ".ssa-config.json")
    if not os.path.exists(config_filepath):
        raise ValueError(f"global_config file does not exists. {config_filepath}")
    with open(config_filepath, 'r') as f:
        config_json = json.loads(f.read())
        storage_path = config_json.get('storage_base_path', os.path.join(Path.home(), ".ssa-data"))
        chains = {}
        for chain in config_json.get('chains'):
            key = chain.get('key')
            chains[key] = Chain(**chain)
        return GlobalConfig(storage_path=storage_path, chains=chains)
