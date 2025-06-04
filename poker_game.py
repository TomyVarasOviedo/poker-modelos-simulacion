from typing import List
from models.Card import Card
from models.betting_system import BettingSystem, BettingRound
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
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
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
        """
        for card in self.cards[:]:
            if card.suit == target_card.suit and card.value == target_card.value:
                self.cards.remove(card)
                return


class PokerGame:
    num_players: int
    deck: Deck
    betting_system: BettingSystem
    current_round: BettingRound
    community_cards: List[Card]
    players: List[Player]
    players_hands: List[List[Card]]

    def __init__(self, num_players: int):
        self.num_players = num_players
        self.deck = Deck()
        self.community_cards = []
        self.players_hands = [] 

        # Initialize players with strategies
        self.players = []
        strategies = {
            "Conservative": ConservativeStrategy(),
            "Aggressive": AggressiveStrategy(),
            "Bluffing": BluffingStrategy(),
            "Tight": TightStrategy(),
            "Random": RandomStrategy()
        }
        print(strategies.values())
        
        # Initialize players and their hands
        for strategy in strategies.values():
            player = Player(strategy=strategy, player_hands=[])
            self.players.append(player)
            self.players_hands.append([])

    def simulate_game(self):
        """Simulate a complete game of poker"""
        # Reset and reshuffle deck
        self.deck = Deck()
        self.deck.shuffle()
        self.betting_system.start_new_round()
        
        # Deal cards to players
        self.players_hands = [self.deck.deal(2) for _ in range(self.num_players)]
        for i, player in enumerate(self.players):
            player.player_hands = self.players_hands[i]
            
        self.community_cards = []

        # Game rounds
        for round_name in [BettingRound.PREFLOP, BettingRound.FLOP, 
                          BettingRound.TURN, BettingRound.RIVER]:
            self.current_round = round_name
            if round_name != BettingRound.PREFLOP:
                cards_to_deal = 3 if round_name == BettingRound.FLOP else 1
                self.community_cards.extend(self.deck.deal(cards_to_deal))
            self._handle_betting_round()

        # Evaluate hands and determine winner
        hand_strengths = [self.calculate_hand_score(hand + self.community_cards) 
                          for hand in self.players_hands]
        winner = int(np.argmax(hand_strengths))
        pot_size = self.betting_system.get_pot_size()
        self.betting_system.player_stacks[winner] += pot_size

        # Update player stats
        for i in range(self.num_players):
            self._update_player_stats(i, i == winner)

        return {
            "winner": winner,
            "profits": [self.betting_system.get_player_stack(i) - 1000 
                       for i in range(self.num_players)],
            "hand_strengths": hand_strengths,
            "betting_history": self.betting_system.get_betting_history(),
            "player_stats": [player.stats for player in self.players],
            "strategies": [player.strategy_name for player in self.players]
        }

    def _update_player_stats(self, player_idx, is_winner):
        """Update player statistics"""
        player = self.players[player_idx]
        position = self._get_position(player_idx)
        profit = self.betting_system.get_player_stack(player_idx) - 1000

        # Update basic stats
        player.stats["hands_dealt"] += 1
        player.stats["hands_played"] += 1
        if is_winner:
            player.stats["hands_won"] += 1
        player.stats["total_profit"] += profit

        # Update position stats
        pos_stats = player.stats["position_stats"][position]
        pos_stats["played"] += 1
        if is_winner:
            pos_stats["won"] += 1

        # Update bluff stats if applicable
        if self._was_bluff_attempted(player_idx):
            player.stats["bluffs_attempted"] += 1
            if self._was_bluff_successful(player_idx):
                player.stats["bluffs_successful"] += 1

    def calculate_hand_score(self, cards):
        """Calculate poker hand score"""
        values = [card.value for card in cards]
        suits = [card.suit for card in cards]
        value_counts = Counter(values)

        value_map = {'J': '11', 'Q': '12', 'K': '13', 'A': '14'}
        numeric_values = [int(value_map.get(v, v)) for v in values]
        numeric_values.sort()

        if len(set(suits)) == 1 and self.is_straight(numeric_values):
            return (9, numeric_values)
        # Four of a kind
        if 4 in value_counts.values():
            quad = max(int(value_map.get(k, k)) for k, v in value_counts.items() if v == 4)
            kicker = max(v for v in numeric_values if v != quad)
            return (8, [quad, kicker])
        # Full house
        if 3 in value_counts.values() and 2 in value_counts.values():
            trips = max(int(value_map.get(k, k)) for k, v in value_counts.items() if v == 3)
            pair = max(int(value_map.get(k, k)) for k, v in value_counts.items() if v == 2)
            return (7, [trips, pair])
        # Flush
        if len(set(suits)) == 1:
            return (6, numeric_values)
        # Straight
        if self.is_straight(numeric_values):
            return (5, numeric_values)
        # Three of a kind
        if 3 in value_counts.values():
            trips = max(int(value_map.get(k, k)) for k, v in value_counts.items() if v == 3)
            kickers = sorted((v for v in numeric_values if v != trips), reverse=True)
            return (4, [trips] + kickers)
        # Two pair
        if list(value_counts.values()).count(2) == 2:
            pairs = sorted((int(value_map.get(k, k)) for k, v in value_counts.items() if v == 2), reverse=True)
            kicker = max(v for v in numeric_values if v not in pairs)
            return (3, pairs + [kicker])
        # One pair
        if 2 in value_counts.values():
            pair = max(int(value_map.get(k, k)) for k, v in value_counts.items() if v == 2)
            kickers = sorted((v for v in numeric_values if v != pair), reverse=True)
            return (2, [pair] + kickers)
        # High card
        return (1, numeric_values)

    def is_straight(self, values):
        if len(values) < 5:
            return False
        for i in range(len(values) - 4):
            if values[i+4] - values[i] == 4:
                return True
        return False

    def monte_carlo_probability(self, community_cards: List[Card], num_simulations: int, num_threads: int):
        """
        Run Monte Carlo simulations to calculate win probabilities for each player
        
        Args:
            community_cards: List of community cards already dealt
            num_simulations: Number of simulations to run
            num_threads: Number of threads to use for parallel processing
            
        Returns:
            Dictionary with probabilities, confidence intervals, and player stats
        """
        import random
        import numpy as np
        from scipy import stats
        from concurrent.futures import ThreadPoolExecutor
        
        num_players = self.num_players
        win_counts = [0] * num_players
        player_profits = [[] for _ in range(num_players)]
        
        # Create a copy of the current deck to avoid modifying the original
        original_deck = self.deck
        
        # Function to run a single simulation
        def run_single_simulation(sim_index):
            # Create a new deck for this simulation
            sim_deck = Deck()
            
            # Remove cards that are already in players' hands or community
            for player_hand in self.players_hands:
                for card in player_hand:
                    sim_deck.remove_card(card)
            
            for card in community_cards:
                sim_deck.remove_card(card)
            
            sim_deck.shuffle()
            
            # Complete the community cards if needed
            remaining_community = 5 - len(community_cards)
            sim_community_cards = community_cards.copy()
            if remaining_community > 0:
                sim_community_cards.extend(sim_deck.deal(remaining_community))
            
            # Calculate hand strengths for each player
            hand_strengths = [self.calculate_hand_score(hand + sim_community_cards) 
                             for hand in self.players_hands]
            
            # Find all players with the maximum hand strength (to handle ties)
            max_strength = max(hand_strengths)
            max_indices = [i for i, strength in enumerate(hand_strengths) if strength == max_strength]
            
            # Randomly select a winner from players with the highest hand strength
            winner = random.choice(max_indices)
            
            # Calculate profits (simplified)
            profits = [-10 if i != winner else 10 * (num_players - 1) for i in range(num_players)]
            
            return winner, profits, hand_strengths
        
        # Run simulations in parallel if num_threads > 1
        if num_threads > 1 and num_simulations > 1:
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                results = list(executor.map(run_single_simulation, range(num_simulations)))
                
                for winner, profits, _ in results:
                    win_counts[winner] += 1
                    for i, profit in enumerate(profits):
                        player_profits[i].append(profit)
        else:
            # Run simulations sequentially
            for _ in range(num_simulations):
                winner, profits, _ = run_single_simulation(0)
                win_counts[winner] += 1
                for i, profit in enumerate(profits):
                    player_profits[i].append(profit)
        
        # Calculate win probabilities
        win_probabilities = [count / num_simulations for count in win_counts]
        
        # Calculate confidence intervals (95%)
        confidence_intervals = []
        for i in range(num_players):
            # Use binomial proportion confidence interval
            if num_simulations > 0:
                interval = stats.binom.interval(0.95, num_simulations, win_probabilities[i])
                confidence_intervals.append((interval[0] / num_simulations, interval[1] / num_simulations))
            else:
                confidence_intervals.append((0, 0))
        
        # Calculate player statistics based on simulation results
        player_stats = []
        for i, player in enumerate(self.players):
            # Use actual simulation data for statistics
            hands_dealt = num_simulations
            hands_played = num_simulations  # Assuming all hands are played
            hands_won = win_counts[i]
            
            # Calculate profit statistics
            profits = player_profits[i]
            total_profit = sum(profits) if profits else 0
            
            # Generate position-based statistics
            position = self._get_position(i)
            position_stats = {
                "early": {"played": 0, "won": 0},
                "middle": {"played": 0, "won": 0},
                "late": {"played": 0, "won": 0}
            }
            
            # Set the actual position stats
            position_stats[position]["played"] = num_simulations
            position_stats[position]["won"] = win_counts[i]
            
            # Get bluff statistics from player object if available
            bluffs_attempted = getattr(player, "stats", {}).get("bluffs_attempted", 0)
            bluffs_successful = getattr(player, "stats", {}).get("bluffs_successful", 0)
            
            stats = {
                "hands_played": hands_played,
                "hands_won": hands_won,
                "hands_dealt": hands_dealt,
                "total_profit": total_profit,
                "bluffs_attempted": bluffs_attempted,
                "bluffs_successful": bluffs_successful,
                "position_stats": position_stats
            }
            player_stats.append(stats)
        
        return {
            "probabilities": win_probabilities,
            "confidence_intervals": confidence_intervals,
            "player_stats": player_stats,
            "strategies": [player.strategy_name for player in self.players]
        }
        
    def _handle_betting_round(self):
        """Handle a betting round in the poker game"""
        # Get current player positions
        positions = [self._get_position(i) for i in range(self.num_players)]
        
        # For each player, make a decision based on their strategy
        for i, player in enumerate(self.players):
            # Skip players who have folded
            if self.betting_system.has_folded(i):
                continue
                
            # Get player's hand and current community cards
            hand = self.players_hands[i]
            
            # Get betting context
            context = {
                "position": positions[i],
                "round": self.current_round,
                "pot_size": self.betting_system.get_pot_size(),
                "current_bet": self.betting_system.get_current_bet(),
                "player_stack": self.betting_system.get_player_stack(i),
                "betting_history": self.betting_system.get_betting_history()
            }
            
            # Get decision from player's strategy
            pot_size = context["pot_size"]
            current_bet = context["current_bet"]
            player_stack = context["player_stack"]
            
            # Call make_decision with the correct parameters
            action, amount = player.strategy.make_decision(hand, self.community_cards, pot_size, current_bet, player_stack)
            
            # Apply decision to betting system
            if action == "fold":
                self.betting_system.fold(i)
            elif action == "check":
                self.betting_system.check(i)
            elif action == "call":
                self.betting_system.call(i)
            elif action == "raise":
                self.betting_system.raise_bet(i, amount)
    
    def _get_position(self, player_idx):
        """Get the position of a player (early, middle, late)"""
        if player_idx < self.num_players // 3:
            return "early"
        elif player_idx < 2 * self.num_players // 3:
            return "middle"
        else:
            return "late"
    
    def _was_bluff_attempted(self, player_idx):
        """Check if a player attempted to bluff"""
        # Simple implementation - consider it a bluff if player raised with a weak hand
        hand_score = self.calculate_hand_score(self.players_hands[player_idx] + self.community_cards)
        betting_history = self.betting_system.get_betting_history()
        
        # Check if player raised in any round
        for round_history in betting_history.values():
            if player_idx in round_history and round_history[player_idx]["action"] == "raise" and hand_score < 4:
                return True
        return False
    
    def _was_bluff_successful(self, player_idx):
        """Check if a player's bluff was successful"""
        # Consider bluff successful if player won with a weak hand
        hand_score = self.calculate_hand_score(self.players_hands[player_idx] + self.community_cards)
        hand_strengths = [self.calculate_hand_score(hand + self.community_cards) for hand in self.players_hands]
        winner = int(np.argmax(hand_strengths))
        
        return winner == player_idx and hand_score < 4

    # Other necessary methods...
