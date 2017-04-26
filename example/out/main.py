

def _py_backwards_merge_dicts(dicts):
    result = {}
    for dict_ in dicts:
        result.update(dict_)
    return result


from typing import Optional


class Example():

    def fn(self, x, y):
        return (x + y)

    def hey(self, x):
        return ''.join(['hey ', '{}'.format(x), '!'])


def asd():
    pass
