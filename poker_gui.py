from analytics.poker_analytics import PokerAnalytics
from gui.poker_visualizer import PokerVisualizer
# Import here to avoid circular imports
#from main import PokerSimulator
# Run simulation in a separate thread to avoid GUI freezing
import threading
from poker_simulate import PokerSimulator
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import webbrowser
from typing import Dict
from dataclasses import dataclass
import json
import os


@dataclass
class SimulationConfig:
    num_players: int = 5
    num_games: int = 1000
    num_threads: int = 4
    sample_games: int = 100

class PokerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Poker Strategy Simulator")
        self.root.geometry("1400x900")

        # Initialize style with ttkbootstrap
        self.style = ttk.Style()

        # Try to set icon, handle different platforms
        try:
            # For Windows
            self.root.iconbitmap("poker_img.ico")
        except:
            # For Linux/Unix
            try:
                self.root.iconbitmap('@poker_img.xbm')
            except:
                pass

        # Configure custom styles
        self.style.configure('Title.TLabel',
                             font=('Helvetica', 24, 'bold'),
                             foreground='#00bc8c')

        self.style.configure('Subtitle.TLabel',
                             font=('Helvetica', 12),
                             foreground='#6c757d')

        # Create header
        header = ttk.Frame(self.root, padding="20 20 20 0")
        header.pack(fill=X)

        ttk.Label(header, text="Poker Strategy Simulator",
                  style='Title.TLabel').pack(side=LEFT)

        ttk.Label(header, text="Analyze different poker strategies in simulated games",
                  style='Subtitle.TLabel').pack(side=LEFT, padx=20)

        # Main containers with improved styling
        self.control_frame = ttk.LabelFrame(
            self.root,
            text="Simulation Controls",
            padding=20,
            bootstyle="default"
        )
        self.control_frame.pack(fill=X, padx=20, pady=(10, 20))

        self.results_frame = ttk.LabelFrame(
            self.root,
            text="Simulation Results",
            padding=20,
            bootstyle="default"
        )
        self.results_frame.pack(fill=BOTH, expand=YES, padx=20, pady=(0, 20))

        self._create_controls()
        self._create_results_view()
        self._add_tooltips()

    def _create_controls(self):
        controls = ttk.Frame(self.control_frame)
        controls.pack(fill=X, expand=YES)

        # Left side - Input controls
        input_frame = ttk.Frame(controls)
        input_frame.pack(side=LEFT, fill=X, expand=YES)

        # Games input with validation
        games_frame = ttk.Frame(input_frame)
        games_frame.pack(side=LEFT, padx=20)

        ttk.Label(games_frame, text="Number of Games",
                  font=("Helvetica", 10, "bold")).pack(anchor=W)
        self.num_games = ttk.Entry(games_frame, width=10,
                                   bootstyle="default")
        self.num_games.insert(0, "1000")
        self.num_games.pack(pady=5)

        # Threads input with validation
        threads_frame = ttk.Frame(input_frame)
        threads_frame.pack(side=LEFT, padx=20)

        ttk.Label(threads_frame, text="Number of Threads",
                  font=("Helvetica", 10, "bold")).pack(anchor=W)
        self.num_threads = ttk.Entry(threads_frame, width=5,
                                     bootstyle="default")
        self.num_threads.insert(0, "4")
        self.num_threads.pack(pady=5)

        # Right side - Action buttons
        button_frame = ttk.Frame(controls)
        button_frame.pack(side=RIGHT, padx=20)

        self.start_btn = ttk.Button(
            button_frame,
            text="Start Simulation",
            command=self._run_simulation,
            bootstyle="success-outline",
            width=15
        )
        self.start_btn.pack(side=LEFT, padx=5)
        
        # Save/Load buttons
        self.save_btn = ttk.Button(
            button_frame,
            text="Save Results",
            command=self._save_results,
            bootstyle="info-outline",
            width=15,
            state="disabled"  # Initially disabled until simulation runs
        )
        self.save_btn.pack(side=LEFT, padx=5)
        
        self.load_btn = ttk.Button(
            button_frame,
            text="Load Results",
            command=self._load_results,
            bootstyle="info-outline",
            width=15
        )
        self.load_btn.pack(side=LEFT, padx=5)

        # Progress bar with label
        progress_frame = ttk.Frame(controls)
        progress_frame.pack(side=RIGHT, padx=20, fill=X, expand=YES)

        self.progress = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=300,
            bootstyle="success-striped"
        )
        self.progress.pack(side=LEFT, padx=5)
        
        # Status label for real-time updates
        self.status_label = ttk.Label(
            progress_frame,
            text="Ready",
            font=("Helvetica", 9),
            bootstyle="secondary"
        )
        self.status_label.pack(side=LEFT, padx=5)

    def _create_results_view(self):
        # Create notebook with custom styling
        self.notebook = ttk.Notebook(
            self.results_frame,
            bootstyle="dark"
        )
        self.notebook.pack(fill=BOTH, expand=YES, padx=5, pady=5)

        # Statistics tab
        self.stats_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.stats_frame, text="Statistics")

        # Overview tab for graphs
        self.overview_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.overview_frame, text="Overview")
        
        # Strategy Comparison tab
        self.comparison_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.comparison_frame, text="Strategy Comparison")
        
        # Hand Replayer tab
        self.replayer_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.replayer_frame, text="Hand Replayer")

        # Style graphs
        self.figure, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 5))
        self.figure.patch.set_facecolor("#202020")

        # Create matplotlib figure and axes
        self.canvas = FigureCanvasTkAgg(self.figure, self.overview_frame)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=YES)
        
        # Setup the strategy comparison tab
        self._setup_comparison_tab()
        
        # Setup the hand replayer tab
        self._setup_replayer_tab()

        # Configure Treeview styles
        self.style.configure(
            "Treeview",
            background="#2f3136",
            foreground="white",
            fieldbackground="#2f3136",
            rowheight=25)
        self.style.configure(
            "Treeview.Heading",
            background="#212529",
            foreground="white",
            relief="flat")

        # Summary statistics with headers
        ttk.Label(
            self.stats_frame,
            text="Summary Statistics",
            style='Subtitle.TLabel'
        ).pack(anchor=W, pady=(0, 5))
        self.summary_tree = ttk.Treeview(
            self.stats_frame,
            columns=("Metric", "Value"),
            show="headings", height=5)
        self._configure_treeview(self.summary_tree)
        self.summary_tree.pack(fill=X, pady=(0, 10))

        # Detailed statistics with headers
        ttk.Label(
            self.stats_frame,
            text="Detailed Statistics",
            style='Subtitle.TLabel'
        ).pack(anchor=W, pady=(10, 5))
        self.stats_tree = ttk.Treeview(
            self.stats_frame, columns=(
                "Strategy", "Wins", "Win Rate", "Avg Profit", "Std Dev"),
            show="headings")
        self._configure_treeview(self.stats_tree)
        self.stats_tree.pack(fill=BOTH, expand=YES)

        # Add Player Statistics section
        ttk.Label(
            self.stats_frame,
            text="Player Statistics",
            style='Subtitle.TLabel'
        ).pack(anchor=W, pady=(10, 5))
        self.player_stats_tree = ttk.Treeview(
            self.stats_frame, columns=(
                "Strategy",
                "Hands Played",
                "Win Rate",
                "Total Profit",
                "Bluff Rate",
                "Position Stats"), show="headings", height=5)
        self._configure_treeview(self.player_stats_tree)

        # Adjust column widths for better visibility
        self.player_stats_tree.column("Strategy", width=100)
        self.player_stats_tree.column("Hands Played", width=100)
        self.player_stats_tree.column("Win Rate", width=80)
        self.player_stats_tree.column("Total Profit", width=100)
        self.player_stats_tree.column("Bluff Rate", width=80)
        self.player_stats_tree.column("Position Stats", width=200)
        self.player_stats_tree.pack(fill=X, pady=(0, 10))

        # Add Interactive Analysis tab
        self.analysis_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.analysis_frame, text="Interactive Analysis")

        # Create placeholder for Plotly figure
        self.plotly_widget = None

    def _configure_treeview(self, tree):
        """Configure consistent treeview styling"""
        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100)

        # Add stripes to rows
        tree.tag_configure('oddrow', background='#2a2d31')
        tree.tag_configure('evenrow', background='#2f3136')

    def _run_simulation(self):
        """Start the simulation with selected parameters"""
        try:
            num_games = int(self.num_games.get())
            num_threads = int(self.num_threads.get())
            
            if num_games <= 0 or num_threads <= 0:
                messagebox.showerror("Invalid Input", "Number of games and threads must be positive integers.")
                return
                
            # Disable controls during simulation
            self.start_btn.configure(state="disabled")
            self.load_btn.configure(state="disabled")
            self.progress["value"] = 0
            self.status_label.configure(text="Initializing simulation...")
            
            print(f"{num_games} games will be simulated using {num_threads} threads...")
            config = SimulationConfig(num_games=num_games, num_threads=num_threads)
            
            # Update progress periodically during simulation
            def update_progress(step, total_steps):
                progress_pct = int((step / total_steps) * 100)
                self.progress["value"] = progress_pct
                self.status_label.configure(text=f"Simulating... {progress_pct}% complete ({step}/{total_steps} games)")
                self.root.update_idletasks()
            
            # Start simulation in a separate thread to avoid freezing the UI
            def run_simulation_thread():
                try:
                    # Create simulator with config
                    simulate = PokerSimulator(config)
                    
                    # Set up progress tracking
                    total_steps = num_games
                    progress_interval = max(1, total_steps // 20)  # Update progress ~20 times
                    
                    # Define a callback to track simulation progress
                    class ProgressTracker:
                        def __init__(self):
                            self.completed = 0
                        
                        def update(self):
                            self.completed += 1
                            if self.completed % progress_interval == 0 or self.completed == total_steps:
                                self.root.after(0, lambda: update_progress(self.completed, total_steps))
                    
                    # Create progress tracker
                    tracker = ProgressTracker()
                    tracker.root = self.root
                    
                    # Initial progress update
                    self.root.after(0, lambda: update_progress(0, total_steps))
                    
                    # Run the actual simulation
                    # In a real implementation, we would need to modify the simulator to call
                    # the progress callback after each simulation, but for now we'll update at the end
                    results = simulate.run_threaded_simulation()
                    
                    # Final progress update
                    self.root.after(0, lambda: update_progress(total_steps, total_steps))
                    
                    # Update UI with results in the main thread
                    self.root.after(0, lambda: self._update_results(results))
                except Exception as e:
                    # Handle errors in the main thread
                    import traceback
                    traceback.print_exc()
                    self.root.after(0, lambda: self._handle_simulation_error(str(e)))
            
            # Start the simulation thread
            import threading
            simulation_thread = threading.Thread(target=run_simulation_thread)
            simulation_thread.daemon = True  # Thread will exit when main program exits
            simulation_thread.start()
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for games and threads.")
        except Exception as e:
            self._handle_simulation_error(str(e))
    
    def _handle_simulation_error(self, error_message):
        """Handle errors during simulation"""
        self.start_btn.configure(state="normal")
        self.load_btn.configure(state="normal")
        self.progress["value"] = 0
        self.status_label.configure(text="Error")
        messagebox.showerror("Simulation Error", f"An error occurred during simulation:\n{error_message}")
        print(f"Simulation error: {error_message}")
        
    def _compare_strategies(self):
        """Compare two selected strategies and display the results"""
        if not hasattr(self, 'current_results') or not self.current_results:
            messagebox.showinfo("No Data", "Please run a simulation first.")
            return
            
        strategy1 = self.strategy1_var.get()
        strategy2 = self.strategy2_var.get()
        
        if not strategy1 or not strategy2:
            messagebox.showinfo("Selection Required", "Please select two strategies to compare.")
            return
            
        # Clear previous comparison
        self.comparison_figure.clear()
        
        # Create analytics and dataframe if not already created
        analytics = PokerAnalytics()
        df = analytics.create_dataframe(self.current_results)
        
        # Filter data for the selected strategies
        strategy1_data = df[df['Strategy'] == strategy1]
        strategy2_data = df[df['Strategy'] == strategy2]
        
        if strategy1_data.empty or strategy2_data.empty:
            messagebox.showinfo("Data Error", "Could not find data for the selected strategies.")
            return
            
        # Update the strategy labels
        for widget in self.strategy1_stats.winfo_children():
            widget.destroy()
        for widget in self.strategy2_stats.winfo_children():
            widget.destroy()
            
        # Create labels for strategy 1
        self._create_strategy_stats(self.strategy1_stats, strategy1, strategy1_data)
        
        # Create labels for strategy 2
        self._create_strategy_stats(self.strategy2_stats, strategy2, strategy2_data)
        
        # Create radar chart for comparison
        self._create_radar_chart(strategy1, strategy2, strategy1_data, strategy2_data)
        
    def _create_strategy_stats(self, parent_frame, strategy_name, strategy_data):
        """Create statistics labels for a strategy"""
        # Calculate statistics
        win_rate = strategy_data['Win Rate'].mean()
        total_profit = strategy_data['Total Profit'].sum()
        avg_profit = strategy_data['Avg Profit'].mean()
        bluff_success = strategy_data['Bluff Success'].mean() if 'Bluff Success' in strategy_data else 0
        
        # Create labels with statistics
        ttk.Label(parent_frame, text=f"Strategy: {strategy_name}", font=("TkDefaultFont", 12, "bold")).pack(anchor=W, pady=(0, 10))
        ttk.Label(parent_frame, text=f"Win Rate: {win_rate:.4f}").pack(anchor=W, pady=2)
        ttk.Label(parent_frame, text=f"Total Profit: {total_profit:.2f}").pack(anchor=W, pady=2)
        ttk.Label(parent_frame, text=f"Average Profit: {avg_profit:.2f}").pack(anchor=W, pady=2)
        ttk.Label(parent_frame, text=f"Bluff Success Rate: {bluff_success:.4f}").pack(anchor=W, pady=2)
        
        # Add position statistics if available
        if 'Position Stats' in strategy_data.columns:
            ttk.Label(parent_frame, text="Position Performance:", font=("TkDefaultFont", 10, "bold")).pack(anchor=W, pady=(10, 5))
            position_stats = strategy_data['Position Stats'].iloc[0] if not strategy_data.empty else {}
            
            for position, stats in position_stats.items():
                if isinstance(stats, dict) and 'win_rate' in stats:
                    ttk.Label(parent_frame, text=f"{position}: {stats['win_rate']:.4f}").pack(anchor=W, pady=1)
        
    def _setup_replayer_tab(self):
        """Setup the hand replayer tab with controls and display area"""
        # Create a frame for the replayer controls
        controls_frame = ttk.Frame(self.replayer_frame)
        controls_frame.pack(fill=X, padx=5, pady=5)
        
        # Add navigation buttons
        self.prev_btn = ttk.Button(
            controls_frame,
            text="◀ Previous",
            command=self._prev_hand_step,
            state="disabled",
            bootstyle="secondary"
        )
        self.prev_btn.pack(side=LEFT, padx=5)
        
        self.next_btn = ttk.Button(
            controls_frame,
            text="Next ▶",
            command=self._next_hand_step,
            state="disabled",
            bootstyle="secondary"
        )
        self.next_btn.pack(side=LEFT, padx=5)
        
        # Add a slider for navigating through the hand
        self.step_var = tk.IntVar(value=0)
        self.step_slider = ttk.Scale(
            controls_frame,
            from_=0,
            to=0,
            variable=self.step_var,
            command=self._on_slider_change,
            bootstyle="success"
        )
        self.step_slider.pack(side=LEFT, fill=X, expand=YES, padx=10)
        
        # Add a label to show current step
        self.step_label = ttk.Label(controls_frame, text="Step: 0/0")
        self.step_label.pack(side=LEFT, padx=5)
        
        # Create a frame for the hand display
        display_frame = ttk.Frame(self.replayer_frame)
        display_frame.pack(fill=BOTH, expand=YES, padx=5, pady=10)
        
        # Split into table view and info view
        table_frame = ttk.LabelFrame(display_frame, text="Poker Table")
        table_frame.pack(fill=BOTH, expand=YES, padx=5, pady=5)
        
        info_frame = ttk.LabelFrame(display_frame, text="Hand Information")
        info_frame.pack(fill=BOTH, expand=YES, padx=5, pady=5)
        
        # Create a canvas for the poker table
        self.table_canvas = tk.Canvas(table_frame, bg="#076324", height=300)
        self.table_canvas.pack(fill=BOTH, expand=YES, padx=5, pady=5)
        
        # Create text widget for hand information
        self.hand_info = tk.Text(info_frame, height=10, wrap=WORD, state=DISABLED)
        self.hand_info.pack(fill=BOTH, expand=YES, padx=5, pady=5)
        
        # Add a button to load a sample hand
        self.load_sample_btn = ttk.Button(
            controls_frame,
            text="Load Sample Hand",
            command=self._load_sample_hand,
            bootstyle="info"
        )
        self.load_sample_btn.pack(side=RIGHT, padx=5)
        
        # Initialize hand data
        self.current_hand = None
        self.current_step = 0
        self.max_steps = 0
    
    def _load_sample_hand(self):
        """Load a sample hand for the replayer"""
        # Sample hand data structure
        self.current_hand = {
            'players': [
                {'name': 'Player 1', 'strategy': 'Aggressive', 'position': 'Button', 'stack': 1000},
                {'name': 'Player 2', 'strategy': 'Conservative', 'position': 'Small Blind', 'stack': 1200},
                {'name': 'Player 3', 'strategy': 'Tight', 'position': 'Big Blind', 'stack': 800},
                {'name': 'Player 4', 'strategy': 'Bluffing', 'position': 'UTG', 'stack': 1500}
            ],
            'community_cards': [],
            'pot': 0,
            'steps': [
                {
                    'description': 'Hand starts. Players receive their hole cards.',
                    'community_cards': [],
                    'player_cards': {
                        'Player 1': ['Ah', 'Kh'],
                        'Player 2': ['Jc', 'Jd'],
                        'Player 3': ['7s', '8s'],
                        'Player 4': ['2d', '5c']
                    },
                    'pot': 0,
                    'actions': []
                },
                {
                    'description': 'Pre-flop betting round.',
                    'community_cards': [],
                    'pot': 150,
                    'actions': [
                        {'player': 'Player 2', 'action': 'Small Blind', 'amount': 25},
                        {'player': 'Player 3', 'action': 'Big Blind', 'amount': 50},
                        {'player': 'Player 4', 'action': 'Fold', 'amount': 0},
                        {'player': 'Player 1', 'action': 'Raise', 'amount': 150},
                        {'player': 'Player 2', 'action': 'Call', 'amount': 125},
                        {'player': 'Player 3', 'action': 'Fold', 'amount': 0}
                    ]
                },
                {
                    'description': 'Flop is dealt.',
                    'community_cards': ['Ks', 'Qh', '10d'],
                    'pot': 150,
                    'actions': []
                },
                {
                    'description': 'Flop betting round.',
                    'community_cards': ['Ks', 'Qh', '10d'],
                    'pot': 350,
                    'actions': [
                        {'player': 'Player 2', 'action': 'Check', 'amount': 0},
                        {'player': 'Player 1', 'action': 'Bet', 'amount': 200},
                        {'player': 'Player 2', 'action': 'Call', 'amount': 200}
                    ]
                },
                {
                    'description': 'Turn is dealt.',
                    'community_cards': ['Ks', 'Qh', '10d', '2s'],
                    'pot': 350,
                    'actions': []
                },
                {
                    'description': 'Turn betting round.',
                    'community_cards': ['Ks', 'Qh', '10d', '2s'],
                    'pot': 750,
                    'actions': [
                        {'player': 'Player 2', 'action': 'Check', 'amount': 0},
                        {'player': 'Player 1', 'action': 'Bet', 'amount': 400},
                        {'player': 'Player 2', 'action': 'Call', 'amount': 400}
                    ]
                },
                {
                    'description': 'River is dealt.',
                    'community_cards': ['Ks', 'Qh', '10d', '2s', 'Ac'],
                    'pot': 750,
                    'actions': []
                },
                {
                    'description': 'River betting round.',
                    'community_cards': ['Ks', 'Qh', '10d', '2s', 'Ac'],
                    'pot': 1550,
                    'actions': [
                        {'player': 'Player 2', 'action': 'Check', 'amount': 0},
                        {'player': 'Player 1', 'action': 'Bet', 'amount': 800},
                        {'player': 'Player 2', 'action': 'Call', 'amount': 800}
                    ]
                },
                {
                    'description': 'Showdown. Player 1 wins with Ace-King pair (Broadway straight).',
                    'community_cards': ['Ks', 'Qh', '10d', '2s', 'Ac'],
                    'pot': 1550,
                    'actions': [
                        {'player': 'Player 1', 'action': 'Show', 'cards': ['Ah', 'Kh'], 'hand': 'Broadway Straight'},
                        {'player': 'Player 2', 'action': 'Show', 'cards': ['Jc', 'Jd'], 'hand': 'Pair of Jacks'},
                        {'player': 'Player 1', 'action': 'Win', 'amount': 1550}
                    ]
                }
            ]
        }
        
        # Update the slider and controls
        self.max_steps = len(self.current_hand['steps']) - 1
        self.step_slider.configure(to=self.max_steps)
        self.step_var.set(0)
        self.current_step = 0
        self.step_label.configure(text=f"Step: {self.current_step}/{self.max_steps}")
        
        # Enable navigation buttons
        self.prev_btn.configure(state="disabled")
        self.next_btn.configure(state="normal")
        
        # Display the first step
        self._display_hand_step(0)
    
    def _on_slider_change(self, value):
        """Handle slider value change"""
        step = int(float(value))
        if step != self.current_step:
            self.current_step = step
            self._display_hand_step(step)
            self.step_label.configure(text=f"Step: {step}/{self.max_steps}")
            
            # Update button states
            self.prev_btn.configure(state="normal" if step > 0 else "disabled")
            self.next_btn.configure(state="normal" if step < self.max_steps else "disabled")
    
    def _prev_hand_step(self):
        """Navigate to the previous step in the hand"""
        if self.current_step > 0:
            self.current_step -= 1
            self.step_var.set(self.current_step)
            self._display_hand_step(self.current_step)
            self.step_label.configure(text=f"Step: {self.current_step}/{self.max_steps}")
            
            # Update button states
            self.prev_btn.configure(state="normal" if self.current_step > 0 else "disabled")
            self.next_btn.configure(state="normal")
    
    def _next_hand_step(self):
        """Navigate to the next step in the hand"""
        if self.current_step < self.max_steps:
            self.current_step += 1
            self.step_var.set(self.current_step)
            self._display_hand_step(self.current_step)
            self.step_label.configure(text=f"Step: {self.current_step}/{self.max_steps}")
            
            # Update button states
            self.prev_btn.configure(state="normal")
            self.next_btn.configure(state="normal" if self.current_step < self.max_steps else "disabled")
    
    def _display_hand_step(self, step_index):
        """Display the current step of the hand"""
        if not self.current_hand or step_index > self.max_steps:
            return
            
        step = self.current_hand['steps'][step_index]
        
        # Clear the canvas
        self.table_canvas.delete("all")
        
        # Draw the poker table (oval)
        table_width = self.table_canvas.winfo_width() or 400
        table_height = self.table_canvas.winfo_height() or 300
        padding = 50
        self.table_canvas.create_oval(
            padding, padding, 
            table_width - padding, table_height - padding, 
            fill="#076324", outline="#8B4513", width=10
        )
        
        # Draw pot in the middle
        pot_text = f"Pot: ${step['pot']}"
        self.table_canvas.create_text(
            table_width // 2, table_height // 2,
            text=pot_text, fill="white", font=("Arial", 14, "bold")
        )
        
        # Draw community cards
        if step['community_cards']:
            card_width = 30
            card_height = 40
            card_spacing = 5
            total_width = len(step['community_cards']) * (card_width + card_spacing) - card_spacing
            start_x = (table_width - total_width) // 2
            y = table_height // 2 - 50
            
            for i, card in enumerate(step['community_cards']):
                x = start_x + i * (card_width + card_spacing)
                self._draw_card(x, y, card_width, card_height, card)
        
        # Draw players around the table
        num_players = len(self.current_hand['players'])
        center_x = table_width // 2
        center_y = table_height // 2
        radius = min(table_width, table_height) // 2 - padding - 20
        
        for i, player in enumerate(self.current_hand['players']):
            angle = 2 * np.pi * i / num_players - np.pi / 2  # Start from top and go clockwise
            x = center_x + radius * np.cos(angle)
            y = center_y + radius * np.sin(angle)
            
            # Draw player position
            self.table_canvas.create_text(
                x, y - 40,
                text=player['position'],
                fill="white", font=("Arial", 10)
            )
            
            # Draw player name and stack
            self.table_canvas.create_text(
                x, y - 25,
                text=f"{player['name']} (${player['stack']})",
                fill="white", font=("Arial", 10, "bold")
            )
            
            # Draw player cards if available in this step
            if 'player_cards' in step and player['name'] in step['player_cards']:
                cards = step['player_cards'][player['name']]
                card_width = 25
                card_height = 35
                card_spacing = 3
                
                # Draw first card
                self._draw_card(x - card_width - card_spacing//2, y, card_width, card_height, cards[0])
                
                # Draw second card
                self._draw_card(x + card_spacing//2, y, card_width, card_height, cards[1])
        
        # Update the hand information text
        self.hand_info.configure(state=NORMAL)
        self.hand_info.delete(1.0, END)
        
        # Add step description
        self.hand_info.insert(END, f"Step {step_index + 1}: {step['description']}\n\n", "bold")
        
        # Add actions
        if step['actions']:
            self.hand_info.insert(END, "Actions:\n", "bold")
            for action in step['actions']:
                if action['action'] == 'Show':
                    self.hand_info.insert(END, f"  {action['player']} shows {action['cards'][0]} {action['cards'][1]} ({action['hand']})\n")
                elif action['action'] == 'Win':
                    self.hand_info.insert(END, f"  {action['player']} wins ${action['amount']}\n")
                else:
                    amount_text = f" ${action['amount']}" if action['amount'] > 0 else ""
                    self.hand_info.insert(END, f"  {action['player']} {action['action'].lower()}{amount_text}\n")
        
        self.hand_info.configure(state=DISABLED)
    
    def _draw_card(self, x, y, width, height, card_code):
        """Draw a playing card on the canvas"""
        # Card background
        self.table_canvas.create_rectangle(
            x, y, x + width, y + height,
            fill="white", outline="black"
        )
        
        # Card value and suit
        value = card_code[0]
        suit = card_code[1]
        
        # Determine color based on suit
        color = "red" if suit in ['h', 'd'] else "black"
        
        # Map suit to symbol
        suit_symbol = {
            'h': '♥',
            'd': '♦',
            'c': '♣',
            's': '♠'
        }.get(suit, suit)
        
        # Map value to display value
        display_value = {
            'A': 'A',
            'K': 'K',
            'Q': 'Q',
            'J': 'J',
            '10': '10',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9'
        }.get(value, value)
        
        # Draw value and suit
        self.table_canvas.create_text(
            x + width // 2, y + height // 2,
            text=f"{display_value}{suit_symbol}",
            fill=color, font=("Arial", 10, "bold")
        )
    
    def _create_radar_chart(self, strategy1, strategy2, strategy1_data, strategy2_data):
        """Create a radar chart comparing two strategies"""
        # Define metrics for comparison
        metrics = ['Win Rate', 'Avg Profit', 'Bluff Success']
        
        # Add position metrics if available
        position_metrics = []
        if 'Position Stats' in strategy1_data.columns and not strategy1_data.empty:
            position_stats = strategy1_data['Position Stats'].iloc[0]
            for position in position_stats.keys():
                if isinstance(position_stats[position], dict) and 'win_rate' in position_stats[position]:
                    position_metrics.append(f"{position} Win Rate")
        
        all_metrics = metrics + position_metrics
        
        if not all_metrics:
            messagebox.showinfo("Data Error", "No metrics available for comparison.")
            return
            
        # Calculate values for each metric
        strategy1_values = []
        strategy2_values = []
        
        for metric in metrics:
            if metric in strategy1_data.columns:
                strategy1_values.append(strategy1_data[metric].mean())
                strategy2_values.append(strategy2_data[metric].mean())
            else:
                strategy1_values.append(0)
                strategy2_values.append(0)
        
        # Add position metrics values
        for position_metric in position_metrics:
            position = position_metric.split(' Win Rate')[0]
            
            # Get position stats for strategy 1
            if 'Position Stats' in strategy1_data.columns and not strategy1_data.empty:
                position_stats = strategy1_data['Position Stats'].iloc[0]
                if position in position_stats and isinstance(position_stats[position], dict) and 'win_rate' in position_stats[position]:
                    strategy1_values.append(position_stats[position]['win_rate'])
                else:
                    strategy1_values.append(0)
            else:
                strategy1_values.append(0)
                
            # Get position stats for strategy 2
            if 'Position Stats' in strategy2_data.columns and not strategy2_data.empty:
                position_stats = strategy2_data['Position Stats'].iloc[0]
                if position in position_stats and isinstance(position_stats[position], dict) and 'win_rate' in position_stats[position]:
                    strategy2_values.append(position_stats[position]['win_rate'])
                else:
                    strategy2_values.append(0)
            else:
                strategy2_values.append(0)
        
        # Create radar chart
        ax = self.comparison_figure.add_subplot(111, polar=True)
        
        # Number of variables
        N = len(all_metrics)
        
        # Angle of each axis
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Close the loop
        
        # Add values for each strategy (also close the loop)
        strategy1_values += strategy1_values[:1]
        strategy2_values += strategy2_values[:1]
        
        # Draw the chart
        ax.plot(angles, strategy1_values, linewidth=1, linestyle='solid', label=strategy1)
        ax.fill(angles, strategy1_values, alpha=0.1)
        
        ax.plot(angles, strategy2_values, linewidth=1, linestyle='solid', label=strategy2)
        ax.fill(angles, strategy2_values, alpha=0.1)
        
        # Add labels
        plt.xticks(angles[:-1], all_metrics)
        
        # Add legend
        ax.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        
        # Set chart title
        ax.set_title(f"Strategy Comparison: {strategy1} vs {strategy2}")
        
        # Adjust appearance for dark theme
        ax.set_facecolor("#202020")
        ax.spines['polar'].set_color('white')
        ax.tick_params(axis='both', colors='white')
        ax.set_title(f"Strategy Comparison: {strategy1} vs {strategy2}", color='white')
        
        # Draw the chart
        self.comparison_canvas.draw()

    def _run_quick_simulation(self, num_games, num_threads):
        # Create a simulation configuration
        from poker_simulate import SimulationConfig
        config = SimulationConfig(
            num_players=4,  # Default number of players
            num_games=num_games,
            num_threads=num_threads,
            sample_games=min(100, num_games)  # Use at most 100 games for sampling
        )
        
        # Create simulator with config and run simulation
        simulator = PokerSimulator(config)
        results = simulator.run_threaded_simulation(num_games, num_threads) 
        self.root.after(0, lambda: self._update_results(results))

    def _start_quick_simulation(self):
        # Get values from UI
        try:
            num_games = int(self.games_entry.get())
            num_threads = int(self.threads_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Number of games and threads must be integers.")
            return
            
        if num_games <= 0 or num_threads <= 0:
            messagebox.showerror("Invalid Input", "Number of games and threads must be positive integers.")
            return
            
        # Start the simulation thread
        thread = threading.Thread(target=lambda: self._run_quick_simulation(num_games, num_threads))
        thread.daemon = True
        thread.start()

    def _setup_comparison_tab(self):
        """Setup the strategy comparison tab with side-by-side comparison"""
        # Create a frame for the comparison controls
        controls_frame = ttk.Frame(self.comparison_frame)
        controls_frame.pack(fill=X, padx=5, pady=5)
        
        # Strategy selection dropdowns
        ttk.Label(controls_frame, text="Strategy 1:").pack(side=LEFT, padx=(0, 5))
        self.strategy1_var = tk.StringVar()
        self.strategy1_dropdown = ttk.Combobox(controls_frame, textvariable=self.strategy1_var, state="readonly", width=20)
        self.strategy1_dropdown.pack(side=LEFT, padx=(0, 10))
        
        ttk.Label(controls_frame, text="Strategy 2:").pack(side=LEFT, padx=(0, 5))
        self.strategy2_var = tk.StringVar()
        self.strategy2_dropdown = ttk.Combobox(controls_frame, textvariable=self.strategy2_var, state="readonly", width=20)
        self.strategy2_dropdown.pack(side=LEFT, padx=(0, 10))
        
        # Compare button
        self.compare_btn = ttk.Button(
            controls_frame, 
            text="Compare", 
            command=self._compare_strategies,
            bootstyle="success"
        )
        self.compare_btn.pack(side=LEFT, padx=5)
        self.compare_btn.configure(state="disabled")
        
        # Create a frame for the comparison results
        results_frame = ttk.Frame(self.comparison_frame)
        results_frame.pack(fill=BOTH, expand=YES, padx=5, pady=5)
        
        # Split the frame into two columns
        left_frame = ttk.LabelFrame(results_frame, text="Strategy 1")
        left_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 2))
        
        right_frame = ttk.LabelFrame(results_frame, text="Strategy 2")
        right_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(2, 0))
        
        # Create radar chart canvas for comparison
        self.comparison_figure = plt.figure(figsize=(10, 6))
        self.comparison_figure.patch.set_facecolor("#202020")
        self.comparison_canvas = FigureCanvasTkAgg(self.comparison_figure, results_frame)
        self.comparison_canvas.get_tk_widget().pack(fill=BOTH, expand=YES, pady=10)
        
        # Create statistics frames for each strategy
        self.strategy1_stats = ttk.Frame(left_frame)
        self.strategy1_stats.pack(fill=BOTH, expand=YES, padx=5, pady=5)
        
        self.strategy2_stats = ttk.Frame(right_frame)
        self.strategy2_stats.pack(fill=BOTH, expand=YES, padx=5, pady=5)
        
    def _update_results(self, results: Dict):
        """Update GUI with simulation results"""
        # Store the current results for saving later
        self.current_results = results
        
        # Create DataFrame for analytics
        analytics = PokerAnalytics()
        df = analytics.create_dataframe(results)
        
        # Update strategy dropdowns in comparison tab
        strategies = list(df['Strategy'].unique())
        self.strategy1_dropdown['values'] = strategies
        self.strategy2_dropdown['values'] = strategies
        
        if len(strategies) >= 2:
            self.strategy1_var.set(strategies[0])
            self.strategy2_var.set(strategies[1])
            self.compare_btn.configure(state="normal")
        elif len(strategies) == 1:
            self.strategy1_var.set(strategies[0])
            self.strategy2_var.set(strategies[0])
            self.compare_btn.configure(state="normal")
        
        # Analytics already created above

        # Create DataFrame and update statistics
        df = analytics.create_dataframe(results)
        summary_stats = analytics.generate_summary_statistics(df)

        # Clear previous results
        for item in self.summary_tree.get_children():
            self.summary_tree.delete(item)
        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)

        # Update summary statistics
        # Check if 'Win Rate' is in the columns
        if 'Win Rate' in summary_stats.columns:
            for strategy in summary_stats.index:
                try:
                    win_rate = summary_stats.loc[strategy, 'Win Rate']
                    self.summary_tree.insert(
                        "", "end",
                        values=(strategy, f"{win_rate:.4f}")
                    )
                except Exception as e:
                    print(f"Error accessing win rate for {strategy}: {e}")
                    self.summary_tree.insert(
                        "", "end",
                        values=(strategy, "0.0000")
                    )
        else:
            print("'Win Rate' column not found in summary_stats")
            print(f"Available columns: {summary_stats.columns.tolist()}")
            # Fallback: use win rate from the original dataframe
            for strategy in df['Strategy'].unique():
                strategy_df = df[df['Strategy'] == strategy]
                win_rate = strategy_df['Win Rate'].mean()
                self.summary_tree.insert(
                    "", "end",
                    values=(strategy, f"{win_rate:.4f}")
                )


        # Update detailed statistics
        for _, row in df.iterrows():
            self.stats_tree.insert(
                "", "end",
                values=(
                    row['Strategy'],
                    row['Hands Won'],
                    f"{row['Win Rate']:.1%}",
                    f"${row['Avg Profit']:.2f}",
                    f"${row['Total Profit']:.2f}"
                )
            )

        # Update graphs
        # Clear previous plots
        self.ax1.clear()
        self.ax2.clear()
        
        # Set background color for plots
        self.ax1.set_facecolor('#202020')
        self.ax2.set_facecolor('#202020')
        
        # Plot win rates
        analytics.plot_win_rates(df, self.ax1)
        self.ax1.set_title('Win Rates by Strategy', color='white')
        self.ax1.tick_params(axis='x', colors='white')
        self.ax1.tick_params(axis='y', colors='white')
        
        # Plot profit distribution
        analytics.plot_profit_distribution(df, self.ax2)
        self.ax2.set_title('Profit Distribution', color='white')
        self.ax2.tick_params(axis='x', colors='white')
        self.ax2.tick_params(axis='y', colors='white')
        
        # Update the canvas
        self.figure.tight_layout()
        self.canvas.draw()

        # Update player statistics
        for item in self.player_stats_tree.get_children():
            self.player_stats_tree.delete(item)

        # Update player statistics tree (only once)
        for i, player_stats in enumerate(results["player_stats"]):
            win_rate = player_stats["hands_won"] / \
                max(1, player_stats["hands_played"])
            bluff_rate = (player_stats["bluffs_successful"] /
                          max(1, player_stats["bluffs_attempted"]))

            position_stats = []
            for pos in ["early", "middle", "late"]:
                pos_stats = player_stats["position_stats"][pos]
                pos_wr = pos_stats["won"] / max(1, pos_stats["played"])
                position_stats.append(f"{pos}: {pos_wr:.1%}")

            self.player_stats_tree.insert(
                "",
                "end",
                values=(
                    results["strategies"][i],
                    player_stats["hands_played"],
                    f"{win_rate:.1%}",
                    f"${player_stats['total_profit']:.2f}",
                    f"{bluff_rate:.1%}",
                    " | ".join(position_stats)
                )
            )

        # Update interactive visualization
        visualizer = PokerVisualizer()
        fig = visualizer.create_interactive_dashboard(results)

        # Create an HTML file with the Plotly figure
        html_path = "poker_analysis.html"
        fig.write_html(html_path)

        # Create a button to open the interactive dashboard
        if hasattr(self, 'open_dashboard_btn'):
            self.open_dashboard_btn.destroy()

        self.open_dashboard_btn = ttk.Button(
            self.analysis_frame,
            text="Open Interactive Dashboard",
            command=lambda: webbrowser.open(html_path),
            bootstyle="info-outline"
        )
        self.open_dashboard_btn.pack(pady=20)

        # Add explanatory text
        if hasattr(self, 'dashboard_label'):
            self.dashboard_label.destroy()

        self.dashboard_label = ttk.Label(
            self.analysis_frame,
            text="Click the button above to open the interactive analysis dashboard in your browser",
            style='Subtitle.TLabel',
            wraplength=400
        )
        self.dashboard_label.pack(pady=10)

        # Re-enable controls and enable save button
        self.start_btn.configure(state="normal")
        self.load_btn.configure(state="normal")
        self.save_btn.configure(state="normal")
        self.progress["value"] = 100
        self.status_label.configure(text="Simulation complete")
        
    def _save_results(self):
        """Save current simulation results to a JSON file"""
        if not hasattr(self, 'current_results') or not self.current_results:
            messagebox.showwarning("No Results", "No simulation results to save. Please run a simulation first.")
            return
            
        # Ask user for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Save Simulation Results"
        )
        
        if not file_path:
            return  # User cancelled
            
        try:
            # Save results to JSON file
            with open(file_path, 'w') as f:
                # Add simulation parameters to the results
                save_data = {
                    "results": self.current_results,
                    "parameters": {
                        "num_games": self.num_games.get(),
                        "num_threads": self.num_threads.get()
                    }
                }
                json.dump(save_data, f, indent=2)
                
            messagebox.showinfo("Success", f"Results saved successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save results: {str(e)}")
    
    def _load_results(self):
        """Load previously saved simulation results"""
        # Ask user for file to load
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Load Simulation Results"
        )
        
        if not file_path:
            return  # User cancelled
            
        try:
            # Load results from JSON file
            with open(file_path, 'r') as f:
                save_data = json.load(f)
                
            # Extract results and parameters
            results = save_data.get("results", {})
            parameters = save_data.get("parameters", {})
            
            # Update UI with parameters if available
            if "num_games" in parameters:
                self.num_games.delete(0, tk.END)
                self.num_games.insert(0, parameters["num_games"])
                
            if "num_threads" in parameters:
                self.num_threads.delete(0, tk.END)
                self.num_threads.insert(0, parameters["num_threads"])
            
            # Update UI with loaded results
            self._update_results(results)
            
            messagebox.showinfo("Success", f"Results loaded successfully from {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load results: {str(e)}")
            print(f"Error details: {e}")

    def _add_tooltips(self):
        """Add tooltips to controls"""
        from ttkbootstrap.tooltip import ToolTip

        ToolTip(self.num_games,
                text="Number of poker games to simulate",
                bootstyle="info-inverse")

        ToolTip(self.num_threads,
                text="Number of parallel processing threads",
                bootstyle="info-inverse")

        ToolTip(self.start_btn,
                text="Start the poker simulation",
                bootstyle="info-inverse")
                
        ToolTip(self.save_btn,
                text="Save current simulation results to a file",
                bootstyle="info-inverse")
                
        ToolTip(self.load_btn,
                text="Load previously saved simulation results",
                bootstyle="info-inverse")


def main():
    root = tk.Tk()
    app = PokerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
