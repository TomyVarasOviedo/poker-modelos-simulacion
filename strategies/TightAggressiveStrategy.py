from strategies.BasePokerStrategy import BasePokerStrategy
from models.Card import Card
from typing import List
import random

class TightAggressiveStrategy(BasePokerStrategy):
    def make_decision(self, hand: List[Card], community_cards: List[Card], phase: str) -> str:
        strength = 0.0

        if phase == "preflop":
            strength = self.evaluate_preflop_strength(hand)
        else:
            strength = self.evaluate_hand_strength(hand, community_cards)

        thresholds = {
            "preflop": 0.6,   # Muy selectivo al entrar
            "flop": 0.55,     # Menos selectivo: si entró, probablemente tenga algo fuerte
            "turn": 0.48,      # Aún menos: sigue presionando si tiene algo decente
            "river": 0.43     # Si llegó hasta aquí, es porque va all-in mentalmente
        }

        # Aumentar presión con manos sólidas
        if strength >= thresholds[phase]:
            return "raise"

        return "fold"