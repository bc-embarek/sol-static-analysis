# -*- coding:utf-8 -*-
import logging
from unittest import TestCase
from common.config import load_config
from common.dataset import init_database
from common.enums import Networks
from source.static_analysis import StaticAnalysisBuilder


class StaticAnalysisTest(TestCase):
    def setUp(self) -> None:
        logging.basicConfig(format='%(message)s')
        logging.getLogger().setLevel(logging.INFO)

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
        results = static_analysis.run('0x3A5Ddb3E5C0D9ee587eb8FB865432893B2A92099')
        self.assertTrue(len(results[0]) <= 0)
