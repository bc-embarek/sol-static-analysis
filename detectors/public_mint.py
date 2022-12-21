# -*- coding:utf-8 -*-
from typing import List

from slither.core.declarations import Function, SolidityVariableComposed
from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.slithir.operations import SolidityCall
from slither.utils.output import Output


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

                if func.name == 'mint':
                    require_nodes = []
                    for modifier in func.modifiers:
                        require_nodes.extend(self._get_require_nodes(modifier))
                    require_nodes.extend(self._get_require_nodes(func))

                    has_msg_sender_check = False
                    for require_node in require_nodes:
                        has_msg_sender_check |= any(
                            [isinstance(x, SolidityVariableComposed) and x.name == 'msg.sender' for x in
                             require_node.variables_read])
                    if not has_msg_sender_check:
                        results.append(self.generate_result(['public mint found in ', func]))

        return results
