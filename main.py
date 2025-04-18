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

def run_threaded_simulation(num_games: int, num_threads: int) -> Dict:
    """Run poker simulation with parallel processing"""
    game = PokerGame(4)  # Initialize with 4 players
    
    # First deal cards
    game.deck.shuffle()
    game.players_hands = [game.deck.deal(2) for _ in range(4)]
    
    # Run Monte Carlo simulation
    results = game.monte_carlo_probability(
        community_cards=[],  # Start with no community cards
        num_simulations=num_games,
        num_threads=num_threads
    )
    
    # Run some actual games to get betting statistics
    for _ in range(min(num_games, 100)):
        game_results = game.simulate_game()
        # Statistics are automatically updated in player_profiles
    
    return results

def run_console_mode():
    game = PokerGame(4)
    results = game.simulate_game()
    print(f"\nWinner: Player {results['winner'] + 1}")
    print(f"Profits: {results['profits']}")
    print(f"Hand strengths: {results['hand_strengths']}")

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