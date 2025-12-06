from vos.core.sys import Kernel
from vos.core.demo_tasks import touch_pages_prog, idle_prog

kernel = Kernel()

# Crear dos procesos con programas distintos
kernel.spawn(touch_pages_prog, "touch")
kernel.spawn(idle_prog, "idle")

for step in range(10):
    print(f"\n[Step {step:02}] ps: {kernel.ps()}")
    kernel.dispatch()

print("\n[Final state] ps:", kernel.ps())
