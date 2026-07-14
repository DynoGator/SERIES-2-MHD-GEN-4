from typing import List, Type, Callable, Literal
from dataclasses import dataclass, field
from physics.scavengers.base import BaseScavenger

@dataclass
class ABTestReport:
    scavenger_name: str
    with_w: float
    without_w: float
    net_delta_w: float
    status: str

@dataclass
class ScavengerEntry:
    module_class: Type[BaseScavenger]
    status: Literal["PENDING", "EARNED", "KILLED"]
    kill_criterion: Callable[[ABTestReport], bool]
    ab_test_history: List[ABTestReport] = field(default_factory=list)
