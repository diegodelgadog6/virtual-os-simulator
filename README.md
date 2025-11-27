# 🖥️ VOS - Virtual Operating System

Un simulador educativo de sistema operativo implementado en Python que incluye memoria virtual, gestión de procesos, scheduling y un shell interactivo.

## 📚 Laboratorios Completados

- ✅ **Lab 1**: Memoria Virtual con paginación y reemplazo FIFO
- ✅ **Lab 2**: Gestión de Procesos y Scheduling
- ✅ **Lab 3**: System Calls y Shell Interactivo

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
vos[0:0]> ps              # Listar procesos
vos[0:0]> vmtest          # Crear proceso de prueba de memoria
vos[0:0]> idle            # Crear proceso idle
vos[0:0]> kill 1          # Terminar proceso con PID 1
```

### Comandos de Filesystem
```bash
vos[0:0]> ls              # Listar directorio actual
vos[0:0]> ls core         # Listar subdirectorio
vos[0:0]> cd core         # Cambiar directorio
vos[0:0]> pwd             # Mostrar directorio actual
vos[0:0]> touch test.txt  # Crear archivo
vos[0:0]> cat test.txt    # Mostrar contenido
```

### Comandos de Shell
```bash
vos[0:0]> shell           # Crear subshell
vos[1:1]> ps              # Ver procesos desde subshell
vos[1:1]> exit            # Salir de subshell
vos[0:0]> exit            # Salir del shell raíz (termina VOS)
```

### Otros Comandos
```bash
vos[0:0]> help            # Mostrar ayuda
```

## 🏗️ Arquitectura

```
VOS
├── Kernel (sys.py)
│   ├── Scheduler (Round-Robin)
│   ├── Process Table
│   └── System Calls
│
├── Memoria Virtual (vm.py)
│   ├── Page Table
│   ├── Physical Memory (8 frames)
│   ├── Virtual Memory (16 pages)
│   └── FIFO Replacement
│
└── Procesos
    ├── PCB (Process Control Block)
    ├── Estados: NEW, READY, RUNNING, TERMINATED
    └── Memoria virtual por proceso
```

## 📁 Estructura del Proyecto

```
vos/
├── vos.py                      # Punto de entrada principal
├── core/
│   ├── __init__.py             # Paquete core
│   ├── vm.py                   # Memoria virtual
│   ├── process.py              # PCB y estados
│   ├── sched.py                # Scheduler Round-Robin
│   ├── sys.py                  # Kernel y syscalls
│   └── demo_tasks.py           # Programas de ejemplo y shell
├── LLM_prompts.md              # Prompts Lab 1
├── LLM_prompts_lab2.md         # Prompts Lab 2
├── CORRECCIONES_LAB3.md        # Documentación de correcciones
└── README.md                   # Este archivo
```

## 🔬 Conceptos Implementados

### Memoria Virtual (Lab 1)
- **Paginación**: 16 páginas virtuales, 8 frames físicos, 256 bytes/página
- **Page Table**: Mapeo de páginas virtuales a frames físicos
- **Page Faults**: Manejo automático cuando página no está en RAM
- **FIFO Replacement**: Algoritmo de reemplazo de páginas
- **Dirty Bit**: Marca páginas modificadas para write-back

### Gestión de Procesos (Lab 2)
- **PCB**: Process Control Block con pid, estado, VM, programa
- **Estados**: NEW → READY → RUNNING → TERMINATED
- **Scheduling**: Round-Robin simple
- **Aislamiento**: Cada proceso tiene su propia memoria virtual

### System Calls (Lab 3)
- **Procesos**: `ps`, `kill`, `spawn`
- **Memoria**: `read_vm`, `write_vm`
- **Filesystem**: `ls`, `cd`, `pwd`, `touch`, `cat`

### Shell Interactivo (Lab 3)
- Shell como proceso (PID 0 es el shell raíz)
- Subshells anidados con comando `shell`
- Stack de shells con `exit` para volver al anterior
- Parser simple de comandos

## 🧪 Ejemplos de Uso

### Ejemplo 1: Crear y Listar Procesos
```bash
$ python vos.py

vos[0:0]> ps
[ps_sys]
  pid=0 state=READY

vos[0:0]> vmtest
[Spawn] Created process 1 (vmtest)

vos[0:0]> idle
[Spawn] Created process 2 (idle)

vos[0:0]> ps
[ps_sys]
  pid=0 state=READY
  pid=1 state=READY
  pid=2 state=READY

vos[0:0]> exit
```

### Ejemplo 2: Trabajar con Archivos
```bash
vos[0:0]> touch mi_archivo.txt
[touch_sys] created /home/user/vos/mi_archivo.txt

vos[0:0]> ls
[ls_sys] /home/user/vos:
  mi_archivo.txt
  core
  vos.py
  ...

vos[0:0]> cat mi_archivo.txt
[cat_sys] /home/user/vos/mi_archivo.txt:

```

### Ejemplo 3: Subshells Anidados
```bash
vos[0:0]> shell
[Shell 0] Creating subshell...
[Spawn] Created process 1 (shell)
[Shell 1] Started (depth=1)

vos[1:1]> shell
[Shell 1] Creating subshell...
[Spawn] Created process 2 (shell)
[Shell 2] Started (depth=2)

vos[2:2]> ps
[ps_sys]
  pid=0 state=READY
  pid=1 state=READY
  pid=2 state=READY

vos[2:2]> exit
[Shell 2] Exiting subshell (depth=2)
[Shell 1] Subshell 2 exited, returning to shell 1

vos[1:1]> exit
[Shell 1] Exiting subshell (depth=1)
[Shell 0] Subshell 1 exited, returning to shell 0

vos[0:0]> exit
[Shell 0] Exiting root shell
```

## 🐛 Problemas Conocidos y Soluciones

### ⚠️ Los procesos vmtest/idle no se ejecutan
**Comportamiento**: Cuando haces `vmtest` o `idle`, el proceso se crea pero no se ejecuta.

**Razón**: El shell actual es bloqueante y no cede control al scheduler.

**Esto es normal**: Según las instrucciones de Lab 3, el shell puede ser bloqueante. Los procesos quedan en estado READY esperando.

**Solución futura**: Implementar un shell cooperativo que ceda control periódicamente.

### ⚠️ No se puede matar el proceso shell actual
**Comportamiento**: `kill 0` mientras estás en PID 0 te deja sin shell.

**Razón**: Matas el proceso actual que está ejecutando el comando.

**Solución**: No mates el shell en el que estás. Usa subshells si necesitas experimentar.

## 📖 Documentación Adicional

- `LLM_prompts.md` - Prompts usados para generar código de Lab 1
- `LLM_prompts_lab2.md` - Prompts usados para Lab 2
- `CORRECCIONES_LAB3.md` - Explicación detallada de correcciones realizadas
- `preguntas_argumentativas_Lab1.md` - Preguntas conceptuales Lab 1
- `preguntas_argumentativas_Lab2.md` - Preguntas conceptuales Lab 2

## 🎓 Conceptos de Sistemas Operativos Cubiertos

1. **Memoria Virtual**
   - Traducción de direcciones virtuales a físicas
   - Page tables y frames
   - Page faults y demand paging
   - Algoritmos de reemplazo (FIFO)

2. **Gestión de Procesos**
   - Process Control Block (PCB)
   - Estados de procesos
   - Context switching
   - Scheduling (Round-Robin)

3. **System Calls**
   - Interfaz kernel-user
   - Syscalls de procesos
   - Syscalls de filesystem
   - Aislamiento y protección

4. **Shell**
   - Parser de comandos
   - Procesos interactivos
   - Subshells y jerarquía de procesos

## 🤝 Desarrollo con IA

Este proyecto fue desarrollado con ayuda de un LLM (Language Model), documentando los prompts usados en cada lab. Es un ejemplo de cómo usar IA efectivamente en proyectos educativos:

1. **Prompts específicos y bien estructurados**
2. **Iteración y refinamiento**
3. **Comprensión de las respuestas generadas**
4. **Modificación y adaptación del código**

## 📝 Licencia

Proyecto educativo - Sistemas Operativos

## 👨‍💻 Autor

Desarrollado como parte de los laboratorios de Sistemas Operativos.

---

**¿Preguntas?** Revisa la documentación en los archivos `.md` del proyecto.
