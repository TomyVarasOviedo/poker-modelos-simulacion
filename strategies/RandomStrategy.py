from .BasePokerStrategy import BasePokerStrategy
import random


class RandomStrategy(BasePokerStrategy):
    def __init__(self):
        super().__init__()

    def make_decision(self, hand, community_cards, pot_size, current_bet, player_stack):
        """
        This function implements a random decision-making strategy for poker.

        Args:
            - hand: list of Cards
            - community_cards: list of Cards
            - pot_size: float
            - current_bet: float
            - player_stack: float

        Returns:
            - decision [String]: raise, call or fold
            - percentage_bet? [float]: amount to bet or call
        """
        action = random.choice(['fold', 'call', 'raise'])
        if action == 'fold':
            return 'fold', 0
        elif action == 'call':
            return 'call', current_bet
        elif action == 'raise':
            return 'raise', min(current_bet * random.randint(2, 5), player_stack)
