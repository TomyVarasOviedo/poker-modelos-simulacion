from .BasePokerStrategy import BasePokerStrategy

class TightStrategy(BasePokerStrategy):
    def __init__(self):
        super().__init__()
    def make_decision(self, hand, community_cards, pot_size, current_bet, player_stack):
        hand_strength = self.evaluate_hand_strength(hand, community_cards)
        pot_odds = self._calculate_pot_odds(pot_size, current_bet)

        # Tight behavior: Only play very strong hands
        if hand_strength > 0.85:  # Very strong hands
            return 'raise', min(current_bet * 2, player_stack)
        elif hand_strength > 0.7 and pot_odds < 0.3:  # Strong hands with good odds
            return 'call', current_bet
        else:
            return 'fold', 0