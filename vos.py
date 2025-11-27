#!/usr/bin/env python3
"""
VOS - Virtual Operating System
Lab 2 & Lab 3 Combined

Usage: python vos.py
"""

from core.sys import Kernel
from core.demo_tasks import shell_prog
from core.process import State


def main():
    """
    Punto de entrada principal del VOS.
    
    Implementa dispatch loop según Lab 2:
    1. Crea el kernel
    2. Spawna el shell inicial
    3. Loop que llama dispatch() repetidamente
    4. Los procesos se ejecutan slice por slice
    """
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