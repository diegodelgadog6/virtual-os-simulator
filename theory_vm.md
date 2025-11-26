# Virtual Memory – From Concept to Simulation

## 1. Virtual vs. Physical Memory
La **memoria física** es la RAM real instalada en el sistema, mientras que la **memoria virtual** es una abstracción que permite a cada proceso creer que tiene su propio espacio de direcciones continuo, aunque internamente esté dividido y parcialmente almacenado en disco.  
El sistema operativo traduce las direcciones virtuales en direcciones físicas mediante estructuras llamadas **tablas de páginas**.

## 2. Paging and Page Tables
La memoria virtual se divide en bloques fijos llamados **páginas**, y la RAM en **frames** (marcos).  
Cada entrada en la **tabla de páginas** indica si una página está presente en memoria y, si lo está, en qué marco físico.  
Esta relación se mantiene mediante un número de página y un desplazamiento (*offset*), que juntos forman la dirección virtual.

## 3. Page Fault Handling
Un **page fault** ocurre cuando un proceso intenta acceder a una página que no está cargada en la RAM.  
El sistema operativo interrumpe la ejecución, busca la página en el disco (*backing store*), la carga en un marco libre o reemplaza otra si no hay espacio, actualiza la tabla de páginas y continúa la ejecución.

## 4. Backing Store and Dirty Bit
El **backing store** es la copia secundaria (generalmente en disco) de las páginas que no están en RAM.  
El **dirty bit** (bit sucio) marca las páginas que han sido modificadas; si una página sucia se reemplaza, primero debe escribirse al disco para no perder los cambios.

## 5. FIFO Page Replacement
El algoritmo **FIFO (First-In, First-Out)** reemplaza la página que lleva más tiempo cargada en memoria.  
Es simple de implementar, aunque puede provocar la **anomalía de Belady**, donde aumentar la memoria puede generar más fallos de página.

## 6. Address Translation
La CPU genera direcciones virtuales que se dividen en dos partes:
- **Número de página (page number)**: indica qué página virtual se necesita.  
- **Desplazamiento (offset)**: la posición exacta dentro de esa página.  

La tabla de páginas traduce el número de página a un número de marco físico y el offset se mantiene igual.

## 7. Process Isolation
Cada proceso tiene su propia tabla de páginas, lo que garantiza que uno no pueda acceder a la memoria de otro.  
Esto evita errores y vulnerabilidades de seguridad, proporcionando **aislamiento entre procesos**.

## 8. Connection to Software Simulation
En esta simulación con Python, reproducimos los mecanismos principales:
- Paginación mediante clases (`PTEntry`, `PageTable`, `PhysicalMemory`).
- Manejo de fallos de página en `_ensure_in_ram`.
- Reemplazo FIFO con una cola.
- Simulación de escrituras al disco cuando la página está sucia.

Esta práctica demuestra cómo el sistema operativo gestiona la memoria detrás de escena, brindando estabilidad y seguridad a los programas.