# -*- coding:utf-8 -*-
from unittest import TestCase
from common.config import load_config
from common.enums import Networks
from source.static_analysis import StaticAnalysisBuilder


class StaticAnalysisTest(TestCase):
    def setUp(self) -> None:
        global_config = load_config('config-example.json')
        self.static_analysis = StaticAnalysisBuilder(global_config=global_config, network=Networks.ETHEREUM)

    def test_run_slither(self):
        results = self.static_analysis.run('0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48')
        self.assertTrue(len(results[0]) <= 0)
