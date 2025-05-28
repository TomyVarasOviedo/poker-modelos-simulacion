from poker_game import PokerGame
from poker_gui import PokerGUI
import tkinter as tk
import ttkbootstrap as ttk

def run_console_mode():
    game = PokerGame(4)
    results = game.simulate_game()
    print(f"\nWinner: Player {results['winner'] + 1}")
    print(f"Profits: {results['profits']}")
    print(f"Hand strengths: {results['hand_strengths']}")

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
