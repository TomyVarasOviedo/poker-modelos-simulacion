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
            "preflop": 0.7,   # Muy selectivo al entrar
            "flop": 0.5,     # Menos selectivo: si entró, probablemente tenga algo fuerte
            "turn": 0.45,      # Aún menos: sigue presionando si tiene algo decente
            "river": 0.4     # Si llegó hasta aquí, es porque va all-in mentalmente
        }

        # Si la mano es débil, se retira
        if strength < thresholds[phase]:
            return "fold"

        # Raise garantizado con mano muy fuerte
        if strength >= 0.85:
            return "raise"

        # Aumentar presión en turn o river con manos sólidas
        if strength >= thresholds[phase] and phase in ["turn", "river"]:
            return "raise"

        # Opcional: raise ocasional en el flop si supera 0.7 (comportamiento semi-agresivo)
        if phase == "flop" and strength > 0.7 and random.random() < 0.3:
            return "raise"

        return "call"
