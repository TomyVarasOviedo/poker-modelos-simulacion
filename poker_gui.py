from analytics.poker_analytics import PokerAnalytics
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import pandas as pd
from typing import List, Dict


class PokerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Poker Strategy Simulator")
        self.root.geometry("1400x900")  # Larger initial size
        self.root.style = ttk.Style(theme='darkly')
        
        # Try to set icon, handle different platforms
        try:
            # For Windows
            self.root.iconbitmap("poker_img.ico")
        except:
            # For Linux/Unix
            try:
                # Try .xbm format for Linux
                self.root.iconbitmap('@poker_img.xbm')
            except:
                # Skip icon if not found
                pass
        
        # Configure custom styles
        self.root.style.configure('Title.TLabel', 
                                font=('Helvetica', 24, 'bold'),
                                foreground='#00bc8c')
        
        self.root.style.configure('Subtitle.TLabel',
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
        
        #Style graphs 
        self.figure,(self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 5)) 
        self.figure.patch.set_facecolor("#202020") 
        
        # Create matplotlib figure and axes 
        self.canvas = FigureCanvasTkAgg(self.figure, self.overview_frame) 
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=YES) 
        
        # Configure Treeview styles 
        self.root.style.configure(
             "Treeview", 
             background="#2f3136",
               foreground="white",
               fieldbackground="#2f3136",
               rowheight=25 )
        self.root.style.configure( 
            "Treeview.Heading",
            background="#212529",
            foreground="white",
            relief="flat" ) 
        
        # Summary statistics with headers 
        ttk.Label( 
            self.stats_frame, 
            text="Summary Statistics", 
            style='Subtitle.TLabel' 
            ).pack(anchor=W, pady=(0, 5)) 
        self.summary_tree = ttk.Treeview( 
            self.stats_frame, 
            columns=("Metric", "Value"), 
            show="headings", height=5 ) 
        self._configure_treeview(self.summary_tree) 
        self.summary_tree.pack(fill=X, pady=(0, 10)) 
        
        # Detailed statistics with headers 
        ttk.Label( 
            self.stats_frame, 
            text="Detailed Statistics", 
            style='Subtitle.TLabel' 
            ).pack(anchor=W, pady=(10, 5)) 
        self.stats_tree = ttk.Treeview( 
            self.stats_frame, columns=("Strategy", "Wins", "Win Rate", "Avg Profit", "Std Dev"), 
            show="headings" ) 
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
                "Position Stats" ), show="headings", height=5 )
        self._configure_treeview(self.player_stats_tree) 
        
        # Adjust column widths for better visibility
        self.player_stats_tree.column("Strategy", width=100) 
        self.player_stats_tree.column("Hands Played", width=100) 
        self.player_stats_tree.column("Win Rate", width=80) 
        self.player_stats_tree.column("Total Profit", width=100) 
        self.player_stats_tree.column("Bluff Rate", width=80)
        self.player_stats_tree.column("Position Stats", width=200) 
        self.player_stats_tree.pack(fill=X, pady=(0, 10))
        
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
        num_games = int(self.num_games.get())
        num_threads = int(self.num_threads.get())
        
        # Disable controls during simulation
        self.start_btn.configure(state="disabled")
        self.progress["value"] = 0
        
        # Import here to avoid circular imports
        from main import run_threaded_simulation
        
        # Run simulation in a separate thread to avoid GUI freezing
        import threading
        def simulation_thread():
            results = run_threaded_simulation(num_games, num_threads)
            self.root.after(0, lambda: self._update_results(results))
        
        thread = threading.Thread(target=simulation_thread)
        thread.start()
        
    def _update_results(self, results: Dict):
        """Update GUI with simulation results"""
        analytics = PokerAnalytics()
        
        # Create DataFrame and update statistics
        df = analytics.create_dataframe(results)
        summary_stats = analytics.generate_summary_statistics(df)
        
        # Clear previous results
        for item in self.summary_tree.get_children():
            self.summary_tree.delete(item)
        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)
            
        # Update summary statistics
        for metric in summary_stats.index:
            self.summary_tree.insert(
                "", "end",
                values=(metric, f"{summary_stats.loc[metric, 'Win Rate']:.4f}")
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
        # Clear and update graphs dynamically
        self.ax1.clear()
        self.ax2.clear()
    
        # Update first graph: Strategy Win Rates Comparison
        analytics.plot_win_rates(df, ax=self.ax1)
        self.ax1.set_facecolor("#2f2f2f")  # Gray background for the plot
        self.ax1.set_title("Strategy Win Rates Comparison", color="white") 
        self.ax1.tick_params(colors="white")  # White axis labels
        self.ax1.xaxis.label.set_color("white")  # Set x-axis label color to white
        self.ax1.yaxis.label.set_color("white")  # Set y-axis label color to white
        for bar in self.ax1.patches:
            bar.set_color("#00bc8c")
    
        # Update second graph: Profit Distribution
        analytics.plot_profit_distribution(df, ax=self.ax2)
        self.ax2.set_facecolor("#2f2f2f")  # Gray background for the plot
        self.ax2.set_title("Profit Distribution", color="white")  
        self.ax2.tick_params(colors="white")  # White axis labels
        self.ax2.xaxis.label.set_color("white")  # Set x-axis label color to white
        self.ax2.yaxis.label.set_color("white")  # Set y-axis label color to white
        for bar in self.ax2.patches:
            bar.set_color("#00bc8c")

        # Apply tight layout and redraw the canvas
        self.figure.tight_layout()
        self.canvas.draw()

        # Update player statistics
        for item in self.player_stats_tree.get_children():
            self.player_stats_tree.delete(item)

        # Update statistics with confidence intervals
        for i, (prob, ci) in enumerate(zip(
            results.get("probabilities", []), 
            results.get("confidence_intervals", [])
        )):
            self.stats_tree.insert(
                "", "end",
                values=(
                    f"Player {i+1}",
                    f"{prob:.1%}",
                    f"({ci[0]:.1%}, {ci[1]:.1%})",
                )
            )
      
        # Update player statistics
        for item in self.player_stats_tree.get_children():
            self.player_stats_tree.delete(item)

        for i, player_stats in enumerate(results["player_stats"]):
            win_rate = player_stats["hands_won"] / max(1, player_stats["hands_played"])
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
        
        # Re-enable controls
        self.start_btn.configure(state="normal")
        self.progress["value"] = 100

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

def main():
    root = tk.Tk()
    app = PokerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
