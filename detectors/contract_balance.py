# -*- coding:utf-8 -*-
from typing import List

from slither.core.declarations import FunctionContract, SolidityFunction
from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.utils.output import Output
from .utils import has_msg_sender_check


class BalanceUsage(AbstractDetector):
    ARGUMENT = "balance-usage"

    HELP = ' '
    IMPACT = DetectorClassification.MEDIUM
    CONFIDENCE = DetectorClassification.MEDIUM

    WIKI = 'check usage of address.balance'
    WIKI_TITLE = WIKI
    WIKI_DESCRIPTION = WIKI_TITLE
    WIKI_RECOMMENDATION = WIKI_TITLE
    WIKI_EXPLOIT_SCENARIO = WIKI_TITLE

    def _func_use_balance(self, func: FunctionContract):
        for call in func.internal_calls:
            if isinstance(call, SolidityFunction) and call.name == 'balance(address)':
                return True
            elif isinstance(call, FunctionContract):
                return self._func_use_balance(call)
        return False

    def _detect(self) -> List[Output]:
        results = []
        for contract in self.contracts:
            for func in contract.functions:
                if func.visibility in ['external', 'public'] and self._func_use_balance(func) \
                        and not has_msg_sender_check(func):
                    results.append(self.generate_result(['use balance in function ', func, '\n']))
        return results
