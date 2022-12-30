# -*- coding:utf-8 -*-

from enum import Enum


class Networks(Enum):
    ETHEREUM = "eth"
    BSC = "bsc"
    POLYGON = "polygon"
    FANTOM = "fantom"
    AVAX = "avax"


def get_network_by_key(key: str):
    if key == Networks.ETHEREUM.value:
        return Networks.ETHEREUM
    elif key == Networks.BSC.value:
        return Networks.BSC
    elif key == Networks.POLYGON.value:
        return Networks.POLYGON
    elif key == Networks.FANTOM.value:
        return Networks.FANTOM
    elif key == Networks.AVAX.value:
        return Networks.AVAX
    else:
        raise ValueError(f"unknown network: {key}")
