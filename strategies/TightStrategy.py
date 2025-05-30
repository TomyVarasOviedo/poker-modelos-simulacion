from .BasePokerStrategy import BasePokerStrategy


class TightStrategy(BasePokerStrategy):
    def __init__(self):
        super().__init__()

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

        # Tight behavior: Only play very strong hands
        if hand_strength > 0.75:
            return 'raise', min(current_bet * 2, player_stack)
        elif hand_strength > 0.55 and pot_odds < 0.4:
            return 'call', current_bet
        elif hand_strength > 0.4 and pot_odds < 0.2:
            return 'call', current_bet
        # Rare semi-bluff with weak hand if pot odds are very good
        elif hand_strength > 0.3 and pot_odds < 0.15:
            return 'raise', min(current_bet * 2, player_stack)
        else:
            return 'fold', 0
