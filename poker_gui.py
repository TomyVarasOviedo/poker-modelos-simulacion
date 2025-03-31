import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from poker_game import PokerGame
from card_utils import CardDisplay

class PokerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Texas Hold'em Simulator")
        self.root.geometry("1024x768")
        
        # Game state
        self.current_stage = "Pre-Flop"
        self.game = None
        self.community_cards = []
        self.card_display = CardDisplay()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Top section - Game controls
        self.setup_controls()
        
        # Middle section - Community cards
        self.setup_community_cards()
        
        # Bottom section - Player hands
        self.setup_player_section()
        
        # Status bar
        self.setup_status_bar()
        
    def setup_controls(self):
        control_frame = ttk.LabelFrame(self.main_container, text="Game Controls", padding=10)
        control_frame.pack(fill="x", pady=(0, 10))
        
        # Left side - Game settings
        settings_frame = ttk.Frame(control_frame)
        settings_frame.pack(side="left")
        
        ttk.Label(settings_frame, text="Players:").pack(side="left")
        self.num_players = ttk.Spinbox(settings_frame, from_=2, to=8, width=5)
        self.num_players.set(4)
        self.num_players.pack(side="left", padx=5)
        
        # Right side - Stage controls
        stages_frame = ttk.Frame(control_frame)
        stages_frame.pack(side="right")
        
        self.stage_label = ttk.Label(stages_frame, text="Stage: Pre-Flop")
        self.stage_label.pack(side="left", padx=10)
        
        ttk.Button(control_frame, text="New Game", command=self.new_game).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Deal Flop", command=lambda: self.next_stage("Flop")).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Deal Turn", command=lambda: self.next_stage("Turn")).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Deal River", command=lambda: self.next_stage("River")).pack(side="left", padx=5)
        
    def setup_community_cards(self):
        self.community_frame = ttk.LabelFrame(self.main_container, text="Community Cards", padding=10)
        self.community_frame.pack(fill="x", pady=(0, 10))
        
        # Placeholders for community cards
        self.card_labels = []
        for _ in range(5):
            label = ttk.Label(self.community_frame, text=self.card_display.card_back, 
                            font=('Arial', 40))
            label.pack(side="left", padx=10)
            self.card_labels.append(label)
            
    def setup_player_section(self):
        self.players_frame = ttk.LabelFrame(self.main_container, text="Players", padding=10)
        self.players_frame.pack(fill="both", expand=True)
        
        # Will be populated when game starts
        self.player_frames = []
        
    def setup_status_bar(self):
        self.status_bar = ttk.Label(self.root, text="Ready to start", relief="sunken")
        self.status_bar.pack(fill="x", side="bottom", pady=5)
        
    def new_game(self):
        # Clear previous game state
        for frame in self.player_frames:
            frame.destroy()
        self.player_frames.clear()
        
        # Reset community cards
        for label in self.card_labels:
            label.config(text=self.card_display.card_back)
            
        # Initialize new game
        num_players = int(self.num_players.get())
        self.game = PokerGame(num_players)
        self.game.simulate_game()
        
        # Setup player frames
        self.setup_players()
        
        # Update status
        self.current_stage = "Pre-Flop"
        self.stage_label.config(text="Stage: Pre-Flop")
        self.status_bar.config(text="New game started")
        
    def setup_players(self):
        for i, hand in enumerate(self.game.players_hands):
            player_frame = ttk.Frame(self.players_frame)
            player_frame.pack(fill="x", pady=2)
            
            ttk.Label(player_frame, text=f"Player {i+1}").pack(side="left")
            
            # Create card symbols for player's hand
            hand_frame = ttk.Frame(player_frame)
            hand_frame.pack(side="left", padx=10)
            
            for card in hand:
                card_label = ttk.Label(hand_frame, 
                                     text=self.card_display.get_card_symbol(card),
                                     font=('Arial', 40))
                card_label.pack(side="left", padx=2)
            
            prob_label = ttk.Label(player_frame, text="Win Probability: --")
            prob_label.pack(side="right")
            
            self.player_frames.append(player_frame)
            
    def next_stage(self, stage):
        if not self.game:
            self.status_bar.config(text="Please start a new game first")
            return
            
        stages = {"Flop": (0, 3), "Turn": (3, 4), "River": (4, 5)}
        if stage in stages:
            start, end = stages[stage]
            for i in range(start, end):
                card = self.game.deck.cards[i]
                self.card_labels[i].config(text=self.card_display.get_card_symbol(card))
                
        self.current_stage = stage
        self.stage_label.config(text=f"Stage: {stage}")
        self.update_probabilities()
        
    def update_probabilities(self):
        if not self.game:
            return
            
        visible_cards = []
        if self.current_stage == "Pre-Flop":
            visible_cards = []
        elif self.current_stage == "Flop":
            visible_cards = self.game.deck.cards[:3]
        elif self.current_stage == "Turn":
            visible_cards = self.game.deck.cards[:4]
        elif self.current_stage == "River":
            visible_cards = self.game.deck.cards[:5]
            
        probabilities = self.game.monte_carlo_probability(visible_cards)
        
        # Update probability labels with more detail
        for i, prob in enumerate(probabilities):
            prob_label = self.player_frames[i].winfo_children()[-1]
            if prob > 0.01:  # Only show significant probabilities
                prob_label.config(text=f"Win Probability: {prob:.1%}")
            else:
                prob_label.config(text="Win Probability: <1%")

def main():
    root = tk.Tk()
    app = PokerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()