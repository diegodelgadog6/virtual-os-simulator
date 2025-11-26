from vos.core.process import State
from vos.core.vm import PAGE_SIZE


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


# ---------- SHELL ----------

def shell_prog(kernel, pcb):
    """
    Shell sencillo que da acceso a las sys-calls del kernel.
    Cada vez que el scheduler le da CPU, lee UN comando,
    lo ejecuta y regresa (para respetar el round-robin).
    """

    # Prompt
    try:
        line = input("vos> ").strip()
    except EOFError:
        # Si por alguna razón no hay input, matar el shell
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
        # ver procesos -> ps_sys
        kernel.ps_sys()

    elif cmd == "spawn":
        # spawn <prog>
        if not args:
            print("usage: spawn <touch|idle|shell>")
        else:
            which = args[0]
            if which == "touch":
                kernel.spawn(touch_pages_prog, "touch")
            elif which == "idle":
                kernel.spawn(idle_prog, "idle")
            elif which == "shell":
                kernel.spawn(shell_prog, "shell")
            else:
                print(f"spawn: unknown program '{which}'")

    elif cmd == "kill":
        # kill <pid>
        if not args:
            print("usage: kill <pid>")
        else:
            try:
                pid = int(args[0])
                kernel.kill_sys(pid)
            except ValueError:
                print("kill: pid must be an integer")

    elif cmd == "readvm":
        # readvm <pid> <vaddr>
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
        # writevm <pid> <vaddr> <value>
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
        # ls [path]
        path = args[0] if args else None
        kernel.ls_sys(path)

    elif cmd == "cd":
        # cd <path>
        if not args:
            print("usage: cd <path>")
        else:
            kernel.cd_sys(args[0])

    elif cmd == "touch":
        # touch <filename>
        if not args:
            print("usage: touch <filename>")
        else:
            kernel.touch_sys(args[0])

    elif cmd == "cat":
        # cat <filename>
        if not args:
            print("usage: cat <filename>")
        else:
            kernel.cat_sys(args[0])

    # ---- Comandos de shell ----

    elif cmd == "shell":
        # crea otro shell
        kernel.spawn(shell_prog, "shell")

    elif cmd == "exit":
        # termina este shell
        pcb.state = State.TERMINATED
        print(f"[shell {pcb.pid}] exit")

    else:
        print(f"Unknown command: {cmd}")
