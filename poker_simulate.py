import random
from collections import Counter
from itertools import combinations
from typing import Dict, List, Optional
from models.Card import Card
from poker_game import PokerGame
from strategies.ConservativeStrategy import ConservativeStrategy
from strategies.AggressiveStrategy import AggressiveStrategy
from strategies.BluffingStrategy import BluffingStrategy
from strategies.TightStrategy import TightStrategy
from strategies.RandomStrategy import RandomStrategy
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

    def run_threaded_simulation(self) -> Dict:
        """
        Run poker simulation with parallel processing

        Args:
            - num_games (int): Number of games to simulate
            - num_threads (int): Number of threads to use
        Returns:
            - Dict: Simulation results
        """

        #simulator = PokerSimulator(config)
        return self.simulate()


