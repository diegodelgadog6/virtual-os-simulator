from vos.core.sys import Kernel
from vos.core.demo_tasks import shell_prog

kernel = Kernel()

# Proceso inicial: un shell
kernel.spawn(shell_prog, "shell")

# Bucle principal del “sistema operativo”
while True:
    # Mostrar tabla de procesos antes de cada dispatch
    print(f"\nps: {kernel.ps()}")
    kernel.dispatch()

    # Condición de salida: no queda ningún proceso vivo
    if all(p.state == State.TERMINATED for p in kernel.procs.values()):
        print("\n[Kernel] No more processes. Halting.")
        break
