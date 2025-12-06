# 🖥️ VOS - Virtual Operating System

Un simulador educativo de sistema operativo implementado en Python que incluye memoria virtual, gestión de procesos, scheduling y un shell interactivo.

## 📚 Laboratorios Completados

- ✅ **Lab 1**: Memoria Virtual con paginación y reemplazo FIFO
- ✅ **Lab 2**: Gestión de Procesos y Scheduling Round-Robin
- ✅ **Lab 3**: System Calls y Shell Interactivo Cooperativo

## 🚀 Inicio Rápido

```bash
# Clonar o descomprimir el proyecto
cd vos/

# Ejecutar el VOS
python vos.py
```

## 🎮 Uso del Shell

### Comandos de Procesos
```bash
vos[0:0]> ps                   # Listar procesos activos
vos[0:0]> vmtest               # Crear proceso de prueba de memoria
vos[0:0]> idle                 # Crear proceso idle
vos[0:0]> kill 1               # Terminar proceso con PID 1
vos[0:0]> readvm 1 4           # Leer memoria del proceso 1 en addr 4
vos[0:0]> writevm 1 100 42     # Escribir 42 en addr 100 del proceso 1
```

### Comandos de Filesystem
```bash
vos[0:0]> ls                   # Listar directorio actual
vos[0:0]> ls core              # Listar subdirectorio
vos[0:0]> cd core              # Cambiar directorio
vos[0:0]> pwd                  # Mostrar directorio actual
vos[0:0]> touch test.txt       # Crear archivo
vos[0:0]> cat test.txt         # Mostrar contenido
```

### Comandos de Shell
```bash
vos[0:0]> shell                # Crear subshell (depth=1)
vos[1:1]> ps                   # Ver procesos desde subshell
vos[1:1]> exit                 # Salir de subshell
vos[0:0]> exit                 # Salir del shell raíz (termina VOS)
```

### Otros Comandos
```bash
vos[0:0]> help                 # Mostrar ayuda completa
```

## 🗃️ Arquitectura

```
VOS
├── Kernel (sys.py)
│   ├── Scheduler (Round-Robin)
│   ├── Process Table
│   └── System Calls
│
├── Memoria Virtual (vm.py)
│   ├── Page Table (16 páginas virtuales)
│   ├── Physical Memory (8 frames)
│   └── FIFO Replacement
│
└── Procesos
    ├── PCB (Process Control Block)
    ├── Estados: NEW, READY, RUNNING, TERMINATED
    └── Memoria virtual aislada por proceso
```

## 📁 Estructura del Proyecto

```
vos/
├── vos.py                      # Punto de entrada principal (dispatch loop)
├── core/
│   ├── __init__.py             # Paquete core
│   ├── vm.py                   # Memoria virtual (Lab 1)
│   ├── process.py              # PCB y estados (Lab 2)
│   ├── sched.py                # Scheduler Round-Robin (Lab 2)
│   ├── sys.py                  # Kernel y syscalls (Lab 2 & 3)
│   └── demo_tasks.py           # Programas de ejemplo y shell (Lab 2 & 3)
├── LLM_prompts.md              # Prompts Lab 1
├── LLM_prompts_lab2.md         # Prompts Lab 2
├── LLM_prompts_Lab3.md         # Prompts Lab 3
├── CORRECCIONES_LAB3.md        # Documentación de correcciones
└── README.md                   # Este archivo
```

## 🔬 Conceptos Implementados

### Memoria Virtual (Lab 1)
- **Paginación**: 16 páginas virtuales → 8 frames físicos (256 bytes/página)
- **Page Table**: Mapeo virtual→físico con bits present/dirty
- **Page Faults**: Carga automática de páginas en demanda
- **FIFO Replacement**: Algoritmo de reemplazo cuando no hay frames libres
- **Write-back**: Páginas dirty se escriben a "disco" al ser reemplazadas

### Gestión de Procesos (Lab 2)
- **PCB**: Process Control Block (pid, state, vm, prog, cpu_time, name)
- **Estados**: NEW → READY → RUNNING → TERMINATED
- **Scheduling**: Round-Robin con cola FIFO
- **Dispatch Loop**: Ejecución de time-slices en rotación
- **Aislamiento**: Cada proceso tiene su propia memoria virtual

### System Calls (Lab 3)
- **Procesos**: `ps_sys`, `kill_sys`, `spawn`
- **Memoria**: `read_vm_sys`, `write_vm_sys` (funcionalidad extra)
- **Filesystem**: `ls_sys`, `cd_sys`, `pwd`, `touch_sys`, `cat_sys`

### Shell Interactivo (Lab 3)
- **Shell Cooperativo**: Ejecuta UN comando por dispatch (no bloqueante)
- **Subshells**: Comando `shell` crea procesos shell anidados
- **Stack de Shells**: `exit` sale del shell actual
- **Prompt**: `vos[PID:DEPTH]>` muestra proceso y profundidad
- **Parser**: Interpreta comandos y argumentos

## 🧪 Ejemplos de Uso

### Ejemplo 1: Ver Round-Robin en Acción
```bash
$ python vos.py

ps: [(0, 'READY')]
[Dispatch] Running PID=0 (shell)
[Shell 0] Started (depth=0)

vos[0:0]> vmtest
[Spawn] Created process 1 (vmtest)

ps: [(0, 'RUNNING'), (1, 'READY')]
[Dispatch] Running PID=1 (vmtest)
[Page Fault] Page 0 not in RAM
[Load] Page 0 -> Frame 0
[Write] vaddr=4 (page=0, offset=4) = 1
[Prog 1] wrote pid=1 to vaddr=4

ps: [(0, 'READY'), (1, 'RUNNING')]
[Dispatch] Running PID=0 (shell)

vos[0:0]> ps
[ps_sys]
  pid=0 state=RUNNING
  pid=1 state=READY

# El proceso vmtest continúa ejecutándose en round-robin...
```

### Ejemplo 2: Trabajar con Archivos
```bash
vos[0:0]> pwd
cwd: /home/user/vos

vos[0:0]> touch mi_archivo.txt
[touch_sys] created /home/user/vos/mi_archivo.txt

vos[0:0]> ls
[ls_sys] /home/user/vos:
  mi_archivo.txt
  core
  vos.py
  README.md

vos[0:0]> cd core
[cd_sys] cwd = /home/user/vos/core

vos[0:0]> ls
[ls_sys] /home/user/vos/core:
  __init__.py
  vm.py
  process.py
  sched.py
  sys.py
  demo_tasks.py

vos[0:0]> cd ..
[cd_sys] cwd = /home/user/vos
```

### Ejemplo 3: Funcionalidad Extra - Acceso a Memoria
```bash
vos[0:0]> vmtest
[Spawn] Created process 1 (vmtest)

vos[0:0]> ps
# ... (después de algunos dispatches, vmtest escribió en memoria)

vos[0:0]> readvm 1 4
[read_vm_sys] pid=1 vaddr=4 -> 1

vos[0:0]> readvm 1 260
[read_vm_sys] pid=1 vaddr=260 -> 1

vos[0:0]> writevm 1 100 99
[write_vm_sys] pid=1 vaddr=100 value=99

vos[0:0]> readvm 1 100
[read_vm_sys] pid=1 vaddr=100 -> 99
```

### Ejemplo 4: Subshells Anidados
```bash
vos[0:0]> ps
[ps_sys]
  pid=0 state=RUNNING

vos[0:0]> shell
[Shell 0] Creating subshell...
[Spawn] Created process 1 (shell)

ps: [(0, 'RUNNING'), (1, 'READY')]
[Dispatch] Running PID=1 (shell)
[Shell 1] Started (depth=1)

vos[1:1]> ps
[ps_sys]
  pid=0 state=READY
  pid=1 state=RUNNING

vos[1:1]> shell
[Shell 1] Creating subshell...
[Spawn] Created process 2 (shell)

vos[2:2]> ps
[ps_sys]
  pid=0 state=READY
  pid=1 state=READY
  pid=2 state=RUNNING

vos[2:2]> exit
[Shell 2] Exiting (depth=2)

ps: [(0, 'READY'), (1, 'READY')]

vos[1:1]> exit
[Shell 1] Exiting (depth=1)

ps: [(0, 'READY')]

vos[0:0]> exit
[Shell 0] Exiting (depth=0)

[Kernel] All processes terminated. Halting.
```

## 💡 Características Importantes

### Shell Cooperativo
El shell NO usa `while True` bloqueante. En su lugar:
- Se ejecuta UN comando por cada `dispatch()` call
- Mantiene su estado en el PCB entre llamadas
- Permite que otros procesos (vmtest, idle) se ejecuten en round-robin
- Esto demuestra correctamente el concepto de time-slicing

### Procesos Terminan Automáticamente
- `vmtest` termina después de escribir en 5 páginas
- `idle` termina después de 6 ticks
- Los procesos TERMINATED desaparecen de `ps`

### Subshells con Profundidad
- Cada subshell incrementa la profundidad: 0 → 1 → 2 → ...
- El prompt muestra: `vos[PID:DEPTH]>`
- `exit` sale del nivel actual y regresa al anterior

## 📖 Documentación Adicional

- `LLM_prompts.md` - Prompts usados para generar código de Lab 1
- `LLM_prompts_lab2.md` - Prompts usados para Lab 2
- `LLM_prompts_Lab3.md` - Prompts usados para Lab 3
- `CORRECCIONES_LAB3.md` - Explicación detallada de correcciones realizadas
- `preguntas_argumentativas_Lab1.md` - Preguntas conceptuales Lab 1
- `preguntas_argumentativas_Lab2.md` - Preguntas conceptuales Lab 2

## 🎓 Conceptos de Sistemas Operativos Cubiertos

1. **Memoria Virtual**
   - Traducción de direcciones virtuales a físicas
   - Page tables y frames
   - Page faults y demand paging
   - Algoritmos de reemplazo (FIFO)
   - Dirty bit y write-back

2. **Gestión de Procesos**
   - Process Control Block (PCB)
   - Estados de procesos y transiciones
   - Context switching (implícito en dispatch)
   - Scheduling (Round-Robin)
   - Aislamiento de memoria por proceso

3. **System Calls**
   - Interfaz kernel-user space
   - Syscalls de procesos (ps, kill, spawn)
   - Syscalls de filesystem (ls, cd, touch, cat)
   - Syscalls de memoria (readvm, writevm)
   - Protección y validación

4. **Shell Interactivo**
   - Parser de comandos
   - Procesos cooperativos
   - Subshells y jerarquía
   - Mantenimiento de estado

## 🤖 Desarrollo con IA

Este proyecto fue desarrollado con ayuda de un LLM (Language Model), documentando los prompts usados en cada lab. Demuestra cómo usar IA efectivamente en proyectos educativos:

1. **Prompts específicos** con contexto claro
2. **Iteración** y refinamiento de respuestas
3. **Comprensión** profunda del código generado
4. **Modificación** y adaptación del código
5. **Documentación** del proceso

## 🎯 Características Extra Implementadas

Más allá de los requisitos básicos del Lab 3:

- ✅ **readvm/writevm syscalls**: Acceso a memoria de otros procesos para debugging
- ✅ **Sistema de profundidad**: Tracking de niveles de subshells
- ✅ **Prompt informativo**: `vos[PID:DEPTH]>` muestra contexto completo
- ✅ **Comando help**: Documentación integrada de todos los comandos
- ✅ **Shell cooperativo**: Demuestra correctamente time-slicing y scheduling
- ✅ **Manejo de errores**: Validación de argumentos y mensajes de error claros

## 📝 Licencia

Proyecto educativo - Sistemas Operativos

## 👨‍💻 Autor

Desarrollado como parte de los laboratorios de Sistemas Operativos.

---

**¿Preguntas?** Revisa la documentación en los archivos `.md` del proyecto.