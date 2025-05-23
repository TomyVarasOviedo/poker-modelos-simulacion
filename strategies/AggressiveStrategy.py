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
        hand_strength = self.evaluate_hand_strength(hand, community_cards)
        pot_odds = self._calculate_pot_odds(pot_size, current_bet)

        # Aggressive play - bet more frequently with wider range
        if hand_strength > 0.6:  # Moderately strong hands
            return 'raise', min(current_bet * 3, player_stack)  # Bigger raises
        elif hand_strength > 0.4:  # Even marginal hands
            return 'raise', min(current_bet * 1.5, player_stack)
        elif pot_odds < 0.4:  # Speculative hands with decent odds
            return 'call', current_bet
        else:
            return 'fold', 0
