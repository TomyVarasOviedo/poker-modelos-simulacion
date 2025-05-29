from .BasePokerStrategy import BasePokerStrategy


class ConservativeStrategy(BasePokerStrategy):
    def make_decision(self, hand, community_cards, pot_size, current_bet, player_stack):
        """
        This function implements the decisions according to actual hand and community cards

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
        hand_strength = self.evaluate_hand_strength(hand, community_cards)
        pot_odds = self._calculate_pot_odds(pot_size, current_bet)
        # Conservative play - only play strong hands
        if hand_strength > 0.85:  # Very strong hands
            return 'raise', min(current_bet * 2, player_stack)
        elif hand_strength > 0.7 and pot_odds < 0.25:  # Strong hands with good odds
            return 'call', current_bet
        else:  # Fold everything else
            return 'fold', 0

    def __init__(self):
        super().__init__()
