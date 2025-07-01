from abc import ABC, abstractmethod
from typing import Tuple, List, Dict
from enum import Enum
from models.Card import Card


class HandRank(Enum):
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10


class BasePokerStrategy(ABC):
    def __init__(self):
        self.card_values = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
            '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
        }

    @abstractmethod
    def make_decision(self,
                      hand: List['Card'],
                      community_cards: List['Card'],
                      phase: str) -> str:
        pass

    def evaluate_hand_strength(self, hand: List['Card'], community_cards: List['Card']) -> float:
        """
        Evalúa la fuerza de la mano entre 0 y 1, usando una lógica especial para el preflop.
        """
        if len(community_cards) == 0:
            return self._evaluate_preflop_strength(hand)

        all_cards = hand + community_cards
        hand_rank = self._get_hand_rank(all_cards)
        base_score = hand_rank.value / len(HandRank)
        high_card_bonus = self._calculate_high_card_bonus(hand)
        return min(base_score + high_card_bonus, 1.0)

    def evaluate_preflop_strength(self, hand: List[Card]) -> float:
        """
        Evalúa la fuerza preflop de una mano con solo dos cartas.
        Devuelve un valor entre 0 (muy débil) y 1 (muy fuerte).
        
        Parámetros:
            - hand (List[Card]): las dos cartas del jugador.
        
        Retorna:
            - float: fuerza de la mano entre 0.0 y 1.0.
        """
        if len(hand) != 2:
            raise ValueError("Preflop solo debe evaluarse con 2 cartas.")

        value_map = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
            '7': 7, '8': 8, '9': 9, '10': 10,
            'J': 11, 'Q': 12, 'K': 13, 'A': 14
        }

        v1 = value_map[hand[0].value]
        v2 = value_map[hand[1].value]
        suited = hand[0].suit == hand[1].suit

        high_card = max(v1, v2)
        low_card = min(v1, v2)
        gap = high_card - low_card

        # Pares son muy fuertes
        if v1 == v2:
            if v1 >= 11:
                return 1.0  # par alto (JJ+)
            elif v1 >= 7:
                return 0.8  # par medio
            else:
                return 0.6  # par bajo

        # Conectadas del mismo palo (como KQ suited)
        if suited and gap == 1:
            return 0.75

        # As con carta decente
        if high_card == 14 and low_card >= 10:
            return 0.7 if suited else 0.6

        # Broadways (10, J, Q, K, A)
        if high_card >= 11 and low_card >= 10:
            return 0.65 if suited else 0.55

        # Suited medio
        if suited and high_card >= 10:
            return 0.55

        # Conectadas no suited
        if not suited and gap == 1:
            return 0.5

        # Totalmente disparejas y bajas
        return 0.3 if suited else 0.2


    def _get_hand_rank(self, cards: List['Card']) -> HandRank:
        if self._is_royal_flush(cards): return HandRank.ROYAL_FLUSH
        if self._is_straight_flush(cards): return HandRank.STRAIGHT_FLUSH
        if self._has_four_of_kind(cards): return HandRank.FOUR_OF_KIND
        if self._is_full_house(cards): return HandRank.FULL_HOUSE
        if self._is_flush(cards): return HandRank.FLUSH
        if self._is_straight(cards): return HandRank.STRAIGHT
        if self._has_three_of_kind(cards): return HandRank.THREE_OF_KIND
        if self._is_two_pair(cards): return HandRank.TWO_PAIR
        if self._is_pair(cards): return HandRank.PAIR
        return HandRank.HIGH_CARD

    def _calculate_high_card_bonus(self, hand: List['Card']) -> float:
        max_value = max(self.card_values[card.value] for card in hand)
        return (max_value - 2) / (14 - 2) * 0.1  # Máximo bonus 0.1

    # Helpers para detectar tipo de mano
    def _get_value_counts(self, cards: List['Card']) -> Dict[str, int]:
        counts = {}
        for card in cards:
            counts[card.value] = counts.get(card.value, 0) + 1
        return counts

    def _is_pair(self, cards): return 2 in self._get_value_counts(cards).values()
    def _is_two_pair(self, cards): return sum(1 for v in self._get_value_counts(cards).values() if v >= 2) >= 2
    def _has_three_of_kind(self, cards): return 3 in self._get_value_counts(cards).values()
    def _has_four_of_kind(self, cards): return 4 in self._get_value_counts(cards).values()
    def _is_full_house(self, cards): vc = self._get_value_counts(cards).values(); return 3 in vc and 2 in vc
    def _is_flush(self, cards): return any([cards.count(card) >= 5 for card in set([c.suit for c in cards])])
    def _is_straight(self, cards):
        if len(cards) < 5: return False
        values = sorted(set(self.card_values[card.value] for card in cards))
        return any(values[i + 4] - values[i] == 4 for i in range(len(values) - 4))
    def _is_straight_flush(self, cards): return self._is_straight(cards) and self._is_flush(cards)
    def _is_royal_flush(self, cards):
        return self._is_straight_flush(cards) and \
               max([self.card_values[card.value] for card in cards]) == 14
