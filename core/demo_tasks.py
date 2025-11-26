from vos.core.process import State
from vos.core.vm import PAGE_SIZE

def touch_pages_prog(kernel, pcb):
    if not hasattr(pcb, "counter"):
        pcb.counter = 0
    addr = pcb.counter * PAGE_SIZE + 4
    pcb.vm.write_byte(addr, pcb.pid)
    print(f"[Prog {pcb.pid}] wrote pid={pcb.pid} to vaddr={addr}")
    pcb.counter += 1
    if pcb.counter > 4:
        pcb.state = State.TERMINATED
        print(f"[Prog {pcb.pid}] finished.")

def idle_prog(kernel, pcb):
    if not hasattr(pcb, "ticks"):
        pcb.ticks = 0
    pcb.ticks += 1
    print(f"[Idle {pcb.pid}] tick {pcb.ticks}")
    if pcb.ticks > 5:
        pcb.state = State.TERMINATED
        print(f"[Idle {pcb.pid}] done.")
