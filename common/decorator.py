# -*- coding:utf-8 -*-

def format_address(func):
    """
    format address string in parameters to lower case
    :param func:
    :return:
    """

    def wrapper(*args, **kwargs):
        new_args = []
        for arg in args:
            if type(arg) == str and len(arg) == 42:
                arg = arg.lower()
            new_args.append(arg)
        new_kwargs = {}
        for k, v in kwargs.items():
            if type(v) == str and len(v) == 42:
                v = v.lower()
            new_kwargs[k] = v
        return func(*new_args, **new_kwargs)

    return wrapper
