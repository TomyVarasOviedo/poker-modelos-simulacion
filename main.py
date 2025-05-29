<<<<<<< fix
from poker_game import PokerGame
from poker_gui import PokerGUI
import tkinter as tk
import ttkbootstrap as ttk
=======
import random
from collections import Counter
from itertools import combinations
from typing import Dict, List, Optional
import tkinter as tk
import ttkbootstrap as ttk
from poker_game import PokerGame
from poker_gui import PokerGUI
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor


@dataclass
class SimulationConfig:
    num_players: int = 4
    num_games: int = 1000
    num_threads: int = 4
    sample_games: int = 100


class PokerSimulator:
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.game = PokerGame(config.num_players)

    def initialize_game(self) -> None:
        """Initialize game state with fresh deck and hands"""
        [self.game.deck.deal(2) for _ in range(self.config.num_players)]

    def run_sample_games(self) -> None:
        """
        Run sample games to gather betting statistics
        """
        for _ in range(self.config.num_games):
            try:
                self.game.simulate_game()
            except Exception as e:
                print(f"Warning: Sample game failed: {str(e)}")

    def simulate(self) -> Dict:
        """
        Run full simulation with Monte Carlo analysis

        Returns:
            - Dict: Simulation results
        """
        try:
            self.initialize_game()
            # Run Monte Carlo probability calculation
            results = self.game.monte_carlo_probability(community_cards=[
            ], num_simulations=self.config.num_games, num_threads=self.config.num_threads)
           # Gather betting statistics
            self.run_sample_games()

            return results

        except Exception as e:
            print(f"Error in simulation: {str(e)}")

        return self._generate_error_results()

    def _generate_error_results(self) -> Dict:
        """Generate empty results in case of simulation failure"""
        return {
            "probabilities": [0] * self.config.num_players,
            "confidence_intervals": [(0, 0)] * self.config.num_players,
            "player_stats": [],
            "strategies": []
        }

    def run_threaded_simulation(num_games: int, num_threads: int) -> Dict:
        """
        Run poker simulation with parallel processing

        Args:
            - num_games (int): Number of games to simulate
            - num_threads (int): Number of threads to use
        Returns:
            - Dict: Simulation results
        """
        config = SimulationConfig(num_games=num_games, num_threads=num_threads)

        simulator = PokerSimulator(config)
        return simulator.simulate()

    def run_console_mode():
        game = PokerGame(4)
        results = game.simulate_game()
        print(f"\nWinner: Player {results['winner'] + 1}")
        print(f"Profits: {results['profits']}")
        print(f"Hand strengths: {results['hand_strengths']}")

    def run_gui_mode():
        # Use ttkbootstrap Window with theme
        root = ttk.Window(themename="darkly")
        app = PokerGUI(root)
        root.mainloop()

    if __name__ == "__main__":
        import sys
>>>>>>> main

def run_console_mode():
    game = PokerGame(4)
    results = game.simulate_game()
    print(f"\nWinner: Player {results['winner'] + 1}")
    print(f"Profits: {results['profits']}")
    print(f"Hand strengths: {results['hand_strengths']}")

def run_gui_mode():
    # Use ttkbootstrap Window with theme
    root = ttk.Window(themename="darkly")
    app = PokerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--console':
        run_console_mode()
    else:
        run_gui_mode()
