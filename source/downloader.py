# -*- coding:utf-8 -*-
import logging
import os
from datetime import datetime

from crytic_compile import CryticCompile, InvalidCompilation
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from common.config import GlobalConfig
from common.dataset import get_or_add_contract
from common.decorator import format_address
from common.enums import Networks
from common.etherscan_api import get_proxy_addr


class SourceCodeDownloader:
    def __init__(self, global_config: GlobalConfig, network: Networks, engine: Engine):
        self.global_config = global_config
        self.network = network
        self.api_keys = self.global_config.chains.get(network.value).etherscan_api_key.split(',')
        self.compile_output_dir = os.path.join(global_config.storage_path, network.value)
        self.engine = engine

    @format_address
    def download_and_compile(self, contract_address, api_key=None):
        if not api_key:
            api_key = self.api_keys[0]
        with sessionmaker(self.engine)() as session:
            try:
                contract = get_or_add_contract(session=session, network=self.network, contract_address=contract_address)
                if contract.has_source_code is not None and not contract.has_source_code:
                    logging.warning(f"contract:{self.network.value}-{contract_address} has no source code, "
                                    f"last check time: {contract.last_check_time}")
                    return
                elif contract.is_proxy and contract.proxy_address:
                    return self.download_and_compile(contract.proxy_address)
                compile_json_file = os.path.join(self.compile_output_dir, contract_address + "_export.json")
                if not os.path.exists(compile_json_file):
                    proxy_address = get_proxy_addr(network=self.network, contract=contract_address, api_key=api_key)
                    contract.last_check_time = datetime.now()
                    if proxy_address:
                        contract.is_proxy = True
                        contract.proxy_address = proxy_address.lower()
                        session.commit()
                        return self.download_and_compile(proxy_address)
                    else:
                        contract.is_proxy = False
                        # compile contract and export standard json file
                        kwargs = {"export_dir": self.compile_output_dir, "export_format": "standard",
                                  "solc_disable_warnings": True}
                        compile_target = contract_address
                        if self.network == Networks.ETHEREUM:
                            kwargs["etherscan_api_key"] = api_key
                            compile_target = f'mainet:{compile_target}'
                        elif self.network == Networks.BSC:
                            kwargs["bscan_api_key"] = api_key
                            compile_target = f'bsc:{compile_target}'
                        elif self.network == Networks.AVAX:
                            kwargs["avax_api_key"] = api_key
                            compile_target = f'avax:{compile_target}'
                        # compile
                        try:
                            compilation = CryticCompile(target=compile_target, **kwargs)
                            if compilation.bytecode_only:
                                logging.warning(f"no source code for contract:{contract_address}")
                                contract.has_source_code = False
                            else:
                                contract.has_source_code = True
                                contract.compile_success = True
                                export_files = compilation.export(**kwargs)

                                # rename filename endswith _export.json for falcon to analysis
                                assert len(export_files) == 1
                                origin_export_file = export_files[0]
                                os.rename(origin_export_file, compile_json_file)
                        except InvalidCompilation as e:
                            logging.warning(f"compile failed with error: {str(e)}")
                            contract.has_source_code = True
                            contract.compile_success = False

                sourcecode_base_dir = os.path.join(self.compile_output_dir, 'etherscan-contracts')
                sourcecode_locations = [x for x in os.listdir(sourcecode_base_dir) if
                                        x.startswith(contract_address.lower())]
                logging.info(f'Location: {os.path.join(sourcecode_base_dir, sourcecode_locations[0])}')
            finally:
                session.commit()
