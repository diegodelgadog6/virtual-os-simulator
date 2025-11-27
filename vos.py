#!/usr/bin/env python3
"""
VOS - Virtual Operating System
Lab 3 Entrypoint

Usage: python vos.py
"""

from core.sys import Kernel
from core.demo_tasks import shell_prog
from core.process import State


def main():
    """
    Punto de entrada principal del VOS.
    
    1. Crea el kernel
    2. Spawna el shell inicial (PID 0)
    3. Lo ejecuta directamente (no usa dispatch en bucle)
    """
    print("=" * 60)
    print("VOS - Virtual Operating System (Lab 3)")
    print("=" * 60)
    print()
    
    # Crear el kernel
    kernel = Kernel()
    
    # Crear el proceso shell inicial con PID 0
    shell_pcb = kernel.spawn(shell_prog, "shell")
    
    # Ejecutar el shell directamente
    # (El shell se encarga de su propio bucle)
    shell_prog(kernel, shell_pcb)
    
    # Cuando el shell termina, el programa termina
    print("\n" + "=" * 60)
    print("VOS terminated. Goodbye!")
    print("=" * 60)


if __name__ == "__main__":
    main()
