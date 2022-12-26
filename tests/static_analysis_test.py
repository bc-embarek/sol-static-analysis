# -*- coding:utf-8 -*-
import logging
import traceback
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

    def test_all_bsc_contract(self):
        logging.basicConfig(format='%(asctime)s: t-%(thread)d: %(levelname)s: %(message)s')
        logging.getLogger().setLevel(logging.INFO)
        with sessionmaker(self.engine)() as session:
            static_analysis = StaticAnalysisBuilder(global_config=self.global_config, network=Networks.BSC,
                                                    engine=self.engine)
            compiled_contracts = get_all_compiled_contracts(session, Networks.BSC)
            for idx, contract in enumerate(compiled_contracts):
                try:
                    results = static_analysis.run(contract.address)
                    if len(results[0]) > 0:
                        logging.warning(f'vulnerability found in contract:{contract.address}')
                    else:
                        logging.info(f'{idx}/{len(compiled_contracts)}')
                except:
                    logging.warning(traceback.format_exc())
