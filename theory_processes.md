# Processes and Round-Robin Scheduling – From Concept to Python Simulation

## 1. Program vs Process vs Thread
Un **programa** es un conjunto de instrucciones almacenadas (estático).  
Un **proceso** es una instancia en ejecución de un programa (dinámico).  
Un **hilo (thread)** es la unidad mínima de ejecución dentro de un proceso; varios hilos pueden compartir el mismo espacio de memoria.

---

## 2. Process Control Block (PCB)
El **PCB** es una estructura de datos que guarda toda la información necesaria para administrar un proceso:

| Campo | Descripción |
|--------|--------------|
| `pid` | Identificador único del proceso |
| `state` | Estado actual (NEW, READY, RUNNING, WAITING, TERMINATED) |
| `program_counter` | Instrucción actual que ejecuta el proceso |
| `registers` | Valores de los registros de CPU |
| `vm` | Espacio de memoria virtual asignado al proceso |
| `prog` | Código o función que ejecuta el proceso |
| `cpu_time` | Tiempo de CPU utilizado |

---

## 3. Estados de proceso
Los estados básicos son:

- **NEW:** creado, no ha comenzado a ejecutarse.
- **READY:** esperando turno para usar CPU.
- **RUNNING:** actualmente ejecutándose.
- **WAITING:** bloqueado, esperando algún evento.
- **TERMINATED:** finalizado.

Las transiciones dependen del scheduler (ejemplo: READY → RUNNING → WAITING → READY → TERMINATED).

---

## 4. CPU Scheduling: objetivos
Los algoritmos de planificación buscan:
- **Utilización alta del CPU**
- **Equidad (fairness)**
- **Bajo tiempo de respuesta**
- **Alto rendimiento (throughput)**

---

## 5. Round-Robin (RR) Scheduling
- Asigna la CPU por turnos fijos (time quantum).
- Usa una **cola circular (ready queue)**.
- Cuando el tiempo de un proceso expira, se coloca al final de la cola.
- Simple, justo y predecible.

**Pseudocódigo básico:**

while queue not empty:
    p = queue.pop(0)
    run(p, quantum)

    if p.state == RUNNING:
        queue.append(p)


---

## 6. Per-Process Virtual Memory
Cada proceso debe tener su **propia instancia de VM**, para evitar interferencias.  
Así, si un proceso escribe en su memoria, no afecta a otro.

Ejemplo:
- Proceso 1 escribe en dirección virtual 1000.
- Proceso 2 también puede tener una dirección 1000, pero apuntará a otra región física distinta.

---

## 7. Relación entre PCB, Scheduler y VM
El **scheduler** selecciona qué proceso ejecutar.  
El **kernel** usa el **PCB** para guardar el estado de cada proceso.  
El **VM** garantiza aislamiento entre ellos.  
Todo esto permite ejecutar múltiples programas “a la vez” de manera segura.

---

**Referencias:**
- Silberschatz, Galvin, Gagne — *Operating System Concepts*, 10th ed.
- Tanenbaum & Bos — *Modern Operating Systems*, 4th ed.