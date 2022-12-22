# -*- coding:utf-8 -*-
import logging
from unittest import TestCase

from sqlalchemy.orm import sessionmaker

from common.config import load_config
from common.dataset import init_database, get_all_new_contracts
from common.enums import Networks
from source.downloader import SourceCodeDownloader


class SourceCodeDownloaderTest(TestCase):

    def setUp(self) -> None:
        logging.basicConfig(format='%(message)s')
        logging.getLogger().setLevel(logging.INFO)
        global_config = load_config('config-example.json')
        self.network = Networks.BSC
        self.engine = init_database(global_config)
        self.downloader = SourceCodeDownloader(global_config, network=self.network, engine=self.engine)

    def test_download_source(self):
        self.downloader.download_and_compile('0xbCB79CF3fE7a17024257c19056a1225a5701A7aB')

    def test_download_all_contract_source(self):
        with sessionmaker(self.engine)() as session:
            for contract in get_all_new_contracts(session, self.network):
                self.downloader.download_and_compile(contract.address)
            pass
