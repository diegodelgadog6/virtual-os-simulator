## 🧩 Prompt 1 — Data Structures

**Prompt enviado:**

Diseña las clases necesarias para una simulación de memoria virtual en Python:

- Usa `@dataclass` para simplificar el código.
- Crea las clases `PTEntry`, `PageTable`, y `PhysicalMemory`.

Usa las siguientes constantes:
  PAGE_SIZE = 256
  VIRTUAL_PAGES = 16
  PHYSICAL_FRAMES = 8

- `PTEntry` debe tener: `frame`, `present`, `dirty`.
- `PageTable` debe mapear páginas → entradas (`PTEntry`).
- `PhysicalMemory` debe mapear frames → `bytearray` (de tamaño `PAGE_SIZE`) y tener una lista de frames libres.
- Explica brevemente por qué existe cada clase y atributo.

**Respuesta generada:**

```python
from dataclasses import dataclass, field
from typing import Dict, Optional, List

PAGE_SIZE = 256
VIRTUAL_PAGES = 16
PHYSICAL_FRAMES = 8

@dataclass
class PTEntry:
    frame: Optional[int] = None
    present: bool = False
    dirty: bool = False

@dataclass
class PageTable:
    entries: Dict[int, PTEntry] = field(default_factory=lambda: {
        i: PTEntry() for i in range(VIRTUAL_PAGES)
    })

@dataclass
class PhysicalMemory:
    frames: Dict[int, bytearray] = field(default_factory=lambda: {
        i: bytearray(PAGE_SIZE) for i in range(PHYSICAL_FRAMES)
    })
    free_frames: List[int] = field(default_factory=lambda: list(range(PHYSICAL_FRAMES)))
```

**Explicación:**
Estas clases forman la base de la simulación de memoria virtual. `PTEntry` guarda el estado de cada página, `PageTable` las agrupa en una estructura de traducción, y `PhysicalMemory` modela los marcos de memoria física.

---

## ⚙️ Prompt 2 — Page Fault + FIFO Replacement

**Prompt enviado:**

Implementa en la clase VM un método llamado _ensure_in_ram(page_no) que:

- Verifique si la página está presente en RAM.

- Si no está, maneje un page fault.

- Use una cola FIFO para decidir qué frame liberar si la RAM está llena.

- Si la página que sale está sucia (dirty=True), simula un “escritura en backing store”.

- Mantén un mapeo inverso frame → página.


**Respuesta generada:**

```python
from collections import deque

class VM:
    def __init__(self):
        self.page_table = PageTable()
        self.physical_memory = PhysicalMemory()
        self.frame_to_page = {}
        self.fifo_queue = deque()

    def _ensure_in_ram(self, page_no: int):
        entry = self.page_table.entries[page_no]

        if entry.present:
            return entry.frame

        print(f"[Page Fault] Page {page_no} not in RAM")

        if self.physical_memory.free_frames:
            frame = self.physical_memory.free_frames.pop(0)
        else:
            old_frame = self.fifo_queue.popleft()
            old_page = self.frame_to_page.pop(old_frame)
            old_entry = self.page_table.entries[old_page]

            if old_entry.dirty:
                print(f"[Write Back] Page {old_page} written to disk (dirty)")

            old_entry.present = False
            old_entry.frame = None
            frame = old_frame

        self.page_table.entries[page_no].frame = frame
        self.page_table.entries[page_no].present = True
        self.page_table.entries[page_no].dirty = False
        self.frame_to_page[frame] = page_no
        self.fifo_queue.append(frame)

        print(f"[Load] Page {page_no} -> Frame {frame}")
        return frame
```

**Explicación:**
El método verifica si una página está en RAM; si no, maneja el fallo, carga la página al marco disponible o reemplaza la más antigua con FIFO.

---

## 💾 Prompt 3 — Read, Write, Zero Page

**Prompt enviado:**

Implementa los métodos read_byte(vaddr), write_byte(vaddr, value) y zero_page(page_no) para el sistema de memoria virtual.

- Usa las constantes PAGE_SIZE, VIRTUAL_PAGES.

- Calcula la página y el offset a partir de la dirección virtual.

- Si la página no está presente, llama a _ensure_in_ram.

- Marca la página como sucia al escribir.

- zero_page debe poner todos los bytes de una página en cero.

**Respuesta generada:**

```python
class VM(VM):
    def read_byte(self, vaddr: int) -> int:
        page_no = vaddr // PAGE_SIZE
        offset = vaddr % PAGE_SIZE
        frame = self._ensure_in_ram(page_no)
        value = self.physical_memory.frames[frame][offset]
        print(f"[Read] vaddr={vaddr} (page={page_no}, offset={offset}) -> {value}")
        return value

    def write_byte(self, vaddr: int, value: int):
        page_no = vaddr // PAGE_SIZE
        offset = vaddr % PAGE_SIZE
        frame = self._ensure_in_ram(page_no)
        self.physical_memory.frames[frame][offset] = value
        self.page_table.entries[page_no].dirty = True
        print(f"[Write] vaddr={vaddr} (page={page_no}, offset={offset}) = {value}")

    def zero_page(self, page_no: int):
        frame = self._ensure_in_ram(page_no)
        self.physical_memory.frames[frame] = bytearray(PAGE_SIZE)
        self.page_table.entries[page_no].dirty = False
        print(f"[Zero] Page {page_no} cleared in Frame {frame}")
```

**Explicación:**
Estos métodos realizan operaciones sobre direcciones virtuales simulando traducción, escritura y limpieza de datos.

---

## 🧠 Prompt 4 — Final Assembly (`vm.py` completo)

**Prompt enviado:**

Combina todos los fragmentos anteriores en un único archivo vm.py funcional.

- Incluye todas las clases: PTEntry, PageTable, PhysicalMemory, VM.

- Usa las constantes dadas.

- Asegúrate de que sea autocontenido y pueda importarse desde run_vos.py.

**Respuesta generada:**

```python
from dataclasses import dataclass, field
from typing import Dict, Optional, List
from collections import deque

PAGE_SIZE = 256
VIRTUAL_PAGES = 16
PHYSICAL_FRAMES = 8

@dataclass
class PTEntry:
    frame: Optional[int] = None
    present: bool = False
    dirty: bool = False

@dataclass
class PageTable:
    entries: Dict[int, PTEntry] = field(default_factory=lambda: {
        i: PTEntry() for i in range(VIRTUAL_PAGES)
    })

@dataclass
class PhysicalMemory:
    frames: Dict[int, bytearray] = field(default_factory=lambda: {
        i: bytearray(PAGE_SIZE) for i in range(PHYSICAL_FRAMES)
    })
    free_frames: List[int] = field(default_factory=lambda: list(range(PHYSICAL_FRAMES)))

class VM:
    def __init__(self):
        self.page_table = PageTable()
        self.physical_memory = PhysicalMemory()
        self.frame_to_page = {}
        self.fifo_queue = deque()

    def _ensure_in_ram(self, page_no: int):
        entry = self.page_table.entries[page_no]
        if entry.present:
            return entry.frame
        print(f"[Page Fault] Page {page_no} not in RAM")
        if self.physical_memory.free_frames:
            frame = self.physical_memory.free_frames.pop(0)
        else:
            old_frame = self.fifo_queue.popleft()
            old_page = self.frame_to_page.pop(old_frame)
            old_entry = self.page_table.entries[old_page]
            if old_entry.dirty:
                print(f"[Write Back] Page {old_page} written to disk (dirty)")
            old_entry.present = False
            old_entry.frame = None
            frame = old_frame
        self.page_table.entries[page_no].frame = frame
        self.page_table.entries[page_no].present = True
        self.page_table.entries[page_no].dirty = False
        self.frame_to_page[frame] = page_no
        self.fifo_queue.append(frame)
        print(f"[Load] Page {page_no} -> Frame {frame}")
        return frame

    def read_byte(self, vaddr: int) -> int:
        page_no = vaddr // PAGE_SIZE
        offset = vaddr % PAGE_SIZE
        frame = self._ensure_in_ram(page_no)
        value = self.physical_memory.frames[frame][offset]
        print(f"[Read] vaddr={vaddr} (page={page_no}, offset={offset}) -> {value}")
        return value

    def write_byte(self, vaddr: int, value: int):
        page_no = vaddr // PAGE_SIZE
        offset = vaddr % PAGE_SIZE
        frame = self._ensure_in_ram(page_no)
        self.physical_memory.frames[frame][offset] = value
        self.page_table.entries[page_no].dirty = True
        print(f"[Write] vaddr={vaddr} (page={page_no}, offset={offset}) = {value}")

    def zero_page(self, page_no: int):
        frame = self._ensure_in_ram(page_no)
        self.physical_memory.frames[frame] = bytearray(PAGE_SIZE)
        self.page_table.entries[page_no].dirty = False
        print(f"[Zero] Page {page_no} cleared in Frame {frame}")
```

**Explicación:**
Este archivo integra toda la funcionalidad de la simulación de memoria virtual, incluyendo manejo de páginas, lectura, escritura, reemplazo FIFO y control del bit sucio.
