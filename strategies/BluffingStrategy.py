from .BasePokerStrategy import BasePokerStrategy
import random


class BluffingStrategy(BasePokerStrategy):
    def __init__(self):
        super().__init__()

    def make_decision(self, hand, community_cards, pot_size, current_bet, player_stack):
        """
        This function implements the desicions according to actual hand and community cards

        Args:
            - hand: list of Cards
            - community_cards: list of Cards
            - pot_size: float
            - current_bet: float
            - player_stack: float

        Returns:
            - desicion [String]: raise, call or fold
            - percentage_bet? [float]: ???
        """
        hand_strength = self.evaluate_hand_strength(hand, community_cards)
        pot_odds = self._calculate_pot_odds(pot_size, current_bet)

        # Bluffing behavior: Randomly raise even with weak hands
        if random.random() < 0.3:  # 30% chance to bluff
            return 'raise', min(current_bet * 2, player_stack)
        elif hand_strength > 0.7:  # Strong hands
            return 'raise', min(current_bet * 3, player_stack)
        elif hand_strength > 0.4 or pot_odds < 0.4:  # Decent hands or good odds
            return 'call', current_bet
        else:
            return 'fold', 0
