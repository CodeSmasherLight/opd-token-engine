from typing import Dict
from .models import Slot, Token

slots: Dict[str, Slot] = {}
tokens: Dict[int, Token] = {}

TOKEN_COUNTER = 0
