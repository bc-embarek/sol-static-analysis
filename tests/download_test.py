# -*- coding:utf-8 -*-
import logging
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from unittest import TestCase

from sqlalchemy.orm import sessionmaker

from common.config import load_config
from common.dataset import init_database, get_all_new_contracts
from common.enums import Networks
from source.downloader import SourceCodeDownloader


class SourceCodeDownloaderTest(TestCase):

    def setUp(self) -> None:
        logging.basicConfig(format='%(asctime)s: t-%(thread)d: %(levelname)s: %(message)s')
        logging.getLogger().setLevel(logging.INFO)
        global_config = load_config('config-example.json')
        self.network = Networks.AVAX
        self.engine = init_database(global_config)
        self.downloader = SourceCodeDownloader(global_config, network=self.network, engine=self.engine)

    def test_download_source(self):
        self.downloader.download_and_compile('0x251573b60b2976fA263bAB01D687594eF92B0291')

    def test_download_all_contract_source(self):
        api_keys_length = len(self.downloader.api_keys)
        pools = []
        for i in range(api_keys_length):
            pools.append(ThreadPoolExecutor(max_workers=5))

        tasks = []
        with sessionmaker(self.engine)() as session:
            for idx, contract in enumerate(get_all_new_contracts(session, self.network)):
                pool_idx = idx % api_keys_length
                tasks.append(pools[pool_idx].submit(self.downloader.download_and_compile, contract.address,
                                                    self.downloader.api_keys[pool_idx]))

        wait(tasks, return_when=ALL_COMPLETED)
