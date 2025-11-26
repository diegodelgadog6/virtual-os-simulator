import os
from typing import Dict, List, Tuple, Optional

from vos.core.sched import RoundRobinScheduler
from vos.core.process import PCB, State


class Kernel:
    def __init__(self):
        self.sched = RoundRobinScheduler()
        self.procs: Dict[int, PCB] = {}
        self.pid_counter: int = 1
        self.running: Optional[PCB] = None

        # “current working directory” del sistema simulado
        self.cwd: str = os.getcwd()

    # ------------ Manejo de procesos (Lab 2) ------------

    def spawn(self, prog, name: str = "proc") -> PCB:
        pid = self.pid_counter
        pcb = PCB(pid=pid, prog=prog, name=name)
        pcb.state = State.READY
        self.procs[pid] = pcb
        self.sched.add(pcb)
        self.pid_counter += 1
        print(f"[Spawn] Created process {pid} ({name})")
        return pcb

    def dispatch(self) -> None:
        # Re-agendar el proceso actual si sigue activo
        if self.running and self.running.state == State.RUNNING:
            self.running.state = State.READY
            self.sched.add(self.running)

        pcb = self.sched.next()
        # Saltar procesos que ya estén TERMINATED (por kill_sys)
        while pcb is not None and pcb.state == State.TERMINATED:
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

    def ps(self) -> List[Tuple[int, str]]:
        return [(p.pid, p.state.name) for p in self.procs.values()]

    # ------------ Syscalls Procs / VM ------------

    def read_vm_sys(self, pid: int, vaddr: int) -> int:
        pcb = self.procs.get(pid)
        if pcb is None:
            print(f"[read_vm_sys] PID {pid} not found")
            return 0
        value = pcb.vm.read_byte(vaddr)
        print(f"[read_vm_sys] pid={pid} vaddr={vaddr} -> {value}")
        return value

    def write_vm_sys(self, pid: int, vaddr: int, value: int) -> None:
        pcb = self.procs.get(pid)
        if pcb is None:
            print(f"[write_vm_sys] PID {pid} not found")
            return
        pcb.vm.write_byte(vaddr, value)
        print(f"[write_vm_sys] pid={pid} vaddr={vaddr} value={value}")

    def ps_sys(self) -> List[Tuple[int, str]]:
        table = self.ps()
        print("[ps_sys]")
        for pid, state in table:
            print(f"  pid={pid} state={state}")
        return table

    def kill_sys(self, pid: int) -> None:
        pcb = self.procs.get(pid)
        if pcb is None:
            print(f"[kill_sys] PID {pid} not found")
            return
        pcb.state = State.TERMINATED
        print(f"[kill_sys] pid={pid} -> TERMINATED")

    # ------------ Syscalls Filesystem ------------

    def ls_sys(self, path: Optional[str] = None) -> List[str]:
        if path is None:
            full_path = self.cwd
        else:
            full_path = os.path.join(self.cwd, path)

        try:
            entries = os.listdir(full_path)
            print(f"[ls_sys] {full_path}:")
            for name in entries:
                print(" ", name)
            return entries
        except FileNotFoundError:
            print(f"[ls_sys] path not found: {full_path}")
            return []

    def cd_sys(self, path: str) -> None:
        new_path = os.path.abspath(os.path.join(self.cwd, path))
        if os.path.isdir(new_path):
            self.cwd = new_path
            print(f"[cd_sys] cwd = {self.cwd}")
        else:
            print(f"[cd_sys] not a directory: {new_path}")

    def touch_sys(self, filename: str) -> str:
        full = os.path.join(self.cwd, filename)
        with open(full, "a", encoding="utf-8"):
            pass
        print(f"[touch_sys] created {full}")
        return full

    def cat_sys(self, filename: str) -> str:
        full = os.path.join(self.cwd, filename)
        try:
            with open(full, "r", encoding="utf-8") as f:
                data = f.read()
            print(f"[cat_sys] {full}:\n{data}")
            return data
        except FileNotFoundError:
            print(f"[cat_sys] file not found: {full}")
            return ""
