from strategies.BasePokerStrategy import BasePokerStrategy
from models.Card import Card
from typing import List
import random

class BluffingStrategy(BasePokerStrategy):
    def make_decision(self, hand: List[Card], community_cards: List[Card], phase: str) -> str:
        strength = 0.0
        
        if phase == "preflop":
            strength = self.evaluate_preflop_strength(hand)
        else:
            strength = self.evaluate_hand_strength(hand, community_cards)

        thresholds = {
            "preflop": 0.35,
            "flop": 0.45,
            "turn": 0.5,
            "river": 0.55,
        }

        bluff_chances = {
            "preflop": 0.15,
            "flop": 0.2,
            "turn": 0.25,
            "river": 0.3,
        }

        # Raise por fuerza real
        if strength >= 0.85:
            return "raise"

        # Bluff si no alcanza el threshold
        if strength < thresholds[phase] and random.random() < bluff_chances[phase]:
            return "raise"

        return "call" if strength >= thresholds[phase] else "fold"
