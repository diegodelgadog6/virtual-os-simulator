## 🧩 Prompt 1 – Process Control Block (PCB) and States

**Prompt enviado:**

Diseña una clase `PCB` (Process Control Block) en Python que guarde la información esencial de un proceso en un sistema operativo simulado.

Debe incluir:
- Un `pid` único (int)
- Un campo `state` con los estados típicos (NEW, READY, RUNNING, WAITING, TERMINATED)
- Un espacio de memoria `vm` (instancia de la clase `VM`)
- Un `prog` que sea una función que representa el código del proceso
- Un contador de CPU (`cpu_time`)
- Un nombre descriptivo (`name`)

Usa `@dataclass` y crea también una enumeración `State` para los estados.  
Incluye un método `__repr__` para imprimir el estado del proceso.

**Respuesta generada:**

```python
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable
from vos.core.vm import VM

class State(Enum):
    NEW = auto()
    READY = auto()
    RUNNING = auto()
    WAITING = auto()
    TERMINATED = auto()

@dataclass
class PCB:
    pid: int
    state: State = State.NEW
    vm: VM = field(default_factory=VM)
    prog: Callable[['Kernel', 'PCB'], None] = None
    cpu_time: int = 0
    name: str = "process"

    def __repr__(self):
        return f"PCB(pid={self.pid}, state={self.state.name}, cpu_time={self.cpu_time})"
```

**Explicación:**  
El PCB almacena toda la información del proceso: su estado, la memoria virtual asociada y el código que ejecutará.  
Esto replica cómo un sistema operativo mantiene datos de control por cada proceso activo.

---

## ⚙️ Prompt 2 – Round-Robin Scheduler

**Prompt enviado:**

Crea una clase `RoundRobinScheduler` que implemente un planificador de procesos con política FIFO (First-In, First-Out) o Round-Robin.  
Debe tener:
- Una cola `ready` (usa `collections.deque`)  
- Un método `add(pcb)` que agrega procesos listos a la cola  
- Un método `next()` que devuelve el siguiente proceso a ejecutar, o `None` si no hay listos.

**Respuesta generada:**

```python
from collections import deque
from vos.core.process import PCB, State

class RoundRobinScheduler:
    def __init__(self):
        self.ready = deque()

    def add(self, pcb: PCB):
        if pcb.state != State.TERMINATED:
            pcb.state = State.READY
            self.ready.append(pcb)

    def next(self):
        if not self.ready:
            return None
        pcb = self.ready.popleft()
        return pcb
```

**Explicación:**  
La clase simula un scheduler muy simple basado en una cola circular.  
Los procesos se van turnando para usar la CPU, y si un proceso aún no termina, puede volver a la cola.

---

## 🧠 Prompt 3 – Kernel

**Prompt enviado:**

Diseña una clase `Kernel` que gestione los procesos y el planificador.  
Debe tener:
- Un objeto `RoundRobinScheduler`
- Una lista/diccionario de procesos (`self.procs`)
- Un método `spawn(prog, name)` para crear un proceso nuevo
- Un método `dispatch()` que tome el siguiente proceso listo y lo ejecute (llamando a su función `prog`)
- Un método `ps()` que liste los procesos y sus estados.

**Respuesta generada:**

```python
from vos.core.sched import RoundRobinScheduler
from vos.core.process import PCB, State

class Kernel:
    def __init__(self):
        self.sched = RoundRobinScheduler()
        self.procs = {}
        self.pid_counter = 1
        self.running = None

    def spawn(self, prog, name="proc"):
        pid = self.pid_counter
        pcb = PCB(pid=pid, prog=prog, name=name)
        pcb.state = State.READY
        self.procs[pid] = pcb
        self.sched.add(pcb)
        self.pid_counter += 1
        print(f"[Spawn] Created process {pid} ({name})")
        return pcb

    def dispatch(self):
        # Reagendar el proceso actual si sigue activo
        if self.running and self.running.state == State.RUNNING:
            self.running.state = State.READY
            self.sched.add(self.running)

        pcb = self.sched.next()
        if pcb is None:
            print("[Kernel] No READY processes.")
            self.running = None
            return

        self.running = pcb
        pcb.state = State.RUNNING
        pcb.cpu_time += 1

        print(f"[Dispatch] Running PID={pcb.pid} ({pcb.name})")
        pcb.prog(self, pcb)

    def ps(self):
        return [(p.pid, p.state.name) for p in self.procs.values()]
```

**Explicación:**  
El kernel coordina todo: crea procesos, los mete en la cola del scheduler y los va ejecutando en cada turno.  
Además, usa `dispatch()` para simular el cambio de contexto entre procesos.

---

## 🧩 Prompt 4 – Demo Programs (Procesos simulados)

**Prompt enviado:**

Crea un archivo `demo_tasks.py` con dos funciones de ejemplo que representen programas de usuario:
1. `touch_pages_prog`: escribe en memoria virtual usando `vm.write_byte` (simula uso de memoria).
2. `idle_prog`: solo imprime un contador y termina después de varios ticks.

Cada programa debe recibir `(kernel, pcb)` como argumentos y terminar cambiando `pcb.state = TERMINATED`.

**Respuesta generada:**

```python
from vos.core.process import State
from vos.core.vm import PAGE_SIZE

def touch_pages_prog(kernel, pcb):
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
    if not hasattr(pcb, "ticks"):
        pcb.ticks = 0
    pcb.ticks += 1
    print(f"[Idle {pcb.pid}] tick {pcb.ticks}")
    if pcb.ticks > 5:
        pcb.state = State.TERMINATED
        print(f"[Idle {pcb.pid}] done.")
```

**Explicación:**  
Estos programas simulan dos tipos de procesos:  
- Uno que usa su memoria (como si fuera un proceso que manipula datos).  
- Otro que solo “espera” (un proceso inactivo o de baja prioridad).

---

## 🧩 Prompt 5 – Integration and Test (`run_vos.py`)

**Prompt enviado:**

Crea un programa principal (`run_vos.py`) que:
1. Cree un kernel.
2. Spawnee dos procesos con funciones distintas.
3. Ejecute 10 ciclos de planificación (simulando el paso del tiempo).
4. Muestre los estados de los procesos en cada paso.

**Respuesta generada:**

```python
from vos.core.sys import Kernel
from vos.core.demo_tasks import touch_pages_prog, idle_prog

kernel = Kernel()

kernel.spawn(touch_pages_prog, "touch")
kernel.spawn(idle_prog, "idle")

for step in range(10):
    print(f"\n[Step {step:02}] ps: {kernel.ps()}")
    kernel.dispatch()

print("\n[Final state] ps:", kernel.ps())
```

**Explicación:**  
Este archivo une todo: el kernel, los procesos y el planificador.  
Cada ciclo (`dispatch`) representa un “tick” del CPU donde un proceso se ejecuta por un turno y luego cede la CPU.

---

**Conclusión:**  
El Lab 2 amplía el simulador del Lab 1 agregando manejo de procesos, aislamiento de memoria y planificación Round-Robin.  
El resultado es un mini sistema operativo educativo que muestra cómo varios programas pueden ejecutarse “al mismo tiempo” compartiendo CPU de manera justa.

