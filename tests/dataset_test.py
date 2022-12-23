# -*- coding:utf-8 -*-
from unittest import TestCase

from sqlalchemy.orm import sessionmaker

from common.config import load_config
from common.enums import Networks
from common.dataset import init_database, get_or_add_contract, get_all_compiled_contracts


class DatasetTest(TestCase):

    def setUp(self) -> None:
        global_config = load_config("config-example.json")
        self.engine = init_database(global_config)

    def testAddContracts(self):
        with sessionmaker(self.engine)() as session:
            try:
                contract = get_or_add_contract(session, Networks.ETHEREUM, '0xa87a8764aa96B2Cab167363eC28C260c10790414')
                self.assertIsNotNone(contract)
            finally:
                session.commit()

    def testGetAllCompiledContract(self):
        with sessionmaker(self.engine)() as session:
            contracts = get_all_compiled_contracts(session, Networks.BSC)
            self.assertTrue(len(contracts) >= 0)

    def testAddContractsFromFile(self):
        with open('../bsc-pancake-swap-tokens.txt', 'r') as f:
            line = f.readline()
            while line:
                with sessionmaker(self.engine)() as session:
                    get_or_add_contract(session=session, network=Networks.BSC, contract_address=line.strip())
                    session.commit()
                line = f.readline()
