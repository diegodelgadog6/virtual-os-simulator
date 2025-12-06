from collections import deque
from vos.core.process import PCB, State

class RoundRobinScheduler:
    def __init__(self):
        self.ready = deque()

    def add(self, pcb: PCB):
        if pcb.state != State.TERMINATED:
            pcb.state = State.READY
            self.ready.append(pcb)

    def next(self):
        if not self.ready:
            return None
        pcb = self.ready.popleft()
        return pcb
