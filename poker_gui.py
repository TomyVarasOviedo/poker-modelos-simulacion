import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from typing import List, Dict

class PokerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Poker Strategy Simulator")
        self.root.geometry("1200x800")
        self.root.style = ttk.Style(theme='darkly')  #cambia el color
        self.root.iconbitmap("poker_img.ico") #Icon del poker
        
        # Create main containers
        self.control_frame = ttk.LabelFrame(self.root, text="Simulation Controls", padding=10)
        self.control_frame.pack(fill=X, padx=20, pady=20)
        
        self.results_frame = ttk.LabelFrame(self.root, text="Simulation Results", padding=10)
        self.results_frame.pack(fill=BOTH, expand=YES, padx=20, pady=20)
        
        self._create_controls()
        self._create_results_view()
        
    def _create_controls(self):
        # Simulation controls
        controls = ttk.Frame(self.control_frame)
        controls.pack(fill=X, expand=YES)
        
        ttk.Label(controls, text="Number of Games:", font=("Courier", 12)).pack(side=LEFT, padx=5)
        self.num_games = ttk.Entry(controls, width=10)
        self.num_games.insert(0, "1000")
        self.num_games.pack(side=LEFT, padx=5)
        
        ttk.Label(controls, text="Number of Threads:", font=("Courier", 12)).pack(side=LEFT, padx=5)
        self.num_threads = ttk.Entry(controls, width=5)
        self.num_threads.insert(0, "4")
        self.num_threads.pack(side=LEFT, padx=5)
        
        self.start_btn = ttk.Button(
            controls, 
            text="Start Simulation",
            command=self._run_simulation,
            style="danger.TButton"
        )
        self.start_btn.pack(side=LEFT, padx=5)
        
        self.progress = ttk.Progressbar(
            controls,
            mode='determinate',
            length=200
        )
        self.progress.pack(side=LEFT, padx=5)
        
    def _create_results_view(self):
        # Create notebook for different views
        self.notebook = ttk.Notebook(self.results_frame)
        self.notebook.pack(fill=BOTH, expand=YES, padx=5, pady=5)
        
        # Statistics tab
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistics")
        
        # Create treeview for statistics
        self.stats_tree = ttk.Treeview(
            self.stats_frame,
            columns=("Strategy", "Wins", "Win Rate", "Avg Profit"),
            show="headings"
        )
        
        self.stats_tree.heading("Strategy", text="Strategy", anchor="center")
        self.stats_tree.column("Strategy", anchor="center")

        self.stats_tree.heading("Wins", text="Wins", anchor="center")
        self.stats_tree.column("Wins", anchor="center")

        self.stats_tree.heading("Win Rate", text="Win Rate", anchor="center")
        self.stats_tree.column("Win Rate", anchor="center")

        self.stats_tree.heading("Avg Profit", text="Avg Profit", anchor="center")
        self.stats_tree.column("Avg Profit", anchor="center")

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"), foreground="white")
        self.stats_tree.pack(fill=BOTH, expand=YES)
        
        # Graphs tab
        self.graphs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.graphs_frame, text="Graphs")
        
        # Create matplotlib figure
        self.figure, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, self.graphs_frame)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=YES)
        
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
        # Clear previous results
        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)
            
        # Update statistics view
        for strategy, stats in results.items():
            self.stats_tree.insert(
                "",
                "end",
                values=(
                    strategy,
                    stats["wins"],
                    f"{stats['win_rate']:.2%}",
                    f"${stats['avg_profit']:.2f}"
                )
            )
            
        # Update graph
        self.ax.clear()
        strategies = list(results.keys())
        win_rates = [results[s]["win_rate"] for s in strategies]
        
        self.ax.bar(strategies, win_rates)
        self.ax.set_title("Strategy Win Rates")
        self.ax.set_ylabel("Win Rate")
        self.ax.tick_params(axis='x', rotation=45)
        
        self.figure.tight_layout()
        self.canvas.draw()
        
        # Re-enable controls
        self.start_btn.configure(state="normal")
        self.progress["value"] = 100

def main():
    root = tk.Tk()
    app = PokerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
