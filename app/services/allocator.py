import time
from datetime import datetime
import heapq

from app.core.models import Slot, Token
from app.core.enums import TokenSource
from app.core import state


class TokenAllocator:
    def __init__(self):
        pass
    
    def _next_token_id(self) -> int:
        state.TOKEN_COUNTER += 1
        return state.TOKEN_COUNTER

    # this method creates a new token and stores it in the global state
    def create_token(
        self,
        patient_id: str,
        source: TokenSource,
        slot_id: str
    ) -> Token:
        token_id = self._next_token_id()

        token = Token(
            token_id=token_id,
            patient_id=patient_id,
            source=source,
            created_at=datetime.utcnow(),
            slot_id=slot_id
        )

        state.tokens[token_id] = token
        return token
    
    # method to allocate a token to a slot based on priority and capacity
    async def allocate(self, token: Token) -> None:
        slot = state.slots.get(token.slot_id)

        if not slot:
            raise ValueError("Invalid slot")
        
        async with slot.lock:
            timestamp = time.time()
            entry = (token.priority, timestamp, token.token_id)
            
            # case 1. slot has free capacity
            if len(slot.allocated) < slot.capacity:
                heapq.heappush(slot.allocated, entry)
                token.status = "allocated"
                return

            # case 2. slot full, try eviction
            lowest_priority, _, lowest_token_id = slot.allocated[0]

            if token.priority > lowest_priority:
                # this will evict lowest priority token
                heapq.heappop(slot.allocated)

                evicted_token = state.tokens[lowest_token_id]
                evicted_token.status = "waiting"

                heapq.heappush(
                    slot.waiting,
                    (-evicted_token.priority, timestamp, evicted_token.token_id)
                )

                heapq.heappush(slot.allocated, entry)
                token.status = "allocated"
                return

            # Case 3. cannot allocate, push to waiting queue
            heapq.heappush(
                slot.waiting,
                (-token.priority, timestamp, token.token_id)
            )
            token.status = "waiting"
    
    # cancellation habdling
    async def cancel_token(self, token_id: int) -> None:
        token = state.tokens.get(token_id)
        if not token:
            return

        slot: Slot | None = state.slots.get(token.slot_id)
        if not slot:
            return

        async with slot.lock:
            token.status = "cancelled"

            # remove from allocated heap if present
            slot.allocated = [
                entry for entry in slot.allocated
                if entry[2] != token_id
            ]
            heapq.heapify(slot.allocated)

            # promote from waiting queue if space frees up
            if slot.waiting and len(slot.allocated) < slot.capacity:
                _, _, next_token_id = heapq.heappop(slot.waiting)
                next_token = state.tokens[next_token_id]

                heapq.heappush(
                    slot.allocated,
                    (next_token.priority, time.time(), next_token_id)
                )
                next_token.status = "allocated"

    
    # emergency handling
    async def emergency_allocate(
        self,
        patient_id: str,
        slot_id: str
    ) -> Token:
        token = self.create_token(
            patient_id=patient_id,
            source=TokenSource.EMERGENCY,
            slot_id=slot_id
        )

        await self.allocate(token)
        return token            