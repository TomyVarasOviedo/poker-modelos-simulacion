from .BasePokerStrategy import BasePokerStrategy
import random

class RandomStrategy(BasePokerStrategy):
    def __init__(self):
        super().__init__()
    def make_decision(self, hand, community_cards, pot_size, current_bet, player_stack):
        # Randomly choose an action
        action = random.choice(['fold', 'call', 'raise'])
        if action == 'fold':
            return 'fold', 0
        elif action == 'call':
            return 'call', current_bet
        elif action == 'raise':
            return 'raise', min(current_bet * random.randint(2, 5), player_stack)