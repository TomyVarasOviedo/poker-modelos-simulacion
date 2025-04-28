from strategies.BasePokerStrategy import BasePokerStrategy

class Player:

    def __init__(self, strategy: BasePokerStrategy):
        self.strategy = strategy