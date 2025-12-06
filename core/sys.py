from vos.core.sched import RoundRobinScheduler
from vos.core.process import PCB, State

class Kernel:
    def __init__(self):
        self.sched = RoundRobinScheduler()
        self.procs = {}
        self.pid_counter = 1
        self.running = None

    def spawn(self, prog, name="proc"):
        pid = self.pid_counter
        pcb = PCB(pid=pid, prog=prog, name=name)
        pcb.state = State.READY
        self.procs[pid] = pcb
        self.sched.add(pcb)
        self.pid_counter += 1
        print(f"[Spawn] Created process {pid} ({name})")
        return pcb

    def dispatch(self):
        # requeue running process if still active
        if self.running and self.running.state == State.RUNNING:
            self.running.state = State.READY
            self.sched.add(self.running)

        pcb = self.sched.next()
        if pcb is None:
            print("[Kernel] No READY processes.")
            self.running = None
            return

        self.running = pcb
        pcb.state = State.RUNNING
        pcb.cpu_time += 1

        print(f"[Dispatch] Running PID={pcb.pid} ({pcb.name})")
        pcb.prog(self, pcb)

    def ps(self):
        return [(p.pid, p.state.name) for p in self.procs.values()]
