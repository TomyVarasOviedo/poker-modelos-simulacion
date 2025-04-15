import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List
import numpy as np
from models.player_profile import PlayerProfile

class PokerAnalytics:
    @staticmethod
    def create_dataframe(results: Dict) -> pd.DataFrame:
        """Convert simulation results to a pandas DataFrame"""
        data = []
        for i, stats in enumerate(results["player_stats"]):
            data.append({
                'Strategy': results["strategies"][i],
                'Hands Played': stats['hands_played'],
                'Hands Won': stats['hands_won'],
                'Win Rate': stats['hands_won'] / max(1, stats['hands_played']),
                'Total Profit': stats['total_profit'],
                'Avg Profit': stats['total_profit'] / max(1, stats['hands_played']),
                'Bluff Success': stats['bluffs_successful'] / max(1, stats['bluffs_attempted'])
            })
        return pd.DataFrame(data)

    @staticmethod
    def generate_summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
        """Generate summary statistics for each strategy"""
        return df.describe()

    @staticmethod
    def plot_win_rates(df: pd.DataFrame, ax=None):
        """Plot win rates comparison"""
        if ax is None:
            _, ax = plt.subplots(figsize=(10, 6))
        
        sns.barplot(data=df, x='Strategy', y='Win Rate', ax=ax)
        ax.set_title('Strategy Win Rates Comparison')
        ax.set_ylabel('Win Rate')
        ax.tick_params(axis='x', rotation=45)
        return ax

    @staticmethod
    def plot_profit_distribution(df: pd.DataFrame, ax=None):
        """Plot profit distribution"""
        if ax is None:
            _, ax = plt.subplots(figsize=(10, 6))
        
        sns.barplot(data=df, x='Strategy', y='Avg Profit', ax=ax)
        ax.set_title('Average Profit by Strategy')
        ax.set_ylabel('Average Profit ($)')
        ax.tick_params(axis='x', rotation=45)
        return ax

    @staticmethod
    def analyze_player_performance(player_profiles: List[PlayerProfile]) -> pd.DataFrame:
        """Analyze detailed player performance"""
        data = []
        for profile in player_profiles:
            data.append({
                'Strategy': profile.strategy_name,
                'Hands Played': profile.stats['hands_played'],
                'Win Rate': profile.get_win_rate(),
                'Avg Profit': profile.stats['total_profit'] / max(1, profile.stats['hands_played']),
                'Bluff Success': profile.get_bluff_success_rate(),
                'Early Position WR': profile.get_position_win_rate('early'),
                'Middle Position WR': profile.get_position_win_rate('middle'),
                'Late Position WR': profile.get_position_win_rate('late')
            })
        return pd.DataFrame(data)