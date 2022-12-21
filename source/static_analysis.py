# -*- coding:utf-8 -*-
import logging
import os
from typing import List, Dict

from crytic_compile import CryticCompile, InvalidCompilation
from slither import Slither

from common.config import GlobalConfig
from common.enums import Networks
from common.etherscan_api import get_proxy_addr

from detectors.all_detectors import ALL_DETECTORS


class StaticAnalysisBuilder:
    def __init__(self, global_config: GlobalConfig, network: Networks):
        self.global_config = global_config
        self.network = network
        self.api_key = self.global_config.chains.get(network.value).etherscan_api_key
        self.compile_output_dir = os.path.join(global_config.storage_path, network.value)

    def _build_slither(self, contract_address: str, proxy=False) -> (Slither, bool):
        compile_json_file = os.path.join(self.compile_output_dir, contract_address + "_export.json")
        if not os.path.exists(compile_json_file):
            proxy_address = get_proxy_addr(network=self.network, contract=contract_address, api_key=self.api_key)
            if proxy_address:
                return self._build_slither(proxy_address, proxy=True)

            # compile contract and export standard json file
            kwargs = {"export_dir": self.compile_output_dir, "export_format": "standard", "solc_disable_warnings": True}
            if self.network == Networks.ETHEREUM:
                kwargs["etherscan_api_key"] = self.api_key
            elif self.network == Networks.BSC.value:
                kwargs["bscscan_api_key"] = self.api_key
            # compile
            try:
                compilation = CryticCompile(target=contract_address, **kwargs)
                if compilation.bytecode_only:
                    logging.info(f"no source code for contract:{contract_address}")
                    return None, proxy
            except InvalidCompilation as e:
                logging.warning(f"compile failed with error: {str(e)}")
                return None, proxy

            export_files = compilation.export(**kwargs)
            # rename filename endswith _export.json for falcon to analysis
            assert len(export_files) == 1
            origin_export_file = export_files[0]
            os.rename(origin_export_file, compile_json_file)

        return Slither(target=compile_json_file), proxy

    def run(self, contract_address: str) -> List[Dict]:
        _slither, proxy = self._build_slither(contract_address)
        for detector in ALL_DETECTORS:
            _slither.register_detector(detector)
        return _slither.run_detectors()
