from typing import Dict
from poker_game import PokerGame
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class SimulationConfig:
    num_players: int = 4
    num_games: int = 1000
    num_threads: int = 4
    sample_games: int = 100


class PokerSimulator:
    def __init__(self, config: SimulationConfig):
        self.config = config

    def initialize_game(self, game) -> None:
        """Initialize game state with fresh deck and hands"""
        [game.deck.deal(2) for _ in range(self.config.num_players)]

    def run_games_batch(self, num_games: int) -> list:
       """Run a batch of games in a single thread and return the results list."""
       game = PokerGame(self.config.num_players)
       batch_results = []
       for _ in range(num_games):
           result = game.simulate_game()
           batch_results.append(result)
       return batch_results

    def simulate(self) -> Dict:
        """
        Run full simulation with Monte Carlo analysis

        Returns:
            - Dict: Simulation results
        """
        try:
            self.initialize_game()
            
            # Run Monte Carlo probability calculation with empty community cards
            # This simulates from the beginning of a hand (preflop)
            results = self.game.monte_carlo_probability(
                community_cards=[],  # Start with no community cards
                num_simulations=self.config.num_games,
                num_threads=self.config.num_threads
            )
            
            # Gather betting statistics from sample games
            self.run_sample_games()
            
            return results

        except Exception as e:
            print(f"Error in simulation: {str(e)}")
            import traceback
            traceback.print_exc()

        return self._generate_error_results()

    def _generate_error_results(self) -> Dict:
        """Generate empty results in case of simulation failure"""
        return {
            "probabilities": [0] * self.config.num_players,
            "confidence_intervals": [(0, 0)] * self.config.num_players,
            "player_stats": [],
            "strategies": []
        }

    def run_threaded_simulation(self, num_games=None, num_threads=None) -> Dict:
        """
        Run poker simulation with parallel processing

        Args:
            - num_games (int): Number of games to simulate (overrides config)
            - num_threads (int): Number of threads to use (overrides config)
        Returns:
            - Dict: Simulation results
        """
        # Update configuration if parameters are provided
        if num_games is not None:
            self.config.num_games = num_games
        if num_threads is not None:
            self.config.num_threads = num_threads
            
        return self.simulate()


