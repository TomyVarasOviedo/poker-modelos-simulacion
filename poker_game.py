from typing import List
from models.Card import Card
from models.betting_system import BettingSystem, BettingRound
from models.player_profile import PlayerProfile
from models.player import Player
from collections import Counter
import random
import numpy as np
from scipy import stats
from concurrent.futures import ThreadPoolExecutor
from strategies.ConservativeStrategy import ConservativeStrategy
from strategies.AggressiveStrategy import AggressiveStrategy
from strategies.BluffingStrategy import BluffingStrategy
from strategies.TightStrategy import TightStrategy
from strategies.RandomStrategy import RandomStrategy


class Deck:
    def __init__(self):
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        values = ['2', '3', '4', '5', '6', '7',
                  '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.cards = [Card(suit, value) for suit in suits for value in values]

    def shuffle(self):
        """This method shuffles the deck of cards"""
        random.shuffle(self.cards)

    def deal(self, num_cards):
        """This method deals a specified number of cards from the deck"""
        return [self.cards.pop() for _ in range(num_cards)]

    def remove_card(self, target_card):
        """
        This method removes a specific card from the deck.

        Args:
            - target_card (Card): The card to be removed.

        """
        for card in self.cards[:]:
            if card.suit == target_card.suit and card.value == target_card.value:
                self.cards.remove(card)
                return


class PokerGame:
    num_players: int
    players_hands: List[List[Card]]
    deck: Deck
    betting_system: BettingSystem
    current_round: BettingRound
    player_profiles: List[PlayerProfile]
    community_cards: List[Card]
    players: List[Player]

    def __init__(self, num_players, initial_stack=1000):
        self.num_players = num_players
        self.deck = Deck()
        self.players_hands = []
        self.betting_system = BettingSystem(num_players, initial_stack)
        self.current_round = BettingRound.PREFLOP
        self.player_profiles = []
        self.community_cards = []

        # Initialize players with strategies (limit to num_players)
        self.players = []
        strategies = {
            "Conservative": ConservativeStrategy(),
            "Aggressive": AggressiveStrategy(),
            "Bluffing": BluffingStrategy(),
            "Tight": TightStrategy()
        }

        # Add only the number of players requested
        for i, (strategy_name, strategy) in enumerate(strategies.items()):
            if i >= num_players:
                break
            self.players.append(Player(strategy))
            self.add_player(strategy_name)

    def add_player(self, strategy_name: str):
        """
        Add a player with their profile

        Args:
            - strategy_name (str): The name of the player's strategy.
        """
        profile = PlayerProfile(strategy_name)
        self.player_profiles.append(profile)

    def simulate_game(self):
        """
        This method simulates a complete game of poker

        Returns:
            - dict: A dictionary containing the game results, including the winner, profits, hand strengths, betting history, and player stats.
        """
        # Reset and reshuffle deck at the start of each game
        self.deck = Deck()  # Create a fresh deck
        self.deck.shuffle()
        self.betting_system.start_new_round()
        self.players_hands = [self.deck.deal(2)
                              for _ in range(self.num_players)]
        self.community_cards = []

        # Preflop betting
        self._handle_betting_round()

        # Flop
        self.community_cards.extend(self.deck.deal(3))
        self.current_round = BettingRound.FLOP
        self._handle_betting_round()

        # Turn
        self.community_cards.extend(self.deck.deal(1))
        self.current_round = BettingRound.TURN
        self._handle_betting_round()

        # River
        self.community_cards.extend(self.deck.deal(1))
        self.current_round = BettingRound.RIVER
        self._handle_betting_round()

        # Evaluate hands and determine winner
        hand_strengths = []
        for hand in self.players_hands:
            all_cards = hand + self.community_cards
            score = self.calculate_hand_score(all_cards)
            hand_strengths.append(score)

        winner = int(hand_strengths.index(max(hand_strengths)))
        pot_size = self.betting_system.get_pot_size()

        # Winner takes the pot
        self.betting_system.player_stacks[winner] += pot_size

        # Update player profiles with game results
        for i in range(self.num_players):
            position = self._get_position(i)
            is_winner = i == winner
            profit = self.betting_system.get_player_stack(i) - 1000

            # Update basic stats
            self.player_profiles[i].stats["hands_played"] += 1
            if is_winner:
                self.player_profiles[i].stats["hands_won"] += 1
            self.player_profiles[i].stats["total_profit"] += profit

            # Update position stats
            pos_stats = self.player_profiles[i].stats["position_stats"][position]
            pos_stats["played"] += 1
            if is_winner:
                pos_stats["won"] += 1

            # Update bluffing stats
            if self._was_bluff_attempted(i):
                self.player_profiles[i].stats["bluffs_attempted"] += 1
                if self._was_bluff_successful(i):
                    self.player_profiles[i].stats["bluffs_successful"] += 1

        return {
            "winner": winner,
            "profits": [self.betting_system.get_player_stack(i) - 1000 for i in range(self.num_players)],
            "hand_strengths": hand_strengths,
            "betting_history": self.betting_system.get_betting_history(),
            "player_stats": [profile.stats for profile in self.player_profiles],
            "strategies": [profile.strategy_name for profile in self.player_profiles]
        }

    def _handle_betting_round(self):
        """Handle a complete betting round"""
        for i in range(self.num_players):
            if self.betting_system.get_player_stack(i) <= 0:
                continue

            action, amount = self.players[i].strategy.make_decision(
                self.players_hands[i],
                self.community_cards,
                self.betting_system.get_pot_size(),
                self.betting_system.current_bet,
                self.betting_system.get_player_stack(i)
            )

            self.betting_system.handle_action(i, action, amount)

    def monte_carlo_probability(self, community_cards, num_simulations=1000, num_threads=4):
        """
        Run Monte Carlo simulation with parallel processing

        Args:
            - community_cards (List[Card]): Community cards on the table
            - community_cards (int): Number of simulations to run
            - num_simulation (int): Number of simulations to run
            - num_threads (int): Number of threads to use
        Returns:
            - dict: Simulation results including probabilities and confidence intervals
        """
        # Always start with a fresh deck
        self.deck = Deck()
        self.deck.shuffle()

        # Initialize player hands if not already done
        if not self.players_hands:
            self.players_hands = [self.deck.deal(
                2) for _ in range(self.num_players)]

        sims_per_thread = num_simulations // num_threads

        def run_batch(batch_size):
            wins = [0] * self.num_players

            for _ in range(batch_size):
                temp_deck = Deck()  # Create fresh deck for each simulation

                # Remove known cards
                for hand in self.players_hands:
                    for card in hand:
                        temp_deck.remove_card(card)
                for card in community_cards:
                    temp_deck.remove_card(card)

                # Deal remaining community cards
                remaining = 5 - len(community_cards)
                simulated_community = community_cards + \
                    temp_deck.deal(remaining)

                # Calculate scores for all players
                scores = []
                for hand in self.players_hands:
                    all_cards = hand + simulated_community
                    score = self.calculate_hand_score(all_cards)
                    scores.append(score)

                # Find winner
                if scores:  # Check if we have valid scores
                    max_score = max(scores)
                    winner = scores.index(max_score)
                    wins[winner] += 1

            return wins

        # Run simulations in parallel
        all_wins = []
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            future_results = [executor.submit(run_batch, sims_per_thread)
                              for _ in range(num_threads)]

            for future in future_results:
                all_wins.append(future.result())

        # Combine results
        total_wins = np.sum(all_wins, axis=0)
        probabilities = total_wins / num_simulations

        # Calculate 95% confidence intervals using normal approximation
        confidence_intervals = []
        for wins in total_wins:
            p = wins / num_simulations
            # Add error handling for edge cases
            if p == 0 or p == 1:
                # If probability is 0 or 1, use exact confidence interval
                confidence_intervals.append((p, p))
            else:
                try:
                    se = np.sqrt(p * (1-p) / num_simulations)
                    if not np.isnan(se) and se > 0:
                        ci = stats.norm.interval(0.95, loc=p, scale=se)
                        confidence_intervals.append(
                            (max(0, ci[0]), min(1, ci[1])))
                    else:
                        # Fallback for very small standard errors
                        confidence_intervals.append(
                            (max(0, p-0.05), min(1, p+0.05)))
                except (ValueError, RuntimeWarning):
                    # Fallback for numerical issues
                    confidence_intervals.append(
                        (max(0, p-0.05), min(1, p+0.05)))

        return {
            "probabilities": probabilities.tolist(),
            "confidence_intervals": confidence_intervals,
            "player_stats": [profile.stats for profile in self.player_profiles],
            "strategies": [profile.strategy_name for profile in self.player_profiles]
        }

    def evaluate_hands(self, community_cards):
        """
        Evaluate all players' hands and return the index of the winner

        Args:
            - community_cards (List[Card]): Community cards on the table

        Returns:
            - int: Index of the winning player
        """
        scores = []  # Initialize scores list
        for hand in self.players_hands:
            all_cards = hand + community_cards
            score = self.calculate_hand_score(all_cards)
            scores.append(score)  # Add the score to the list

        # Return winner index, handle empty scores case
        if not scores:
            return 0  # Default to first player if no scores
        return scores.index(max(scores))

    def calculate_hand_score(self, cards):
        """
        This method calculates the score of a poker hand

        Args:
            - cards (List[Card]): List of cards in the hand

        Returns:
            - int: The score of the hand
        """
        values = [card.value for card in cards]
        suits = [card.suit for card in cards]
        value_counts = Counter(values)

        value_map = {'J': '11', 'Q': '12', 'K': '13', 'A': '14'}
        numeric_values = [value_map.get(v, v) for v in values]
        numeric_values = [int(v) for v in numeric_values]
        numeric_values.sort()

        if len(set(suits)) == 1 and self.is_straight(numeric_values):
            return 9
        if 4 in value_counts.values():
            return 8
        if 3 in value_counts.values() and 2 in value_counts.values():
            return 7
        if len(set(suits)) == 1:
            return 6
        if self.is_straight(numeric_values):
            return 5
        if 3 in value_counts.values():
            return 4
        if list(value_counts.values()).count(2) == 2:
            return 3
        if 2 in value_counts.values():
            return 2
        return 1

    def is_straight(self, values):
        if len(values) < 5:
            return False
        for i in range(len(values) - 4):
            if values[i+4] - values[i] == 4:
                return True
        return False

    def _get_position(self, player_idx: int) -> str:
        """
        Determine player's position

        Args:
            - player_idx (int): Index of the player
        Returns:
            - str: Player's position ("early", "middle", "late")
        """
        positions = ["early", "middle", "late"]
        position_idx = (player_idx * len(positions)) // self.num_players
        return positions[position_idx]

    def _was_bluff_attempted(self, player_idx: int) -> bool:
        """
        Determine if player attempted to bluff

        Args:
            - player_idx (int): Index of the player
        Returns:
            - bool: True if bluff was attempted, False otherwise
        """
        actions = self.betting_system.get_betting_history()
        hand_strength = self.calculate_hand_score(
            self.players_hands[player_idx])
        return any(action.player_id == player_idx and
                   action.action_type == "raise" and
                   hand_strength < 5
                   for action in actions)

    def _was_bluff_successful(self, player_idx: int) -> bool:
        """
        Determine if bluff was successful

        Args:
            - player_idx (int): Index of the player
        Returns:
            - bool: True if bluff was successful, False otherwise
        """
        current_winner = self.evaluate_hands(self.community_cards)
        return self._was_bluff_attempted(player_idx) and player_idx == current_winner

    def _get_hand_type(self, hand_strength: int) -> str:
        """
        Get the type of hand based on its strength

        Args:
            - hand_strength (int): The strength of the hand

        Returns:
            - str: The type of hand
        """
        hand_types = {
            9: "Straight Flush",
            8: "Four of a Kind",
            7: "Full House",
            6: "Flush",
            5: "Straight",
            4: "Three of a Kind",
            3: "Two Pair",
            2: "One Pair",
            1: "High Card"
        }
        return hand_types.get(hand_strength, "Unknown")
