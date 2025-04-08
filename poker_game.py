import random
from collections import Counter

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
    def __init__(self, num_players):
        self.num_players = num_players
        self.deck = Deck()
        self.players_hands = []
    
    def simulate_game(self):
        self.deck.shuffle()
        self.players_hands = [self.deck.deal(2) for _ in range(self.num_players)]
        community_cards = self.deck.deal(5)
        
        # Calculate final hand strengths
        hand_strengths = []
        for hand in self.players_hands:
            all_cards = hand + community_cards
            score = self.calculate_hand_score(all_cards)
            hand_strengths.append(score)
        
        # Find winner (index of highest strength)
        winner = int(hand_strengths.index(max(hand_strengths)))
        
        # Calculate profits (simplified)
        profits = [-10] * self.num_players  # Everyone loses 10 by default
        profits[winner] = 10 * (self.num_players - 1)  # Winner takes all
        
        # Return dictionary with game results
        return {
            "winner": winner,
            "profits": profits,
            "hand_strengths": hand_strengths
        }
    
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