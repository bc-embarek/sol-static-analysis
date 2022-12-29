# -*- coding:utf-8 -*-
from typing import List

from slither.core.declarations import Function, FunctionContract
from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.slithir.operations import SolidityCall
from slither.utils.output import Output

from detectors.utils import has_msg_sender_check


class PublicMintDetector(AbstractDetector):
    ARGUMENT = "public-mint"

    HELP = ' '
    IMPACT = DetectorClassification.MEDIUM
    CONFIDENCE = DetectorClassification.MEDIUM

    WIKI = 'check public mint method'
    WIKI_TITLE = WIKI
    WIKI_DESCRIPTION = WIKI_TITLE
    WIKI_RECOMMENDATION = WIKI_TITLE
    WIKI_EXPLOIT_SCENARIO = WIKI_TITLE

    @staticmethod
    def _get_require_nodes(func: Function):
        require_nodes = []
        for node in func.nodes:
            for ir in node.irs:
                if isinstance(ir, SolidityCall) and ir.function.name == 'require(bool,string)':
                    require_nodes.append(node)
                    break
        return require_nodes

    def _detect(self) -> List[Output]:
        results = []
        for contract in self.contracts:
            if contract.is_interface:
                continue

            for func in contract.functions:
                if func.is_constructor or func.is_fallback or func.is_receive:
                    continue

                if func.name == 'mint' and func.entry_point is not None and func.visibility in ['external', 'public']:
                    functions_to_check = [func]
                    for x in func.internal_calls:
                        if isinstance(x, FunctionContract):
                            functions_to_check.append(x)
                    if not any([has_msg_sender_check(f) for f in functions_to_check]):
                        results.append(self.generate_result(['public mint found in ', func]))
        return results
