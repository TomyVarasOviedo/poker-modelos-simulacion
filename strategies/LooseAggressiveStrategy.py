from strategies.BasePokerStrategy import BasePokerStrategy
from models.Card import Card
from typing import List
import random

class LooseAggressiveStrategy(BasePokerStrategy):
    def make_decision(self, hand: List[Card], community_cards: List[Card], phase: str) -> str:
        if phase == "preflop":
            strength = self.evaluate_preflop_strength(hand)
            if strength >= 0.6:
                return "raise"
            elif strength >= 0.35:
                return "call"
            elif random.random() < 0.15:
                return "raise"  # Bluff preflop ocasional
            else:
                return "fold"

        strength = self.evaluate_hand_strength(hand, community_cards)

        thresholds = {
            "flop": 0.35,
            "turn": 0.45,
            "river": 0.5
        }

        bluff_chances = {
            "flop": 0.2,
            "turn": 0.25,
            "river": 0.3
        }

        threshold = thresholds.get(phase, 0.5)
        bluff_probability = bluff_chances.get(phase, 0.0)

        if strength >= threshold:
            return "raise"
        if random.random() < bluff_probability:
            return "raise"
        
        return "fold"
