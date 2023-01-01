# -*- coding:utf-8 -*-
import logging
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

import click
from sqlalchemy.orm import sessionmaker

from common.config import load_config
from common.dataset import init_database, get_all_new_contracts
from common.enums import get_network_by_key
from source.downloader import SourceCodeDownloader
from source.static_analysis import StaticAnalysisBuilder


@click.group()
@click.pass_context
def entrypoint(cls):
    pass


@click.command(context_settings=dict(help_option_names=['-h', '--help']), help='download and compile source code')
@click.option('-n', '--network', required=True, type=str, help='network. eg:eth、bsc、avax')
@click.option('-a', '--address', required=True, type=str, help='contract address')
def download_sourcecode(network: str, address: str):
    global_config = load_config()
    downloader = SourceCodeDownloader(global_config, network=get_network_by_key(network),
                                      engine=init_database(global_config))
    downloader.download_and_compile(address)


@click.command(context_settings=dict(help_option_names=['-h', '--help']), help='batch download and compile source code')
@click.option('-n', '--network', required=True, type=str, help='network. eg:eth、bsc、avax')
def batch_download_source_code(network: str):
    global_config = load_config()
    engine = init_database(global_config)
    api_keys = global_config.chains.get(network).etherscan_api_key.split(',')

    api_keys_length = len(api_keys)
    pools = []
    for i in range(api_keys_length):
        pools.append(ThreadPoolExecutor(max_workers=2))

    downloader = SourceCodeDownloader(global_config, network=get_network_by_key(network),
                                      engine=init_database(global_config))
    tasks = []
    with sessionmaker(engine)() as session:
        contracts = list(get_all_new_contracts(session, get_network_by_key(network)))
        logging.info(f"{len(contracts)} contracts to download.")
        for idx, contract in enumerate(contracts):
            pool_idx = idx % api_keys_length
            tasks.append(pools[pool_idx].submit(downloader.download_and_compile, contract.address,
                                                downloader.api_keys[pool_idx]))
    wait(tasks, return_when=ALL_COMPLETED)


@click.command(context_settings=dict(help_option_names=['-h', '--help']), help='run static analysis')
@click.option('-n', '--network', required=True, type=str, help='network. eg:eth、bsc、avax')
@click.option('-a', '--address', required=True, type=str, help='contract address')
def static_analysis(network: str, address: str):
    global_config = load_config()
    analyser = StaticAnalysisBuilder(global_config=global_config, network=get_network_by_key(network),
                                     engine=init_database(global_config))
    results = analyser.run(address)
    logging.info(f'found {sum([len(x) for x in results])} results')


entrypoint.add_command(download_sourcecode, "download")
entrypoint.add_command(batch_download_source_code, "batch_download")
entrypoint.add_command(static_analysis, "scan")


def main():
    logging.basicConfig(format='%(asctime)s: t-%(thread)d: %(levelname)s: %(message)s')
    logging.getLogger().setLevel(logging.INFO)
    entrypoint()


if __name__ == '__main__':
    entrypoint()
