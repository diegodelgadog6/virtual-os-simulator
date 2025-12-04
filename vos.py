from core.sys import Kernel
from core.demo_tasks import shell_prog
from core.process import State

def main():
    print("=" * 60)
    print("VOS - Virtual Operating System (Lab 2 & Lab 3)")
    print("=" * 60)
    print()
    
    kernel = Kernel()
    
    kernel.spawn(shell_prog, "shell")
    
    while True:
        print(f"\nps: {kernel.ps()}")
        
        kernel.dispatch()
        
        if not kernel.procs:
            print("\n[Kernel] No more processes. Halting.")
            break
        
        if all(p.state == State.TERMINATED for p in kernel.procs.values()):
            print("\n[Kernel] All processes terminated. Halting.")
            break
    
    print("\n" + "=" * 60)
    print("VOS terminated. Goodbye!")
    print("=" * 60)


if __name__ == "__main__":
    main()