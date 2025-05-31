from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

from models.player import Player


class BettingRound(Enum):
    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3


@dataclass
class BettingAction:
    player_id: int
    action_type: str
    amount: int

    def __init__ (self, player_id: int, action_type: str, amount: int):
        self.player_id = player_id
        self.action_type = action_type
        self.amount = amount


class BettingSystem:
    def __init__(self, num_players: int, players: List[Player],  initial_stack: int = 1000):
        self.num_players = num_players
        self.small_blind = 5
        self.big_blind = 10
        self.min_raise = self.big_blind
        self.current_pot = 0
        self.current_bet = 0
        for player in players:
            player.stack = initial_stack
        self.player_bets = [0] * num_players
        self.betting_history = []

    def start_new_round(self, players: List[Player]):
        """Start a new betting round"""
        self.current_pot = 0
        self.current_bet = 0
        self.player_bets = [0] * self.num_players
        players[:] = players[1:] + players[:1]
        self.post_blinds(players=players)

    def post_blinds(self, players: List[Player]):
        """Post small and big blinds"""
        # Small blind
        players[0].stack -= self.small_blind
        self.player_bets[0] = self.small_blind
        self.current_pot += self.small_blind

        # Big blind
        players[1].stack -= self.big_blind
        self.player_bets[1] = self.big_blind
        self.current_pot += self.big_blind
        self.current_bet = self.big_blind

    def handle_action(self, player_id: int, action: str, amount: int = 0) -> bool:
        """
        Handle a player's betting action

        Args:
            - player_id (int): ID of the player
            - action (str): Action taken by the player ('fold', 'call', 'raise')
            - amount (int): Amount to raise (only used if action is 'raise')

        Returns:
            - bool: True if action was successful, False otherwise
        """
        if action not in ['fold', 'call', 'raise']:
            return False

        if action == 'fold':
            self.betting_history.append(BettingAction(player_id, 'fold', amount))
            return True
        elif action == 'call':
            call_amount = self.current_bet - self.player_bets[player_id]
            if call_amount > self.player_stacks[player_id]:
                return False
            self.player_stacks[player_id] -= call_amount
            self.player_bets[player_id] += call_amount
            self.current_pot += call_amount
            self.betting_history.append(
                BettingAction(player_id, 'call', call_amount))
            return True
        elif action == 'raise':
            if amount < self.min_raise or amount > self.player_stacks[player_id]:
                return False
            self.player_stacks[player_id] -= amount
            self.player_bets[player_id] += amount
            self.current_pot += amount
            self.current_bet = amount
            self.min_raise = amount * 2
            self.betting_history.append(
                BettingAction(player_id, 'raise', amount))
            return True

    def get_pot_size(self) -> int:
        """
        Get current pot size

        Returns:
            - int: Current pot size
        """
        return self.current_pot

    def get_player_stack(self, player_id: int) -> int:
        """
        Get player's remaining stack

        Args:
            - player_id (int): ID of the player

        Returns:
            - int: Remaining stack of the player
        """
        return self.player_stacks[player_id]

    def get_min_raise(self) -> int:
        """
        Get minimum raise amount

        Returns:
            - int: Minimum raise amount
        """
        return self.min_raise

    def get_betting_history(self) -> List[BettingAction]:
        """
        Get history of betting actions

        Returns:
            - List[BettingAction]: List of betting actions
        """
        return self.betting_history
