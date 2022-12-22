# -*- coding:utf-8 -*-
import os
from typing import List, Dict

from slither import Slither
from sqlalchemy.orm import sessionmaker

from common.decorator import format_address
from detectors.all_detectors import ALL_DETECTORS
from common.dataset import get_or_add_contract
from .downloader import SourceCodeDownloader


class StaticAnalysisBuilder(SourceCodeDownloader):

    def _build_slither(self, contract_address: str) -> (Slither, bool):
        self.download_and_compile(contract_address)

        with sessionmaker(self.engine)() as session:
            contract = get_or_add_contract(session, self.network, contract_address)
            if contract.is_proxy and contract.proxy_address:
                contract_address = contract.proxy_address

        compile_json_file = os.path.join(self.compile_output_dir, contract_address + "_export.json")
        if os.path.exists(compile_json_file):
            return Slither(target=compile_json_file)

    @format_address
    def run(self, contract_address: str) -> List[Dict]:
        _slither = self._build_slither(contract_address)
        if _slither:
            for detector in ALL_DETECTORS:
                _slither.register_detector(detector)
            return _slither.run_detectors()
