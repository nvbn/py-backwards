from typing import Optional


class Example:
    a: int

    def fn(self, x: int, y: int) -> int:
        return x + y
    
    def hey(self, x: Optional[str]) -> str:
        return f'hey {x}!'

