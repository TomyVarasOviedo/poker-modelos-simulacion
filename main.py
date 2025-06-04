from poker_game import PokerGame
from poker_gui import PokerGUI
import tkinter as tk
import ttkbootstrap as ttk

def run_console_mode():
    final_result=[]
    strategies = [
                'Conservative',
                "Aggressive",
                "Bluffing",
                "Tight",
                "Random"
    ]

    profit_by_strategy = {strategy: 0 for strategy in strategies}

    game = PokerGame(4)
    results = game.simulate_game()
    for winner in results['winner']:
        final_result.append(winner)
        results = game.simulate_game()
    # Aggregate profit for each player by their strategy
    for strat, profit in zip(results['players_strategies'], results['profits']):
        profit_by_strategy[strat] += profit

    for strategy in strategies:
        avg_profit = profit_by_strategy[strategy] / 10000
        print(f"Strategy: {strategy}")
        print(f"Win Rate: {final_result.count(strategy) / len(final_result) * 100:.2f}%")
        print(f"Average Profit per Game: {avg_profit:.2f}")
        
def run_gui_mode():
    # Use ttkbootstrap Window with theme
    root = ttk.Window(themename="darkly")
    app = PokerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--console':
        run_console_mode()
    else:
        run_gui_mode()
 