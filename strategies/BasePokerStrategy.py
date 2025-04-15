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
                      pot_size: int,
                      current_bet: int,
                      player_stack: int) -> Tuple[str, int]:
        """
        Abstract method to implements the each strategy

        Args:
            hand [List{Card}]: cards that are being played
            community_cards [List{Card}]:
            pot_size [int]:
            current_bet [int]:
            player_stack [int]:
        Returns:
            Tuple [str, int]: (action, amount)
            action: 'fold', 'call', or 'raise'
            amount: bet amount if raising
        """
        pass

    def evaluate_hand_strength(self, hand: List['Card'], community_cards: List['Card']) -> float:
        """
        Evaluates hand strength on a scale of 0 to 1

        Args:
            hand [List{Card}]:
            community_cards [List{Card}]:

        Returns:
            strength [float]: between 0 (weakest) and 1 (strongest)
        """
        all_cards = hand + community_cards
        hand_rank = self._get_hand_rank(all_cards)

        # Base score from hand rank
        base_score = hand_rank.value / len(HandRank)

        # Adjust for high cards
        high_card_bonus = self._calculate_high_card_bonus(hand)

        return min(base_score + high_card_bonus, 1.0)

    def _get_hand_rank(self, cards: List['Card']) -> HandRank:
        """
        Method to calculate points of hand 

        Args:
            cards [List{Card}]:

        Returns:
            handRank [HandRank]: points of hand according to its cards
        """
        if self._is_royal_flush(cards):
            return HandRank.ROYAL_FLUSH
        if self._is_straight_flush(cards):
            return HandRank.STRAIGHT_FLUSH
        if self._has_four_of_kind(cards):
            return HandRank.FOUR_OF_KIND
        if self._is_full_house(cards):
            return HandRank.FULL_HOUSE
        if self._is_flush(cards):
            return HandRank.FLUSH
        if self._is_straight(cards):
            return HandRank.STRAIGHT
        if self._has_three_of_kind(cards):
            return HandRank.THREE_OF_KIND
        if self._is_two_pair(cards):
            return HandRank.TWO_PAIR
        if self._is_pair(cards):
            return HandRank.PAIR
        return HandRank.HIGH_CARD

    def _calculate_pot_odds(self, pot_size: int, current_bet: int) -> float:
        """Calculate pot odds as a percentage"""
        if current_bet == 0:
            return 0.0
        return current_bet / (pot_size + current_bet)

    def _calculate_implied_odds(self, pot_size: int, player_stack: int) -> float:
        """Calculate implied odds based on pot size and remaining stack"""
        return (pot_size + player_stack) / pot_size if pot_size > 0 else 0.0

    def _calculate_high_card_bonus(self, hand: List['Card']) -> float:
        """Calculate bonus for high cards in hand"""
        max_value = max(self.card_values[card.value] for card in hand)
        return (max_value - 2) / (14 - 2) * 0.1  # 0.1 is the maximum bonus

    # Helper methods for hand evaluation
    def _is_royal_flush(self, cards: List['Card']) -> bool:
        if len(cards) < 5:
            return False
        if not self._is_straight_flush(cards):
            return False
        values = [self.card_values[card.value] for card in cards]
        return max(values) == 14  # Ace high

    def _is_straight_flush(self, cards: List['Card']) -> bool:
        return self._is_straight(cards) and self._is_flush(cards)

    def _has_four_of_kind(self, cards: List['Card']) -> bool:
        value_counts = self._get_value_counts(cards)
        return 4 in value_counts.values()

    def _is_full_house(self, cards: List['Card']) -> bool:
        value_counts = self._get_value_counts(cards)
        return 3 in value_counts.values() and 2 in value_counts.values()

    def _is_flush(self, cards: List['Card']) -> bool:
        if len(cards) < 5:
            return False
        suits = [card.suit for card in cards]
        return any(suits.count(suit) >= 5 for suit in set(suits))

    def _is_straight(self, cards: List['Card']) -> bool:
        if len(cards) < 5:
            return False
        values = sorted(set(self.card_values[card.value] for card in cards))
        for i in range(len(values) - 4):
            if values[i+4] - values[i] == 4:
                return True
        return False

    def _has_three_of_kind(self, cards: List['Card']) -> bool:
        value_counts = self._get_value_counts(cards)
        return 3 in value_counts.values()

    def _is_two_pair(self, cards: List['Card']) -> bool:
        value_counts = self._get_value_counts(cards)
        pairs = sum(1 for count in value_counts.values() if count >= 2)
        return pairs >= 2

    def _is_pair(self, cards: List['Card']) -> bool:
        value_counts = self._get_value_counts(cards)
        return 2 in value_counts.values()

    def _get_value_counts(self, cards: List['Card']) -> Dict[str, int]:
        """Helper method to count occurrences of each card value"""
        value_counts = {}
        for card in cards:
            value_counts[card.value] = value_counts.get(card.value, 0) + 1
        return value_counts
