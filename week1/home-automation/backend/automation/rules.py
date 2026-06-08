from dataclasses import dataclass
from typing import Callable, Optional

@dataclass
class Rule:
    name: str
    condition: Callable[[dict], bool]
    action: Callable[[dict], None]
    priority: int = 0
    cooldown: int = 0 #antalet sekunder
    last_triggered: float = 0