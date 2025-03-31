import random
from collections import Counter
from itertools import combinations
import tkinter as tk
from poker_game import PokerGame
from poker_gui import PokerGUI

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
    
    def __str__(self):
        return f"{self.value} of {self.suit}"
    
    def __eq__(self, other):
        # Add equality comparison
        if isinstance(other, Card):
            return self.suit == other.suit and self.value == other.value
        return False

class Deck:
    def __init__(self):
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.cards = [Card(suit, value) for suit in suits for value in values]
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def deal(self, num_cards):
        return [self.cards.pop() for _ in range(num_cards)]

    def remove_card(self, target_card):
        # Add helper method to remove cards by value and suit
        for card in self.cards[:]:  # Create a copy to iterate
            if card.suit == target_card.suit and card.value == target_card.value:
                self.cards.remove(card)
                return

class PokerGame:
    def __init__(self, num_players):
        self.num_players = num_players
        self.deck = Deck()
        self.players_hands = []
    
    def simulate_game(self):
        self.deck.shuffle()
        self.players_hands = [self.deck.deal(2) for _ in range(self.num_players)]
        community_cards = self.deck.deal(5)
        
        print("\nCommunity Cards:")
        for card in community_cards:
            print(card)
            
        print("\nPlayer Hands:")
        for i, hand in enumerate(self.players_hands):
            print(f"Player {i+1}:", ", ".join(str(card) for card in hand))
        
        return self.monte_carlo_probability(community_cards)
    
    def monte_carlo_probability(self, community_cards, num_simulations=1000):
        wins = [0] * self.num_players
        
        for _ in range(num_simulations):
            temp_deck = Deck()
            
            # Remove known cards using the new helper method
            for hand in self.players_hands:
                for card in hand:
                    temp_deck.remove_card(card)
            for card in community_cards:
                temp_deck.remove_card(card)
            
            # Find winner
            winner = self.evaluate_hands(community_cards)
            wins[winner] += 1
        
        probabilities = [w/num_simulations for w in wins]
        return probabilities
    
    def evaluate_hands(self, community_cards):
        # Basic hand evaluation (can be expanded)
        scores = []
        for hand in self.players_hands:
            all_cards = hand + community_cards
            score = self.calculate_hand_score(all_cards)
            scores.append(score)
        return scores.index(max(scores))
    
    def calculate_hand_score(self, cards):
        values = [card.value for card in cards]
        suits = [card.suit for card in cards]
        value_counts = Counter(values)
        
        # Convert face cards to numeric values for straight checking
        value_map = {'J': '11', 'Q': '12', 'K': '13', 'A': '14'}
        numeric_values = [value_map.get(v, v) for v in values]
        numeric_values = [int(v) for v in numeric_values]
        numeric_values.sort()
        
        # Check for straight flush
        if len(set(suits)) == 1 and self.is_straight(numeric_values):
            return 9
        
        # Check for four of a kind
        if 4 in value_counts.values():
            return 8
            
        # Check for full house
        if 3 in value_counts.values() and 2 in value_counts.values():
            return 7
            
        # Check for flush
        if len(set(suits)) == 1:
            return 6
            
        # Check for straight
        if self.is_straight(numeric_values):
            return 5
            
        # Check for three of a kind
        if 3 in value_counts.values():
            return 4
            
        # Check for two pair
        if list(value_counts.values()).count(2) == 2:
            return 3
            
        # Check for one pair
        if 2 in value_counts.values():
            return 2
            
        # High card
        return 1

    def is_straight(self, values):
        if len(values) < 5:
            return False
        for i in range(len(values) - 4):
            if values[i+4] - values[i] == 4:  # Check for 5 consecutive cards
                return True
        return False

def run_console_mode():
    game = PokerGame(4)
    probabilities = game.simulate_game()
    
    print("\nWin Probabilities:")
    for i, prob in enumerate(probabilities):
        print(f"Player {i+1}: {prob:.2%}")

def run_gui_mode():
    root = tk.Tk()
    app = PokerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--console':
        run_console_mode()
    else:
        run_gui_mode()