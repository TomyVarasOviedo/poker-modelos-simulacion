from dataclasses import dataclass, field
from typing import Dict, List
from strategies.BasePokerStrategy import BasePokerStrategy
from models.Card import Card

@dataclass
class Player:
    strategy: BasePokerStrategy
    player_hands: List[Card]
    stack: int
    stats: Dict = field(default_factory=lambda: {
        "hands_dealt": 0,
        "hands_played": 0,
        "hands_won": 0,
        "total_profit": 0.0,
        "bluffs_attempted": 0,
        "bluffs_successful": 0,
        "position_stats": {
            "early": {"played": 0, "won": 0},
            "middle": {"played": 0, "won": 0},
            "late": {"played": 0, "won": 0}
        }
    })
    
    @property
    def strategy_name(self) -> str:
        """Get the name of the strategy being used by this player"""
        return self.strategy.__class__.__name__

    def get_win_rate(self) -> float:
        """
        This method calculates the win rate of the player.

        Returns:
            - float: The win rate of the player as a percentage.
        """
        if self.stats["hands_played"] == 0:
            return 0.0
        return self.stats["hands_won"] / self.stats["hands_played"]

    def get_position_win_rate(self, position: str) -> float:
        """
        This method calculates the win rate of the player based on their position.

        Args:
            - position (str): The position of the player ('early', 'middle', 'late').

        Returns:
            - float: The win rate of the player in the specified position as a percentage.
        """
        pos_stats = self.stats["position_stats"][position]
        if pos_stats["played"] == 0:
            return 0.0
        return pos_stats["won"] / pos_stats["played"]

    def get_bluff_success_rate(self) -> float:
        """
        This method calculates the bluff success rate of the player.

        Returns:
            - float: The bluff success rate of the player as a percentage.
        """
        if self.stats["bluffs_attempted"] == 0:
            return 0.0
        return self.stats["bluffs_successful"] / self.stats["bluffs_attempted"]
    
    def get_player_stack(self) -> int:
        """
        Get player's remaining stack

        Args:
            - player_id (int): ID of the player

        Returns:
            - int: Remaining stack of the player
        """
        return self.stack
