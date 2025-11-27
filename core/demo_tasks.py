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
    Shell interactivo mejorado para Lab 3.
    
    Soporta:
    - ps, kill, vmtest, idle (comandos de procesos)
    - ls, cd, touch, cat (comandos de filesystem)
    - shell (crear subshell)
    - exit (salir del shell actual)
    
    IMPORTANTE: Este shell usa un bucle while True que bloquea
    el dispatch hasta que el usuario escribe 'exit'. Esto es
    aceptable para Lab 3 según las instrucciones.
    """
    
    # Inicializar nivel de profundidad si es la primera vez
    if not hasattr(pcb, "depth"):
        pcb.depth = 0
    
    print(f"\n[Shell {pcb.pid}] Started (depth={pcb.depth})")
    
    # Bucle principal del shell
    while True:
        # Mostrar prompt con PID y profundidad
        prompt = f"vos[{pcb.pid}:{pcb.depth}]> "
        
        try:
            line = input(prompt).strip()
        except EOFError:
            # Ctrl+D o fin de entrada
            pcb.state = State.TERMINATED
            print(f"\n[Shell {pcb.pid}] EOF detected, exiting.")
            return
        
        # Línea vacía, continuar
        if not line:
            continue
        
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
            # Incrementar profundidad para el hijo
            child_pcb.depth = pcb.depth + 1
            # IMPORTANTE: Llamar directamente al shell hijo (bloquea hasta que termine)
            shell_prog(kernel, child_pcb)
            # Cuando el hijo termina, volvemos aquí
            print(f"[Shell {pcb.pid}] Subshell {child_pcb.pid} exited, returning to shell {pcb.pid}")
        
        elif cmd == "exit":
            if pcb.depth > 0:
                # Subshell: solo salir de este nivel
                print(f"[Shell {pcb.pid}] Exiting subshell (depth={pcb.depth})")
                pcb.state = State.TERMINATED
                return
            else:
                # Shell raíz (depth=0): terminar completamente
                print(f"[Shell {pcb.pid}] Exiting root shell")
                pcb.state = State.TERMINATED
                return
        
        elif cmd == "help":
            print("""
Available commands:
  Process control:
    ps              - list all processes
    kill <pid>      - terminate process
    vmtest          - spawn memory test program
    idle            - spawn idle program
    
  Filesystem:
    ls [path]       - list directory
    cd <path>       - change directory
    pwd             - print working directory
    touch <file>    - create empty file
    cat <file>      - display file contents
    
  Shell:
    shell           - create new subshell
    exit            - exit current shell
    help            - show this message
""")
        
        else:
            print(f"Unknown command: {cmd}")
            print("Type 'help' for available commands")
