from dataclasses import dataclass, field
from datetime import datetime
import asyncio
from typing import List, Tuple

from .enums import TokenSource, PRIORITY_WEIGHT


@dataclass
class Token:
    token_id: int
    patient_id: str
    source: TokenSource
    created_at: datetime
    slot_id: str
    status: str = "waiting"

    @property
    def priority(self) -> int:
        return PRIORITY_WEIGHT[self.source]


@dataclass
class Slot:
    slot_id: str
    doctor_id: str
    start_time: str
    end_time: str
    capacity: int

    allocated: List[Tuple[int, float, int]] = field(default_factory=list)
    waiting: List[Tuple[int, float, int]] = field(default_factory=list)

    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
