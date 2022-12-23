# -*- coding:utf-8 -*-
from typing import List

from slither.core.declarations import Function, SolidityVariableComposed, FunctionContract
from slither.core.expressions import CallExpression
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

    def _get_function_variables_read_recursively(self, func: FunctionContract):
        variables_read = func.variables_read
        if len(func.calls_as_expressions) > 0:
            for call in func.calls_as_expressions:
                if isinstance(call, CallExpression) and \
                        call.called and hasattr(call.called, 'value') and \
                        isinstance(call.called.value, FunctionContract):
                    variables_read.extend(self._get_function_variables_read_recursively(call.called.value))
        return variables_read

    def _has_msg_sender_check(self, func: FunctionContract):
        for modifier in func.modifiers:
            for var in self._get_function_variables_read_recursively(modifier):
                if isinstance(var, SolidityVariableComposed) and var.name == 'msg.sender':
                    return True
        for var in self._get_function_variables_read_recursively(func):
            if isinstance(var, SolidityVariableComposed) and var.name == 'msg.sender':
                return True
        return False

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

                if func.name == 'mint' and func.entry_point is not None:
                    functions_to_check = [func]
                    for x in func.internal_calls:
                        if isinstance(x, FunctionContract):
                            functions_to_check.append(x)
                    if not any([self._has_msg_sender_check(f) for f in functions_to_check]):
                        results.append(self.generate_result(['public mint found in ', func]))
        return results
