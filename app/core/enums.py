from enum import Enum

class TokenSource(str, Enum):
    EMERGENCY = "emergency"
    PAID = "paid"
    FOLLOWUP = "followup"
    ONLINE = "online"
    WALKIN = "walkin"

PRIORITY_WEIGHT = {
    TokenSource.EMERGENCY: 100,
    TokenSource.PAID: 80,
    TokenSource.FOLLOWUP: 60,
    TokenSource.ONLINE: 40,
    TokenSource.WALKIN: 20,
}
