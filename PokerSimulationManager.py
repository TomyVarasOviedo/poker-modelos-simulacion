from models.Player import Player
from strategies.TightAggressiveStrategy import TightAggressiveStrategy
from strategies.LooseAggressiveStrategy import LooseAggressiveStrategy
from strategies.ConservativeStrategy import ConservativeStrategy
from strategies.BluffingStrategy import BluffingStrategy
from PokerGame import PokerGame


class PokerSimulationManager:
    STRATEGY_MAP = {
        "tight-aggressive": TightAggressiveStrategy,
        "loose-aggressive": LooseAggressiveStrategy,
        "conservative": ConservativeStrategy,
        "bluffing": BluffingStrategy
    }

    def __init__(self, strategy1_name: str, strategy2_name: str, num_games: int):
        self.strategy1_name = strategy1_name.lower()
        self.strategy2_name = strategy2_name.lower()
        self.num_games = num_games

        self.player1 = Player(strategy_name=self.strategy1_name, strategy=self._get_strategy_instance(self.strategy1_name))
        self.player2 = Player(strategy_name=self.strategy2_name, strategy=self._get_strategy_instance(self.strategy2_name))
        print(f"{self.player1} and {self.player2}")

    def _get_strategy_instance(self, strategy_name: str):
        if strategy_name not in self.STRATEGY_MAP:
            raise ValueError(f"Estrategia no reconocida: {strategy_name}")
        return self.STRATEGY_MAP[strategy_name]()

    def run_simulation(self):
        for _ in range(self.num_games):
            game = PokerGame(self.player1, self.player2)
            winner = game.play()

            self.player1.stats["hands_dealt"] += 1
            self.player2.stats["hands_dealt"] += 1

            if winner:
                winner.stats["hands_won"] += 1

    def get_results(self):
        return {
            self.player1.strategy_name: {
                "win-rate": self.player1.get_win_rate(),
                "win_rate_total": self.player1.get_win_rate_total(),
                "hands_won": self.player1.stats["hands_won"],
                "hands_played": self.player1.stats["hands_played"],
                "hands_dealt": self.player1.stats["hands_dealt"],
            },
            self.player2.strategy_name: {
                "win-rate": self.player2.get_win_rate(),
                "win_rate_total": self.player2.get_win_rate_total(),
                "hands_won": self.player2.stats["hands_won"],
                "hands_played": self.player2.stats["hands_played"],
                "hands_dealt": self.player2.stats["hands_dealt"],
            }
        }
