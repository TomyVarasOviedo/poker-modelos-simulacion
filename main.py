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
from strategies.BluffingStrategy import BluffingStrategy
from strategies.TightStrategy import TightStrategy
from strategies.RandomStrategy import RandomStrategy

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
        # Reset deck at the start of each game
        self.deck = Deck()  # Add this line
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
    
    def monte_carlo_probability(self, community_cards, num_simulations=1000, num_threads=4):
        """
        Run Monte Carlo simulation with parallel processing
        
        Args:
            community_cards (List[Card]): Known community cards
            num_simulations (int): Total number of simulations to run
            num_threads (int): Number of threads to use for parallel processing
            
        Returns:
            Dict containing:
            - probabilities: List of win probabilities for each player
            - confidence_intervals: List of (lower, upper) bounds for each player
        """
        from concurrent.futures import ThreadPoolExecutor
        import numpy as np
        from scipy import stats
        
        sims_per_thread = num_simulations // num_threads
        
        def run_batch(batch_size):
            wins = [0] * self.num_players
            
            for _ in range(batch_size):
                temp_deck = Deck()
                
                # Remove known cards
                for hand in self.players_hands:
                    for card in hand:
                        temp_deck.remove_card(card)
                for card in community_cards:
                    temp_deck.remove_card(card)
                
                # Deal remaining community cards
                remaining = 5 - len(community_cards)
                simulated_community = community_cards + temp_deck.deal(remaining)
                
                # Find winner
                winner = self.evaluate_hands(simulated_community)
                wins[winner] += 1
                
            return wins
        
        # Run simulations in parallel
        all_wins = []
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            future_results = [executor.submit(run_batch, sims_per_thread) 
                             for _ in range(num_threads)]
            
            for future in future_results:
                all_wins.append(future.result())
        
        # Combine results
        total_wins = np.sum(all_wins, axis=0)
        probabilities = total_wins / num_simulations
        
        # Calculate 95% confidence intervals using normal approximation
        confidence_intervals = []
        for wins in total_wins:
            p = wins / num_simulations
            se = np.sqrt(p * (1-p) / num_simulations)
            ci = stats.norm.interval(0.95, loc=p, scale=se)
            confidence_intervals.append((max(0, ci[0]), min(1, ci[1])))
        
        return {
            "probabilities": probabilities.tolist(),
            "confidence_intervals": confidence_intervals
        }
    
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

    def _get_position(self, player_idx: int) -> str:
        """Determine player's position based on their index"""
        if self.num_players <= 3:
            return "late" if player_idx == self.num_players - 1 else "early"
            
        positions = ["early"] * (self.num_players // 3)
        positions += ["middle"] * (self.num_players // 3)
        positions += ["late"] * (self.num_players - len(positions))
        return positions[player_idx]

    def _was_bluff_attempted(self, player_idx: int) -> bool:
        """Determine if player attempted to bluff"""
        # Simple implementation - consider it a bluff if player's hand strength is low
        hand_strength = self.calculate_hand_score(self.players_hands[player_idx])
        return hand_strength < 3  # Pair or lower is considered a bluff

    def _was_bluff_successful(self, player_idx: int, winner: int) -> bool:
        """Determine if bluff was successful"""
        return self._was_bluff_attempted(player_idx) and player_idx == winner

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
    from strategies import (
        ConservativeStrategy,
        AggressiveStrategy,
        BluffingStrategy,
        TightStrategy,
        RandomStrategy
    )
    
    strategies = {
        "Conservative": ConservativeStrategy(),
        "Aggressive": AggressiveStrategy(),
        "Bluffing": BluffingStrategy(),
        "Tight": TightStrategy(),
        "Random": RandomStrategy()
    }
    
    results = {
        name: {
            "wins": 0, 
            "total_profit": 0.0, 
            "profit_history": [],
            "hands_played": 0,  # Initialize hands_played
            "hands_won": 0,     # Initialize hands_won
            "bluffs_attempted": 0,
            "bluffs_successful": 0,
            "position_stats": {
                "early": {"played": 0, "won": 0},
                "middle": {"played": 0, "won": 0},
                "late": {"played": 0, "won": 0}
            }
        } 
        for name in strategies.keys()
    }
    
    games_per_thread = num_games // num_threads
    
    def run_batch(batch_size):
        game = PokerGame(len(strategies))
        batch_results = {name: results[name].copy() for name in strategies}
        
        for _ in range(batch_size):
            game_result = game.simulate_game()
            winner = game_result["winner"]
            profits = game_result["profits"]
            
            # Update statistics for each player
            for i, (name, strategy) in enumerate(strategies.items()):
                batch_results[name]["hands_played"] += 1  # Increment hands played
                if i == winner:
                    batch_results[name]["hands_won"] += 1  # Increment hands won
                    batch_results[name]["wins"] += 1
                    
                batch_results[name]["total_profit"] += profits[i]
                batch_results[name]["profit_history"].append(profits[i])
                
                # Update position stats
                position = game._get_position(i)
                batch_results[name]["position_stats"][position]["played"] += 1
                if i == winner:
                    batch_results[name]["position_stats"][position]["won"] += 1
                
                # Track bluffs
                if game._was_bluff_attempted(i):
                    batch_results[name]["bluffs_attempted"] += 1
                    if game._was_bluff_successful(i, winner):  # Pass winner parameter
                        batch_results[name]["bluffs_successful"] += 1
        
        return batch_results

    # Run simulations in parallel
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_results = [executor.submit(run_batch, games_per_thread) 
                         for _ in range(num_threads)]
        
        # Combine results from all threads
        for future in future_results:
            batch_results = future.result()
            for name in strategies:
                results[name]["hands_played"] += batch_results[name]["hands_played"]
                results[name]["hands_won"] += batch_results[name]["hands_won"]
                results[name]["wins"] += batch_results[name]["wins"]
                results[name]["total_profit"] += batch_results[name]["total_profit"]
                results[name]["profit_history"].extend(batch_results[name]["profit_history"])
                results[name]["bluffs_attempted"] += batch_results[name]["bluffs_attempted"]
                results[name]["bluffs_successful"] += batch_results[name]["bluffs_successful"]
                
                # Combine position stats
                for position in ["early", "middle", "late"]:
                    results[name]["position_stats"][position]["played"] += \
                        batch_results[name]["position_stats"][position]["played"]
                    results[name]["position_stats"][position]["won"] += \
                        batch_results[name]["position_stats"][position]["won"]
    
    # Convert results to the expected format
    results["player_stats"] = [
        {
            "hands_played": results[name]["hands_played"],
            "hands_won": results[name]["hands_won"],
            "total_profit": results[name]["total_profit"],
            "bluffs_attempted": results[name]["bluffs_attempted"],
            "bluffs_successful": results[name]["bluffs_successful"],
            "position_stats": results[name]["position_stats"]
        }
        for name in strategies.keys()
    ]
    results["strategies"] = list(strategies.keys())
    
    return results

def calculate_std_dev(profit_history):
    """Calculate standard deviation of profit history"""
    if not profit_history:
        return 0.0
    mean = sum(profit_history) / len(profit_history)
    variance = sum((x - mean) ** 2 for x in profit_history) / len(profit_history)
    return variance ** 0.5

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--console':
        run_console_mode()
    else:
        run_gui_mode()