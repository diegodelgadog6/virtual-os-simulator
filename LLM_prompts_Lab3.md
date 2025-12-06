# LLM Prompts - Lab 3: System Calls & Interactive Shell

Este documento contiene todos los prompts utilizados para desarrollar el Lab 3 del VOS (Virtual Operating System).

## Contexto

Lab 3 se enfoca en:
- Implementar system calls para filesystem (ls, cd, pwd, touch, cat)
- Implementar system call kill para terminar procesos
- Crear un shell interactivo que pueda crear subshells anidados
- Integrar todo con el sistema de scheduling del Lab 2

---

## Prompt 1 - Arreglar Imports Circulares

### Prompt Inicial

```
Tengo un proyecto Python con la siguiente estructura:

vos/
├── vos.py
└── core/
    ├── vm.py
    ├── process.py
    ├── sched.py
    └── sys.py

El problema es que tengo un error de imports circulares:

ImportError: cannot import name 'Kernel' from partially initialized module 'core.sys'

Esto ocurre porque:
- vos.py hace: from core.sys import Kernel
- sys.py hace: from .sched import RoundRobinScheduler
- sched.py hace: from vos.core.process import PCB, State (ruta absoluta)

¿Cómo puedo arreglar esto usando imports relativos correctamente?
```

### Prompt Refinado

```
Necesito arreglar imports circulares en mi proyecto Python. La estructura es:

vos/
├── vos.py                 # Entry point
└── core/
    ├── vm.py              # Virtual memory
    ├── process.py         # PCB class
    ├── sched.py           # Scheduler
    └── sys.py             # Kernel

Requisitos:
1. core/ debe ser un paquete Python válido
2. Todos los archivos en core/ deben usar imports RELATIVOS entre sí
3. vos.py debe poder importar desde core/ sin problemas
4. NO debe haber imports circulares

Específicamente:
- process.py importa: from .vm import VM
- sched.py importa: from .process import PCB, State
- sys.py importa: from .sched import RoundRobinScheduler, from .process import PCB, State
- vos.py importa: from core.sys import Kernel, from core.demo_tasks import shell_prog, from core.process import State

¿Qué archivos necesito crear/modificar para que esto funcione?
```

### Cambios Realizados

- Creé `core/__init__.py` (necesario para que Python reconozca core como paquete)
- Cambié todos los imports en core/ a imports relativos (usando `.`)
- Mantuve imports absolutos solo en vos.py (entry point)

### Respuesta Utilizada

Crear archivo vacío `core/__init__.py` y cambiar:
- `sched.py`: `from vos.core.process import PCB` → `from .process import PCB, State`
- `process.py`: `from vos.core.vm import VM` → `from .vm import VM`
- Mantener sys.py como estaba (ya usaba imports relativos)

---

## Prompt 2 - System Calls de Filesystem

### Prompt Inicial

```
Necesito implementar system calls para filesystem en mi clase Kernel. 
Los syscalls que necesito son:
- ls(path) - listar archivos
- cd(path) - cambiar directorio
- touch(filename) - crear archivo
- cat(filename) - leer archivo

Dame la implementación de estos métodos.
```

### Prompt Refinado

```
Estoy implementando un Virtual OS en Python y necesito agregar syscalls de filesystem a mi clase Kernel.

Contexto actual:
- El Kernel ya tiene self.cwd que guarda el directorio actual (inicializado con os.getcwd())
- Los syscalls deben ser métodos de la clase Kernel
- Deben imprimir mensajes de log para debugging (como [ls_sys], [cd_sys], etc.)

Syscalls a implementar:

1. ls_sys(self, path: Optional[str] = None) -> List[str]
   - Si path es None, usar self.cwd
   - Si path es relativo, combinarlo con self.cwd usando os.path.join()
   - Usar os.listdir() para obtener archivos
   - Imprimir el path completo y los archivos encontrados
   - Manejar FileNotFoundError
   - Retornar la lista de archivos

2. cd_sys(self, path: str) -> None
   - Combinar path con self.cwd para obtener path absoluto
   - Verificar que sea directorio válido con os.path.isdir()
   - Actualizar self.cwd
   - Imprimir mensaje de confirmación

3. touch_sys(self, filename: str) -> str
   - Crear archivo en self.cwd
   - Usar open() con modo 'a' (append) para crear si no existe
   - Retornar path completo del archivo creado

4. cat_sys(self, filename: str) -> str
   - Leer contenido del archivo
   - Imprimir el path y contenido
   - Manejar FileNotFoundError
   - Retornar el contenido como string

Proporciona el código completo de estos 4 métodos para agregar a la clase Kernel.
```

### Respuesta Utilizada

```python
def ls_sys(self, path: Optional[str] = None) -> List[str]:
    if path is None:
        full_path = self.cwd
    else:
        full_path = os.path.join(self.cwd, path)

    try:
        entries = os.listdir(full_path)
        print(f"[ls_sys] {full_path}:")
        for name in entries:
            print(" ", name)
        return entries
    except FileNotFoundError:
        print(f"[ls_sys] path not found: {full_path}")
        return []

def cd_sys(self, path: str) -> None:
    new_path = os.path.abspath(os.path.join(self.cwd, path))
    if os.path.isdir(new_path):
        self.cwd = new_path
        print(f"[cd_sys] cwd = {self.cwd}")
    else:
        print(f"[cd_sys] not a directory: {new_path}")

def touch_sys(self, filename: str) -> str:
    full = os.path.join(self.cwd, filename)
    with open(full, "a", encoding="utf-8"):
        pass
    print(f"[touch_sys] created {full}")
    return full

def cat_sys(self, filename: str) -> str:
    full = os.path.join(self.cwd, filename)
    try:
        with open(full, "r", encoding="utf-8") as f:
            data = f.read()
        print(f"[cat_sys] {full}:\n{data}")
        return data
    except FileNotFoundError:
        print(f"[cat_sys] file not found: {full}")
        return ""
```

---

## Prompt 3 - Shell Cooperativo con Dispatch Loop

### Prompt Inicial

```
Tengo un shell bloqueante con while True que no permite que otros procesos se ejecuten. 
Necesito convertirlo en un shell cooperativo que se ejecute con el dispatch loop del scheduler.
```

### Prompt Refinado

```
Estoy implementando un shell interactivo para mi Virtual OS. El problema es que el shell actual usa while True y bloquea todo el sistema.

Contexto:
- Tengo un Kernel con dispatch() que ejecuta un time-slice de cada proceso en round-robin
- Los procesos son funciones: def prog(kernel, pcb): ...
- El dispatch loop está en vos.py y llama kernel.dispatch() repetidamente

Requisito:
- El shell debe ser COOPERATIVO: ejecutar UN comando por cada llamada a dispatch()
- No puede usar while True (eso bloquea el scheduler)
- Debe mantener su estado entre llamadas (porque se ejecuta slice por slice)

Diseño propuesto:
1. La función shell_prog(kernel, pcb) se llama una vez por dispatch
2. Usa hasattr() para inicializar variables en el PCB la primera vez
3. Lee UN comando con input()
4. Ejecuta ese comando
5. Retorna (cede control al scheduler)
6. En la siguiente llamada, continúa desde donde dejó

Implementa shell_prog() con este diseño cooperativo. El shell debe soportar estos comandos:
- ps, vmtest, idle, kill <pid>
- ls, cd, pwd, touch, cat
- shell (crear subshell), exit, help

Para subshells:
- Cuando se ejecuta "shell", crear un nuevo proceso shell con depth+1
- Guardar referencia al hijo en pcb.child_shell
- Mientras el hijo esté activo (no TERMINATED), el padre no hace nada
- Cuando el hijo termina, el padre continúa normalmente

Proporciona el código completo de shell_prog().
```

### Respuesta Utilizada

La función completa `shell_prog()` del archivo `demo_tasks.py` que:
- Inicializa depth y child_shell en el PCB
- Ejecuta UN comando por dispatch call (no while True)
- Maneja subshells guardando referencia al hijo
- Implementa todos los comandos requeridos
- Usa return para ceder control al scheduler

---

## Prompt 4 - Modificar vos.py para Dispatch Loop

### Prompt Inicial

```
Mi vos.py actual ejecuta el shell directamente:
shell_prog(kernel, shell_pcb)

Pero necesito cambiarlo para usar dispatch loop según Lab 2.
```

### Prompt Refinado

```
Necesito modificar mi archivo vos.py para implementar correctamente el dispatch loop del Lab 2.

Código actual (INCORRECTO):
```python
kernel = Kernel()
shell_pcb = kernel.spawn(shell_prog, "shell")
shell_prog(kernel, shell_pcb)  # Ejecución directa - bloquea todo
print("VOS terminated. Goodbye!")
```

Comportamiento deseado (según Lab 2):
1. Crear kernel
2. Spawnar el shell inicial
3. Bucle infinito que llama kernel.dispatch() repetidamente
4. Cada proceso (incluyendo el shell) se ejecuta slice por slice
5. Terminar cuando no haya más procesos activos

Condiciones de terminación:
- Si kernel.procs está vacío (no hay procesos)
- O si todos los procesos están en estado TERMINATED

Proporciona el código completo del archivo vos.py con:
- main() function
- Dispatch loop correcto
- Verificación de terminación
- Mensajes informativos
```

### Respuesta Utilizada

```python
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
```

---

## Prompt 5 - Funcionalidad Extra: readvm_sys y writevm_sys

### Prompt Inicial

```
Quiero agregar syscalls para leer y escribir en la memoria virtual de otros procesos.
¿Cómo los implemento?
```

### Prompt Refinado

```
Necesito implementar syscalls para acceder a la memoria virtual de procesos desde el shell (para debugging/demostración).

Contexto:
- Cada proceso tiene su propia VM en pcb.vm
- VM tiene métodos: read_byte(vaddr) y write_byte(vaddr, value)
- Los procesos están en self.procs (dict de pid -> PCB)

Syscalls a implementar:

1. read_vm_sys(self, pid: int, vaddr: int) -> int
   - Buscar el PCB con ese pid en self.procs
   - Si no existe, imprimir error y retornar 0
   - Llamar pcb.vm.read_byte(vaddr)
   - Imprimir mensaje de log con pid, vaddr y valor leído
   - Retornar el valor

2. write_vm_sys(self, pid: int, vaddr: int, value: int) -> None
   - Buscar el PCB con ese pid
   - Si no existe, imprimir error y retornar
   - Llamar pcb.vm.write_byte(vaddr, value)
   - Imprimir mensaje de log con pid, vaddr y value

Estos syscalls se usarán desde el shell con comandos:
- readvm <pid> <vaddr>
- writevm <pid> <vaddr> <value>

Proporciona el código de ambos métodos.
```

### Respuesta Utilizada

```python
def read_vm_sys(self, pid: int, vaddr: int) -> int:
    pcb = self.procs.get(pid)
    if pcb is None:
        print(f"[read_vm_sys] PID {pid} not found")
        return 0
    value = pcb.vm.read_byte(vaddr)
    print(f"[read_vm_sys] pid={pid} vaddr={vaddr} -> {value}")
    return value

def write_vm_sys(self, pid: int, vaddr: int, value: int) -> None:
    pcb = self.procs.get(pid)
    if pcb is None:
        print(f"[write_vm_sys] PID {pid} not found")
        return
    pcb.vm.write_byte(vaddr, value)
    print(f"[write_vm_sys] pid={pid} vaddr={vaddr} value={value}")
```

---

## Prompt 6 - Comandos del Shell

### Prompt Inicial

```
¿Cómo implemento el parser de comandos en el shell?
```

### Prompt Refinado

```
Necesito implementar el parser y dispatcher de comandos dentro de shell_prog().

El shell debe:
1. Leer una línea con input()
2. Parsear el comando y argumentos con split()
3. Ejecutar el comando correspondiente usando if/elif/else
4. Manejar errores de argumentos (mostrar usage)

Comandos a implementar:

PROCESOS:
- ps → kernel.ps_sys()
- vmtest → kernel.spawn(touch_pages_prog, "vmtest")
- idle → kernel.spawn(idle_prog, "idle")
- kill <pid> → kernel.kill_sys(int(pid))
- readvm <pid> <vaddr> → kernel.read_vm_sys(int(pid), int(vaddr))
- writevm <pid> <vaddr> <value> → kernel.write_vm_sys(int(pid), int(vaddr), int(value))

FILESYSTEM:
- ls [path] → kernel.ls_sys(path if path else None)
- cd <path> → kernel.cd_sys(path)
- pwd → print(f"cwd: {kernel.cwd}")
- touch <file> → kernel.touch_sys(file)
- cat <file> → kernel.cat_sys(file)

SHELL:
- shell → crear subshell (explicado en prompt anterior)
- exit → pcb.state = State.TERMINATED
- help → imprimir ayuda con todos los comandos

Consideraciones:
- Si el comando tiene argumentos incorrectos, mostrar "usage: comando <args>"
- Si el comando no existe, mostrar "Unknown command"
- Parsear argumentos numéricos con int() y manejar ValueError

Proporciona el código del parser completo (la sección de if/elif/else del shell).
```

### Respuesta Utilizada

Todo el bloque de `if cmd == "ps": ... elif cmd == "vmtest": ... elif cmd == "exit": ...` completo del archivo demo_tasks.py.

---

## Prompt 7 - Comando Help

### Prompt Inicial

```
Necesito agregar un comando help que muestre todos los comandos disponibles.
```

### Prompt Refinado

```
Para el comando "help" del shell, necesito mostrar una lista bien formateada de todos los comandos disponibles.

Formato deseado:
- Agrupar por categoría (Process control, Filesystem, Shell)
- Mostrar sintaxis: comando <args> - descripción
- Usar indentación consistente

Comandos a incluir:

Process control:
  ps - list all processes
  kill <pid> - terminate process
  vmtest - spawn memory test program
  idle - spawn idle program
  readvm <pid> <vaddr> - read byte from process memory
  writevm <pid> <vaddr> <value> - write byte to process memory

Filesystem:
  ls [path] - list directory
  cd <path> - change directory
  pwd - print working directory
  touch <file> - create empty file
  cat <file> - display file contents

Shell:
  shell - create new subshell
  exit - exit current shell
  help - show this message

Proporciona el código del elif para el comando help con este formato.
```

### Respuesta Utilizada

```python
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
```

---

## Resumen de Cambios - Lab 3

### Archivos Creados
1. `core/__init__.py` - Paquete Python para core

### Archivos Modificados

1. **core/sched.py**
   - Cambió imports a relativos: `from .process import PCB, State`

2. **core/process.py**
   - Cambió imports a relativos: `from .vm import VM`

3. **core/sys.py**
   - Agregó syscalls: `ls_sys()`, `cd_sys()`, `touch_sys()`, `cat_sys()`
   - Agregó syscalls: `read_vm_sys()`, `write_vm_sys()`
   - Ya tenía: `ps_sys()`, `kill_sys()`

4. **core/demo_tasks.py**
   - Reescribió `shell_prog()` completamente
   - Shell cooperativo (sin while True)
   - Soporte para todos los comandos
   - Implementación de subshells anidados
   - Comando help actualizado

5. **vos.py**
   - Implementó dispatch loop correcto
   - Condiciones de terminación apropiadas
   - Mensajes informativos

### Conceptos Implementados

1. **System Calls**
   - Interfaz kernel-espacio de usuario
   - Syscalls de filesystem (ls, cd, pwd, touch, cat)
   - Syscalls de procesos (ps, kill, spawn)
   - Syscalls de memoria (readvm, writevm)

2. **Shell Cooperativo**
   - Ejecución slice por slice
   - Mantenimiento de estado entre llamadas
   - Parser de comandos
   - Subshells anidados con profundidad

3. **Integración con Scheduler**
   - El shell es un proceso más
   - Round-robin entre shell y otros procesos
   - Subshells como procesos independientes

### Funcionalidades Extra

- `readvm` y `writevm` para debugging de memoria
- Sistema de profundidad (depth) en subshells
- Prompt informativo: `vos[PID:DEPTH]>`
- Comando `help` completo

---

## Lecciones Aprendidas

1. **Imports en Python**: La importancia de usar imports relativos dentro de paquetes y cómo `__init__.py` convierte un directorio en paquete.

2. **Diseño Cooperativo**: Un programa puede ser "pausable" manteniendo su estado y retornando control periódicamente.

3. **Abstracción de Syscalls**: Los syscalls son simplemente métodos del kernel que encapsulan operaciones privilegiadas.

4. **Jerarquía de Procesos**: Los subshells son procesos normales pero con una relación padre-hijo explícita.

5. **Prompt Engineering**: Prompts específicos con contexto claro, requisitos detallados y ejemplos producen mejores resultados que prompts genéricos.

---

## Conclusión

Lab 3 completó el VOS con:
- ✅ Shell interactivo funcional
- ✅ Subshells anidados
- ✅ System calls de filesystem
- ✅ Integración correcta con scheduler
- ✅ Funcionalidades extra (readvm/writevm)

El sistema ahora es un simulador educativo completo de un OS con memoria virtual, scheduling, syscalls y shell interactivo.