# -*- coding:utf-8 -*-
import logging
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from unittest import TestCase

from sqlalchemy.orm import sessionmaker

from common.config import load_config
from common.dataset import init_database, get_all_compiled_contracts
from common.enums import Networks
from source.static_analysis import StaticAnalysisBuilder


class StaticAnalysisTest(TestCase):
    def setUp(self) -> None:
        self.global_config = load_config('config-example.json')
        self.engine = init_database(self.global_config)

    def test_eth(self):
        static_analysis = StaticAnalysisBuilder(global_config=self.global_config, network=Networks.ETHEREUM,
                                                engine=self.engine)
        results = static_analysis.run('0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48')
        self.assertTrue(len(results[0]) <= 0)

    def test_bsc(self):
        static_analysis = StaticAnalysisBuilder(global_config=self.global_config, network=Networks.BSC,
                                                engine=self.engine)
        results = static_analysis.run('0x002e662ed331bd17aaa7051fbd65b33428c71832')
        self.assertTrue(len(results[0]) <= 0)

    def test_avax(self):
        static_analysis = StaticAnalysisBuilder(global_config=self.global_config, network=Networks.AVAX,
                                                engine=self.engine)
        results = static_analysis.run('0x3531ed4cb9F8B68e0C706C92aF5B8a50e095f293')
        self.assertTrue(len(results[0]) <= 0)

    def test_all_contract(self):
        logging.basicConfig(format='%(asctime)s: t-%(thread)d: %(levelname)s: %(message)s')
        logging.getLogger().setLevel(logging.INFO)

        thread_count = 5
        network = Networks.AVAX

        def detect(_contract, _idx, _total_contracts):
            try:
                results = static_analysis.run(_contract.address)
                if any([len(x) > 0 for x in results]):
                    logging.warning(f'vulnerability found in contract:{_contract.address}')
                else:
                    logging.info(f'{_idx}/{_total_contracts}')
            except Exception as e:
                logging.warning(e)

        with sessionmaker(self.engine)() as session:
            static_analysis = StaticAnalysisBuilder(global_config=self.global_config, network=network,
                                                    engine=self.engine)
            compiled_contracts = get_all_compiled_contracts(session, network)
            total_contracts = len(compiled_contracts)
            pool = ThreadPoolExecutor(max_workers=thread_count)
            tasks = []
            for idx, contract in enumerate(compiled_contracts):
                tasks.append(pool.submit(detect, contract, idx, total_contracts))
            wait(tasks, return_when=ALL_COMPLETED)
