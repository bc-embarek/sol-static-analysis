# -*- coding:utf-8 -*-
import logging

import click

from .config import load_config
from .dataset import init_database
from .enums import get_network_by_key
from source.downloader import SourceCodeDownloader


@click.group()
@click.pass_context
def entrypoint(cls):
    pass


@click.command(context_settings=dict(help_option_names=['-h', '--help']), help='download and compile source code')
@click.option('-n', '--network', required=True, type=str, help='network. eg:eth、bsc、avax')
@click.option('-a', '--address', required=True, type=str, help='contract address')
def sourcecode_downloader(network: str, address: str):
    global_config = load_config()
    downloader = SourceCodeDownloader(global_config, network=get_network_by_key(network),
                                      engine=init_database(global_config))
    downloader.download_and_compile(address)


entrypoint.add_command(sourcecode_downloader, "download")


def main():
    logging.basicConfig(format='%(message)s')
    logging.getLogger().setLevel(logging.INFO)
    entrypoint()
