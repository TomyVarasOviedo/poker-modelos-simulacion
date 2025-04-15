import random
from collections import Counter
from models.betting_system import BettingSystem, BettingRound
from models.player_profile import PlayerProfile

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
    
    def __str__(self):
        return f"{self.value} of {self.suit}"
    
    def __eq__(self, other):
        if isinstance(other, Card):
            return self.suit == other.suit and self.value == other.value
        return False

class Deck:
    def __init__(self):
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.cards = [Card(suit, value) for suit in suits for value in values]
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def deal(self, num_cards):
        return [self.cards.pop() for _ in range(num_cards)]

    def remove_card(self, target_card):
        for card in self.cards[:]:
            if card.suit == target_card.suit and card.value == target_card.value:
                self.cards.remove(card)
                return

class PokerGame:
    def __init__(self, num_players, initial_stack=1000):
        self.num_players = num_players
        self.deck = Deck()
        self.players_hands = []
        self.betting_system = BettingSystem(num_players, initial_stack)
        self.current_round = BettingRound.PREFLOP
        self.player_profiles = []
        # Initialize profiles for each strategy
        for strategy in ["Conservative", "Aggressive", "Bluffing", "Tight", "Random"]:
            self.add_player(strategy)

    def add_player(self, strategy_name: str):
        """Add a player with their profile"""
        profile = PlayerProfile(strategy_name)
        self.player_profiles.append(profile)

    def simulate_game(self):
        self.deck.shuffle()
        self.betting_system.start_new_round()
        self.players_hands = [self.deck.deal(2) for _ in range(self.num_players)]
        community_cards = []

        # Preflop betting
        self._handle_betting_round()
        
        # Flop
        community_cards.extend(self.deck.deal(3))
        self.current_round = BettingRound.FLOP
        self._handle_betting_round()
        
        # Turn
        community_cards.extend(self.deck.deal(1))
        self.current_round = BettingRound.TURN
        self._handle_betting_round()
        
        # River
        community_cards.extend(self.deck.deal(1))
        self.current_round = BettingRound.RIVER
        self._handle_betting_round()

        # Evaluate hands and determine winner
        hand_strengths = []
        for hand in self.players_hands:
            all_cards = hand + community_cards
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
                community_cards,
                self.betting_system.get_pot_size(),
                self.betting_system.current_bet,
                self.betting_system.get_player_stack(i)
            )
            
            self.betting_system.handle_action(i, action, amount)

    def monte_carlo_probability(self, community_cards, num_simulations=1000):
        wins = [0] * self.num_players
        ties = [0] * self.num_players
        remaining_community = 5 - len(community_cards)
        
        for _ in range(num_simulations):
            # Create a temporary deck without known cards
            temp_deck = Deck()
            
            # Remove known cards
            for hand in self.players_hands:
                for card in hand:
                    temp_deck.remove_card(card)
            for card in community_cards:
                temp_deck.remove_card(card)
            
            # Deal remaining community cards
            temp_deck.shuffle()
            simulated_community = community_cards + temp_deck.deal(remaining_community)
            
            # Calculate scores for all players
            scores = []
            for hand in self.players_hands:
                all_cards = hand + simulated_community
                score = self.calculate_hand_score(all_cards)
                scores.append(score)
            
            # Find winner(s)
            max_score = max(scores)
            winners = [i for i, score in enumerate(scores) if score == max_score]
            
            # Update wins and ties
            if len(winners) == 1:
                wins[winners[0]] += 1
            else:
                # Split the win among tied players
                for winner in winners:
                    ties[winner] += 1
        
        # Calculate final probabilities including ties
        probabilities = [(wins[i] + ties[i]/2)/num_simulations for i in range(self.num_players)]
        
        return probabilities
    
    def evaluate_hands(self, community_cards):
        scores = []
        for hand in self.players_hands:
            all_cards = hand + community_cards
            score = self.calculate_hand_score(all_cards)
            scores.append(score)
        return scores.index(max(scores))
    
    def calculate_hand_score(self, cards):
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
        """Determine player's position"""
        positions = ["early", "middle", "late"]
        position_idx = (player_idx * len(positions)) // self.num_players
        return positions[position_idx]

    def _was_bluff_attempted(self, player_idx: int) -> bool:
        """Determine if player attempted to bluff"""
        actions = self.betting_system.get_player_actions(player_idx)
        hand_strength = self.calculate_hand_score(self.players_hands[player_idx])
        return any(action["type"] == "raise" and hand_strength < 5 for action in actions)

    def _was_bluff_successful(self, player_idx: int) -> bool:
        """Determine if bluff was successful"""
        return self._was_bluff_attempted(player_idx) and player_idx == winner

    def _get_hand_type(self, hand_strength: int) -> str:
        """Get the type of hand based on its strength"""
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