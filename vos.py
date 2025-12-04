from core.sys import Kernel
from core.demo_tasks import shell_prog
from core.process import State


def main():
    print("=" * 60)
    print("VOS - Virtual Operating System (Lab 2 & Lab 3)")
    print("=" * 60)
    print()
    
    # Crear el kernel
    kernel = Kernel()
    
    # Crear el proceso shell inicial con PID 0
    kernel.spawn(shell_prog, "shell")
    
    # Bucle principal: dispatch hasta que no haya procesos
    while True:
        # Mostrar tabla de procesos (solo activos, no TERMINATED)
        print(f"\nps: {kernel.ps()}")
        
        # Ejecutar un time slice
        kernel.dispatch()
        
        # Si ya no hay procesos activos, terminar
        if not kernel.procs:
            print("\n[Kernel] No more processes. Halting.")
            break
        
        # O si todos están TERMINATED
        if all(p.state == State.TERMINATED for p in kernel.procs.values()):
            print("\n[Kernel] All processes terminated. Halting.")
            break
    
    print("\n" + "=" * 60)
    print("VOS terminated. Goodbye!")
    print("=" * 60)


if __name__ == "__main__":
    main()