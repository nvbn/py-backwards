
from typing import Optional


class Example():

    def fn(self, x: int, y: int) -> int:
        return (x + y)

    def hey(self, x: Optional[str]) -> str:
        return ''.join(['hey ', '{}'.format(x), '!'])
