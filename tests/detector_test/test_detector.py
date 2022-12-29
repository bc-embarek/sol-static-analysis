# -*- coding:utf-8 -*-
import logging
import os
from unittest import TestCase

from slither.slither import Slither

from detectors.contract_balance import BalanceUsage


class DetectorTest(TestCase):

    def setUp(self) -> None:
        logging.basicConfig(format='%(asctime)s: t-%(thread)d: %(levelname)s: %(message)s')
        logging.getLogger().setLevel(logging.INFO)
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

    @staticmethod
    def solc_version(version):
        env = dict(os.environ)
        env["SOLC_VERSION"] = version
        os.environ.clear()
        os.environ.update(env)

    def test_contract_balance(self):
        self.solc_version('0.8.0')
        slither = Slither('testcases/ContractBalanceTest.sol')
        slither.register_detector(BalanceUsage)
        slither.run_detectors()
