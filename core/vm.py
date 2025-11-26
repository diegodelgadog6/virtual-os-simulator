# vm.py — Virtual Memory Simulation
from dataclasses import dataclass, field
from typing import Dict, Optional, List
from collections import deque

PAGE_SIZE = 256
VIRTUAL_PAGES = 16
PHYSICAL_FRAMES = 8

# === Data Structures ===

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

# === VM Class ===

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