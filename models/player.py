from strategies.BasePokerStrategy import BasePokerStrategy

class Player:
    strategy: BasePokerStrategy
    
    def __init__(self, strategy: BasePokerStrategy):
        self.strategy = strategy