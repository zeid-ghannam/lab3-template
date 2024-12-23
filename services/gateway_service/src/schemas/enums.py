from enum import Enum


class ReservationStatus(str, Enum):
    PAID = "PAID"
    RESERVED = "RESERVED"
    CANCELED = "CANCELED"


class PaymentStatus(str, Enum):
    PAID = "PAID"
    REVERSED = "REVERSED"
    CANCELED = "CANCELED"


class LoyaltyStatus(str, Enum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
