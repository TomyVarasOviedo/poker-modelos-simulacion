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

    def run_threaded_simulation(self, num_games: int, num_threads: int) -> dict:
        """
        Run poker simulation with parallel processing.
        Returns:
            - Dict: Aggregated simulation results.
        """
        if num_games > 0 and num_threads > 0:
            self.config.num_games = num_games
            self.config.num_threads = num_threads
            
        games_per_thread = self.config.num_games // self.config.num_threads
        extra_games = self.config.num_games % self.config.num_threads

        batches = [games_per_thread] * self.config.num_threads
        for i in range(extra_games):
            batches[i] += 1  # Distribute any remainder

        all_results = []
        with ThreadPoolExecutor(max_workers=self.config.num_threads) as executor:
            futures = [executor.submit(self.run_games_batch, n) for n in batches]
            for future in as_completed(futures):
                all_results.extend(future.result())

        # Aggregate results
        return self.aggregate_results(all_results)

    def aggregate_results(self, results_list: list) -> dict:
        """
        Aggregate results from all games to compute average win rates and stats.
        """
        if not results_list:
            return {}

        num_players = len(results_list[0]["player_stats"])
        total_hands_won = [0] * num_players
        total_hands_played = [0] * num_players
        total_hands_dealt = [0] * num_players
        total_profit = [0.0] * num_players
        strategies = results_list[0]["strategies"]

        for result in results_list:
            for i, stats in enumerate(result["player_stats"]):
                total_hands_won[i] += stats["hands_won"]
                total_hands_played[i] += stats["hands_played"]
                total_hands_dealt[i] += stats.get("hands_dealt", 1)
                total_profit[i] += stats["total_profit"]

        avg_win_rate = [
            total_hands_won[i] / max(1, total_hands_dealt[i])
            for i in range(num_players)
        ]
        avg_profit = [
            total_profit[i] / max(1, total_hands_dealt[i])
            for i in range(num_players)
        ]

        return {
            "average_win_rate": avg_win_rate,
            "average_profit": avg_profit,
            "total_hands_won": total_hands_won,
            "total_hands_played": total_hands_played,
            "total_hands_dealt": total_hands_dealt,
            "strategies": strategies,
        }