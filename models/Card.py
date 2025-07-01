from typing import Literal

SuitType = Literal['Hearts', 'Diamonds', 'Clubs', 'Spades']
ValueType = Literal['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

class Card:
    def __init__(self, suit: SuitType, value: ValueType):
        if suit not in ['Hearts', 'Diamonds', 'Clubs', 'Spades']:
            raise ValueError(f"Invalid suit: {suit}")
        if value not in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']:
            raise ValueError(f"Invalid value: {value}")
        self.suit = suit
        self.value = value

    def __str__(self):
        return f"{self.value} of {self.suit}"

    def __repr__(self):
        suit_symbols = {
            'Hearts': '♥',
            'Diamonds': '♦',
            'Clubs': '♣',
            'Spades': '♠'
        }
        return f"{self.value}{suit_symbols[self.suit]}"

    def __eq__(self, other):
        return isinstance(other, Card) and self.suit == other.suit and self.value == other.value

    def __hash__(self):
        return hash((self.suit, self.value))  # útil si usás sets o dicts con cartas
