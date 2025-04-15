from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class PlayerProfile:
    strategy_name: str
    stats: Dict = field(default_factory=lambda: {
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

    def get_win_rate(self) -> float:
        if self.stats["hands_played"] == 0:
            return 0.0
        return self.stats["hands_won"] / self.stats["hands_played"]

    def get_position_win_rate(self, position: str) -> float:
        pos_stats = self.stats["position_stats"][position]
        if pos_stats["played"] == 0:
            return 0.0
        return pos_stats["won"] / pos_stats["played"]

    def get_bluff_success_rate(self) -> float:
        if self.stats["bluffs_attempted"] == 0:
            return 0.0
        return self.stats["bluffs_successful"] / self.stats["bluffs_attempted"]