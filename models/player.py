from strategies.BasePokerStrategy import BasePokerStrategy
class Player:
    def __init__(self, strategy_name, strategy):
        self.strategy_name = strategy_name              # Nombre legible: "Tight-Aggressive", etc.
        self.strategy: BasePokerStrategy = strategy               # Instancia de la estrategia (objeto con método de decisión)
        self.player_hand = []                           # Lista de cartas (se definirá con clase Card)
        self.stats = {
            "hands_dealt": 0,
            "hands_played": 0,
            "hands_won": 0,
        }

    def reset_hand(self):
        """Limpia la mano del jugador (para repartir una nueva)."""
        self.player_hand = []

    def update_stat(self, key, amount=1):
        """Incrementa una estadística básica."""
        if key in self.stats:
            self.stats[key] += amount

    def get_win_rate_total(self) -> float:
        """
        Calcula el win rate general del jugador (hands_won / hands_dealt).
        """
        if self.stats["hands_dealt"] == 0:
            return 0.0
        return self.stats["hands_won"] / self.stats["hands_dealt"]
    
    def get_win_rate(self) -> float:
        """
        Calcula el win rate general del jugador (hands_won / hands_played).
        """
        if self.stats["hands_played"] == 0:
            return 0.0
        return self.stats["hands_won"] / self.stats["hands_played"]

    def __repr__(self):
        return f"Player({self.strategy_name})"
