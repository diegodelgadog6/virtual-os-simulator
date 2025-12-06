from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, TYPE_CHECKING
from .vm import VM

if TYPE_CHECKING:
    from .sys import Kernel

class State(Enum):
    NEW = auto()
    READY = auto()
    RUNNING = auto()
    WAITING = auto()
    TERMINATED = auto()

@dataclass
class PCB:
    pid: int
    state: State = State.NEW
    vm: VM = field(default_factory=VM)
    prog: Callable[['Kernel', 'PCB'], None] = None
    cpu_time: int = 0
    name: str = "process"

    def __repr__(self):
        return f"PCB(pid={self.pid}, state={self.state.name}, cpu_time={self.cpu_time})"
