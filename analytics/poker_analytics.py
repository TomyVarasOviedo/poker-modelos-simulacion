import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List
import numpy as np

class PokerAnalytics:
    @staticmethod
    def create_dataframe(results: Dict) -> pd.DataFrame:
        """Convert simulation results to a pandas DataFrame"""
        data = []
        for strategy, stats in results.items():
            data.append({
                'Strategy': strategy,
                'Wins': stats['wins'],
                'Win Rate': stats['win_rate'],
                'Avg Profit': stats['avg_profit'],
                'Total Profit': stats['total_profit']
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