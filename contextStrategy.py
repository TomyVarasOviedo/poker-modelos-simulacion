from interfaceStrategy import InterfaceStrategy

class contextStrategy:
    def __init__(self, strategy):
        self.strategy = strategy

    def setStrategy(self, newStrategy):
        self.strategy = newStrategy
    
    def startStrategy(self) -> None:
        self.strategy.execute_strategy()