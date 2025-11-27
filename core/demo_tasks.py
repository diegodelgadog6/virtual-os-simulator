"""
Demo tasks/programs for VOS
"""
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


# ---------- SHELL MEJORADO (LAB 3) ----------

def shell_prog(kernel, pcb):
    """
    Shell interactivo COOPERATIVO para Lab 2 & Lab 3.
    
    IMPORTANTE: Este shell NO tiene while True.
    Se ejecuta UN COMANDO por cada dispatch() call.
    Esto permite que otros procesos también se ejecuten.
    """
    
    # Inicializar estado si es la primera vez
    if not hasattr(pcb, "depth"):
        pcb.depth = 0
        pcb.child_shell = None
        print(f"\n[Shell {pcb.pid}] Started (depth={pcb.depth})")
    
    # Asegurar que child_shell siempre exista (por si acaso)
    if not hasattr(pcb, "child_shell"):
        pcb.child_shell = None
    
    # Si hay un subshell activo, no hacer nada (el hijo se ejecuta)
    if pcb.child_shell and pcb.child_shell.state != State.TERMINATED:
        return
    
    # Si el subshell terminó, limpiarlo
    if pcb.child_shell and pcb.child_shell.state == State.TERMINATED:
        print(f"[Shell {pcb.pid}] Subshell {pcb.child_shell.pid} exited")
        pcb.child_shell = None
    
    # Mostrar prompt y leer UN comando
    prompt = f"vos[{pcb.pid}:{pcb.depth}]> "
    
    try:
        line = input(prompt).strip()
    except EOFError:
        pcb.state = State.TERMINATED
        print(f"\n[Shell {pcb.pid}] EOF detected, exiting.")
        return
    
    # Línea vacía, no hacer nada este slice
    if not line:
        return
    
    # Parsear comando y argumentos
    parts = line.split()
    cmd = parts[0]
    args = parts[1:]
    
    # ========== COMANDOS DE PROCESOS ==========
    
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
    
    # ========== COMANDOS DE FILESYSTEM ==========
    
    elif cmd == "ls":
        path = args[0] if args else None
        kernel.ls_sys(path)
    
    elif cmd == "cd":
        if not args:
            print("usage: cd <path>")
        else:
            kernel.cd_sys(args[0])
    
    elif cmd == "pwd":
        print(f"cwd: {kernel.cwd}")
    
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
    
    # ========== COMANDOS DE SHELL ==========
    
    elif cmd == "shell":
        # Crear un nuevo subshell
        print(f"[Shell {pcb.pid}] Creating subshell...")
        child_pcb = kernel.spawn(shell_prog, "shell")
        child_pcb.depth = pcb.depth + 1
        pcb.child_shell = child_pcb
        print(f"[Shell {pcb.pid}] Created subshell {child_pcb.pid}")
    
    elif cmd == "exit":
        print(f"[Shell {pcb.pid}] Exiting (depth={pcb.depth})")
        pcb.state = State.TERMINATED
    
    elif cmd == "help":
        print("""
Available commands:
  Process control:
    ps                      - list all processes
    kill <pid>              - terminate process
    vmtest                  - spawn memory test program
    idle                    - spawn idle program
    readvm <pid> <vaddr>    - read byte from process memory
    writevm <pid> <vaddr> <value> - write byte to process memory
    
  Filesystem:
    ls [path]               - list directory
    cd <path>               - change directory
    pwd                     - print working directory
    touch <file>            - create empty file
    cat <file>              - display file contents
    
  Shell:
    shell                   - create new subshell
    exit                    - exit current shell
    help                    - show this message
""")
    
    else:
        print(f"Unknown command: {cmd}")
        print("Type 'help' for available commands")