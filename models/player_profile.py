from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class PlayerProfile:
    strategy_name: str
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