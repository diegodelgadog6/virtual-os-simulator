# Argumentative Questions – Lab 2

## 1. Program vs Process
Un **programa** es un conjunto de instrucciones almacenadas en disco.  
Un **proceso** es la ejecución activa de ese programa, con su propio PCB y espacio de memoria.  
El PCB convierte un programa estático en una entidad dinámica con estado, CPU asignado y memoria virtual.

## 2. PCB Design
El PCB debe contener al menos `pid`, `state`, `vm`, y `prog` porque:
- `pid` identifica el proceso.
- `state` indica su estado actual.
- `vm` le da su propio espacio de memoria.
- `prog` define qué ejecuta.
Si faltara alguno, el kernel no podría administrar o aislar correctamente los procesos.

## 3. Per-Process Virtual Memory
Cada proceso necesita su propio VM para evitar interferencias.  
Si compartieran un solo VM, un proceso podría escribir en la memoria del otro, causando errores o violaciones de seguridad.  
Por ejemplo, un proceso que borre direcciones podría dañar datos de otro.
