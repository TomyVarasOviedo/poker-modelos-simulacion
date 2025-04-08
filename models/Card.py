from dataclasses import dataclass
from typing import Literal

SuitType = Literal['Hearts', 'Diamonds', 'Clubs', 'Spades']
ValueType = Literal['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
    
    def __str__(self):
        return f"{self.value} of {self.suit}"
    
    def __eq__(self, other):
        if isinstance(other, Card):
            return self.suit == other.suit and self.value == self.value
        return False