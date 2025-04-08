import random
from collections import Counter
from itertools import combinations
from typing import Dict
import tkinter as tk
from models.Card import Card
from poker_game import PokerGame
from poker_gui import PokerGUI
from strategies.ConservativeStrategy import ConservativeStrategy
from strategies.AggressiveStrategy import AggressiveStrategy

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
        
        # Evaluate hands and determine the winner
        hand_strengths = []
        for hand in self.players_hands:
            all_cards = hand + community_cards
            score = self.calculate_hand_score(all_cards)
            hand_strengths.append(score)
        
        winner = int(hand_strengths.index(max(hand_strengths)))
        
        # Calculate profits (simplified)
        profits = [-10] * self.num_players  # Everyone loses 10 by default
        profits[winner] = 10 * (self.num_players - 1)  # Winner takes all
        
        # Return dictionary with game results
        return {
            "winner": winner,
            "profits": profits,
            "hand_strengths": hand_strengths
        }
    
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

def run_threaded_simulation(num_games: int, num_threads: int) -> Dict:
    """Run poker simulations using multiple threads"""
    from concurrent.futures import ThreadPoolExecutor
    
    strategies = {
        "Conservative": ConservativeStrategy(),
        "Aggressive": AggressiveStrategy()
    }
    
    results = {
        name: {"wins": 0, "total_profit": 0.0} 
        for name in strategies.keys()
    }
    
    games_per_thread = num_games // num_threads
    
    def run_batch(batch_size):
        batch_results = {
            name: {"wins": 0, "profit": 0.0}
            for name in strategies.keys()
        }
        
        for _ in range(batch_size):
            game = PokerGame(len(strategies))
            result = game.simulate_game()  # Now returns a dictionary
            winner_idx = result["winner"]
            profits = result["profits"]
            
            strategy_name = list(strategies.keys())[winner_idx]
            batch_results[strategy_name]["wins"] += 1
            
            for i, profit in enumerate(profits):
                name = list(strategies.keys())[i]
                batch_results[name]["profit"] += profit
        
        return batch_results
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(run_batch, games_per_thread) 
            for _ in range(num_threads)
        ]
        
        for future in futures:
            batch_results = future.result()
            for name, stats in batch_results.items():
                results[name]["wins"] += stats["wins"]
                results[name]["total_profit"] += stats["profit"]
    
    # Calculate final statistics
    for name in results:
        results[name]["win_rate"] = results[name]["wins"] / num_games
        results[name]["avg_profit"] = results[name]["total_profit"] / num_games
        
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--console':
        run_console_mode()
    else:
        run_gui_mode()