# Argumentative Questions

## 1. Page Fault Handling
Un *page fault* ocurre cuando una página no está en la RAM.  
El sistema o simulador detiene la ejecución, carga la página desde el disco al primer marco libre, actualiza la tabla de páginas y reanuda el proceso.

## 2. Dirty Bit
El *dirty bit* marca una página modificada.  
Si se reemplaza una página sucia sin escribirla al disco, los datos se pierden.  
Por eso, antes de eliminarla, debe guardarse en el *backing store*.

## 3. FIFO Replacement
**Ventaja:** Es sencillo y rápido de implementar.  
**Desventaja:** Puede eliminar páginas que todavía se usan, causando más fallos de página (anomalía de Belady).

## 4. Isolation
La memoria virtual le da a cada proceso su propio espacio de direcciones.  
Así evita que un proceso lea o modifique la memoria de otro, garantizando aislamiento y seguridad.
