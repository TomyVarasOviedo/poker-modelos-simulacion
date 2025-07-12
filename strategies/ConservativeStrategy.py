from strategies.BasePokerStrategy import BasePokerStrategy
from models.Card import Card
from typing import List

class ConservativeStrategy(BasePokerStrategy):
    def make_decision(self, hand: List[Card], community_cards: List[Card], phase: str) -> str:
        strength = 0.0

        if phase == "preflop":
            strength = self.evaluate_preflop_strength(hand)
        else:
            strength = self.evaluate_hand_strength(hand, community_cards)

        thresholds = {
            "preflop": 0.65,  
            "flop": 0.55,     
            "turn": 0.6,      
            "river": 0.65     
        }

        # Raise solo si tiene una mano MUY fuerte
        if strength >= 0.85:
            return "raise"
        elif strength >= thresholds[phase]:
            return "call"
        else:
            return "fold"
