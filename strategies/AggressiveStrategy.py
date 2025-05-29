from .BasePokerStrategy import BasePokerStrategy


class AggressiveStrategy(BasePokerStrategy):
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
            desicion [String]: raise, call or fold
            percentage_bet? [float]: ???
        """
        import random
        hand_strength = self.evaluate_hand_strength(hand, community_cards)
        pot_odds = self._calculate_pot_odds(pot_size, current_bet)

        # Aggressive play - bet more frequently with wider range
        if hand_strength > 0.7:
            return 'raise', min(current_bet * 3, player_stack)
        elif hand_strength > 0.5 and pot_odds < 0.4:
            return 'call', current_bet
        elif random.random() < 0.15 and pot_odds < 0.25:
            return 'raise', min(current_bet * 2, player_stack)  # Occasional bluff
        else:
            return 'fold', 0
