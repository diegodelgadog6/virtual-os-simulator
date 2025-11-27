from core.sys import Kernel
from core.demo_tasks import shell_prog
from core.process import State


def main():
    kernel = Kernel()

    # Proceso inicial: shell con PID 0
    kernel.spawn(shell_prog, "shell")

    # Bucle principal del “sistema operativo”
    while True:
        print(f"\nps: {kernel.ps()}")
        kernel.dispatch()

        # Si ya no hay procesos en absoluto
        if not kernel.procs:
            print("\n[Kernel] No more processes. Halting.")
            break

        # O si todos están TERMINATED
        if all(p.state == State.TERMINATED for p in kernel.procs.values()):
            print("\n[Kernel] No more processes. Halting.")
            break


if __name__ == "__main__":
    main()
