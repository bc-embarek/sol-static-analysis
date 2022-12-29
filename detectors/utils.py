# -*- coding:utf-8 -*-
from slither.core.declarations import FunctionContract, SolidityVariableComposed
from slither.core.expressions import CallExpression


def _get_function_variables_read_recursively(func: FunctionContract):
    variables_read = func.variables_read
    if len(func.calls_as_expressions) > 0:
        for call in func.calls_as_expressions:
            if isinstance(call, CallExpression) and \
                    call.called and hasattr(call.called, 'value') and \
                    isinstance(call.called.value, FunctionContract):
                variables_read.extend(_get_function_variables_read_recursively(call.called.value))
    return variables_read


def has_msg_sender_check(func: FunctionContract):
    for modifier in func.modifiers:
        for var in _get_function_variables_read_recursively(modifier):
            if isinstance(var, SolidityVariableComposed) and var.name == 'msg.sender':
                return True
    for var in _get_function_variables_read_recursively(func):
        if isinstance(var, SolidityVariableComposed) and var.name == 'msg.sender':
            return True
    return False
