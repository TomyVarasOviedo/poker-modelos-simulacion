import random
from typing import List
from models.Card import Card
from models.Player import Player
from strategies.BasePokerStrategy import BasePokerStrategy

class Deck:
    def __init__(self):
        self.reset()

    def reset(self):
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        values = ['2', '3', '4', '5', '6', '7',
                  '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.cards = [Card(suit, value) for suit in suits for value in values]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, num_cards: int) -> List[Card]:
        return [self.cards.pop() for _ in range(num_cards)]

    def remove_card(self, target_card: Card):
        for card in self.cards[:]:
            if card.suit == target_card.suit and card.value == target_card.value:
                self.cards.remove(card)
                return

class PokerGame:
    def __init__(self, player1: Player, player2: Player):
        self.player1 = player1
        self.player2 = player2
        self.deck = Deck()
        self.deck.shuffle()
        self.community_cards = []

    def deal_hole_cards(self):
        self.player1.player_hand = self.deck.deal(2)
        self.player2.player_hand = self.deck.deal(2)

    def deal_flop(self):
        self.deck.deal(1)  # Burn card
        self.community_cards += self.deck.deal(3)

    def deal_turn(self):
        self.deck.deal(1)  # Burn card
        self.community_cards += self.deck.deal(1)

    def deal_river(self):
        self.deck.deal(1)  # Burn card
        self.community_cards += self.deck.deal(1)

    def play(self):
        self.deal_hole_cards()

        # Preflop decision
        action1 = self.player1.strategy.make_decision(
            self.player1.player_hand, [], phase='preflop'
        )
        action2 = self.player2.strategy.make_decision(
            self.player2.player_hand, [], phase='preflop'
        )

        if self._handle_folds(action1, action2):
            if action1 == "fold" and action2 != "fold":
                self.player2.stats["hands_played"] += 1
            elif action2 == "fold" and action1 != "fold":
                self.player1.stats["hands_played"] += 1
            return self._fold_winner(action1, action2)

        self.player1.stats["hands_played"] += 1
        self.player2.stats["hands_played"] += 1

        self.deal_flop()
        action1 = self.player1.strategy.make_decision(
            self.player1.player_hand, self.community_cards.copy(), phase='flop'
        )
        action2 = self.player2.strategy.make_decision(
            self.player2.player_hand, self.community_cards.copy(), phase='flop'
        )

        if self._handle_folds(action1, action2):
            return self._fold_winner(action1, action2)

        self.deal_turn()
        action1 = self.player1.strategy.make_decision(
            self.player1.player_hand, self.community_cards.copy(), phase='turn'
        )
        action2 = self.player2.strategy.make_decision(
            self.player2.player_hand, self.community_cards.copy(), phase='turn'
        )

        if self._handle_folds(action1, action2):
            return self._fold_winner(action1, action2)

        self.deal_river()
        action1 = self.player1.strategy.make_decision(
            self.player1.player_hand, self.community_cards.copy(), phase='river'
        )
        action2 = self.player2.strategy.make_decision(
            self.player2.player_hand, self.community_cards.copy(), phase='river'
        )
        

        if self._handle_folds(action1, action2):
            return self._fold_winner(action1, action2)

        # Showdown

        strength1 = self.player1.strategy.evaluate_hand_strength(
            self.player1.player_hand, self.community_cards
        )
        strength2 = self.player2.strategy.evaluate_hand_strength(
            self.player2.player_hand, self.community_cards
        )

        if strength1 > strength2:
            return self.player1
        elif strength2 > strength1:
            return self.player2
        else:
            return None  # Empate

    def _handle_folds(self, action1: str, action2: str) -> bool:
        return action1 == "fold" or action2 == "fold"

    def _fold_winner(self, action1: str, action2: str):
        if action1 == "fold" and action2 != "fold":
            return self.player2
        elif action2 == "fold" and action1 != "fold":
            return self.player1
        elif action1 == "fold" and action2 == "fold":
            return None  # Ambos se retiran
