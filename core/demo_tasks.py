from .process import State
from .vm import PAGE_SIZE


def touch_pages_prog(kernel, pcb):
    """
    Proceso de ejemplo que usa su memoria virtual.
    Escribe su propio PID en distintas páginas y luego termina.
    """
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
    """
    Proceso que solo imprime 'ticks' y luego termina.
    Sirve para ver el round-robin.
    """
    if not hasattr(pcb, "ticks"):
        pcb.ticks = 0
    pcb.ticks += 1
    print(f"[Idle {pcb.pid}] tick {pcb.ticks}")
    if pcb.ticks > 5:
        pcb.state = State.TERMINATED
        print(f"[Idle {pcb.pid}] done.")


# ---------- SHELL (único proceso con niveles anidados) ----------

def shell_prog(kernel, pcb):
    """
    Shell sencillo que da acceso a las sys-calls del kernel.
    SOLO hay un proceso shell; el comando `shell` entra a un nivel
    anidado (subshell) dentro del mismo proceso, y `exit` sale de
    ese nivel. Cuando la profundidad llega a 0 y vuelves a hacer
    `exit`, el shell se termina.
    """

    # Nivel de anidamiento del shell (0 = normal)
    if not hasattr(pcb, "depth"):
        pcb.depth = 0

    prompt = f"vos[{pcb.pid}:{pcb.depth}]> "
    try:
        line = input(prompt).strip()
    except EOFError:
        pcb.state = State.TERMINATED
        print(f"[shell {pcb.pid}] EOF, exiting.")
        return

    if not line:
        # Comando vacío, no hace nada en este tick
        return

    parts = line.split()
    cmd = parts[0]
    args = parts[1:]

    # ---- Comandos sobre procesos / VM ----

    if cmd == "ps":
        kernel.ps_sys()

    elif cmd == "vmtest":
        kernel.spawn(touch_pages_prog, "vmtest")

    elif cmd == "idle":
        kernel.spawn(idle_prog, "idle")

    elif cmd == "kill":
        if not args:
            print("usage: kill <pid>")
        else:
            try:
                pid = int(args[0])
                kernel.kill_sys(pid)
            except ValueError:
                print("kill: pid must be an integer")

    elif cmd == "readvm":
        if len(args) != 2:
            print("usage: readvm <pid> <vaddr>")
        else:
            try:
                pid = int(args[0])
                vaddr = int(args[1])
                kernel.read_vm_sys(pid, vaddr)
            except ValueError:
                print("readvm: pid and vaddr must be integers")

    elif cmd == "writevm":
        if len(args) != 3:
            print("usage: writevm <pid> <vaddr> <value>")
        else:
            try:
                pid = int(args[0])
                vaddr = int(args[1])
                value = int(args[2])
                kernel.write_vm_sys(pid, vaddr, value)
            except ValueError:
                print("writevm: pid, vaddr and value must be integers")

    # ---- Comandos de filesystem ----

    elif cmd == "ls":
        path = args[0] if args else None
        kernel.ls_sys(path)

    elif cmd == "cd":
        if not args:
            print("usage: cd <path>")
        else:
            kernel.cd_sys(args[0])

    elif cmd == "touch":
        if not args:
            print("usage: touch <filename>")
        else:
            kernel.touch_sys(args[0])

    elif cmd == "cat":
        if not args:
            print("usage: cat <filename>")
        else:
            kernel.cat_sys(args[0])

    # ---- Comandos de shell (anidado) ----

    elif cmd == "shell":
        pcb.depth += 1
        print(f"[shell {pcb.pid}] entering subshell (depth={pcb.depth})")

    elif cmd == "exit":
        if pcb.depth > 0:
            pcb.depth -= 1
            print(f"[shell {pcb.pid}] exit subshell, depth={pcb.depth}")
        else:
            pcb.state = State.TERMINATED
            print(f"[shell {pcb.pid}] exit")

    else:
        print(f"Unknown command: {cmd}")
