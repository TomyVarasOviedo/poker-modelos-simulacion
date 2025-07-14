import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List
import numpy as np
from models.Player import Player


class PokerAnalytics:
    @staticmethod
    def create_dataframe(results: Dict) -> pd.DataFrame:
        """
        Convierte los resultados de la simulación en un DataFrame de pandas.
        """
        if not results or 'player_stats' not in results or 'strategies' not in results:
            return pd.DataFrame({'Error': ['Invalid input data']})

        data = []
        for i, stats in enumerate(results["player_stats"]):
            if not stats:
                continue
            data.append({
                'Strategy': results["strategies"][i] if i < len(results["strategies"]) else 'Unknown',
                'Hands Won': stats.get('hands_won', 0),
                'Hands Played': stats.get('hands_played', 0),
                'Win Rate': stats.get('win_rate', 0.0),
                'Win Rate Total': stats.get('win_rate_total', 0.0),
            })
        return pd.DataFrame(data) if data else pd.DataFrame({'Error': ['No valid player data']})   
        """
        Convert simulation results to a pandas DataFrame with validation

        Args:
            - results (Dict): Simulation results containing player statistics and strategies.

        Returns:
            - pd.DataFrame: DataFrame containing player statistics and strategies.
        """
        if not results or 'player_stats' not in results or 'strategies' not in results:
            return pd.DataFrame({'Error': ['Invalid input data']})

        data = []
        for i, stats in enumerate(results["player_stats"]):
            if not stats:  # Skip empty player stats
                continue
                
            # Set default values if stats are missing
            hands_played = stats.get('hands_played', 0)
            hands_won = stats.get('hands_won', 0)
            win_rate = stats.get('win_rate', 0.0)
            win_rate_total = stats.get('win_rate_total', 0.0)
            
            data.append({
                'Strategy': results["strategies"][i] if i < len(results["strategies"]) else 'Unknown',
                'Hands Played': hands_played,
                'Hands Won': hands_won,
                'Win Rate': win_rate,
                'Win Rate Total': win_rate_total,
            })
        
        return pd.DataFrame(data) if data else pd.DataFrame({'Error': ['No valid player data']})
 
    @staticmethod
    def generate_summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate summary statistics for each strategy with validation

        Args:
            - df (pd.DataFrame): DataFrame containing player statistics and strategies.

        Returns:
            - pd.DataFrame: DataFrame containing summary statistics for each strategy.
        """
        if df is None or df.empty or 'Error' in df.columns:
            return pd.DataFrame({'Error': ['No data available']})
        
        try:
            # Create a summary DataFrame with strategies as index and metrics as columns
            strategies = df['Strategy'].unique()
            summary_data = {}
            
            for strategy in strategies:
                strategy_df = df[df['Strategy'] == strategy]
                summary_data[strategy] = {
                    'Win Rate': strategy_df['Win Rate'].mean(),
                    'Win Rate Total': strategy_df['Win Rate Total'].mean(),
                    'Hands Played': strategy_df['Hands Played'].mean()
                }
            
            # Convert to DataFrame with strategies as index
            summary = pd.DataFrame.from_dict(summary_data, orient='index')
            return summary
        except Exception as e:
            print(f"Error generating stats: {e}")
            return pd.DataFrame({'Error': [str(e)]})

    @staticmethod
    def plot_win_rates(df: pd.DataFrame, ax=None):
        """
        Plot win rates comparison with validation

        Args:
            - df (pd.DataFrame): DataFrame containing player statistics and strategies.
            - ax (matplotlib.axes.Axes, optional): Axes to plot on. If None, a new figure is created.

        Returns:
            - ax (matplotlib.axes.Axes): Axes with the plot.
        """
        if df is None or df.empty or 'Error' in df.columns:
            return None

        if ax is None:
            _, ax = plt.subplots(figsize=(10, 6))

        try:
            sns.barplot(data=df, x='Strategy', y='Win Rate', ax=ax)
            ax.set_title('Strategy Win Rates Comparison')
            ax.set_ylabel('Win Rate')
            ax.tick_params(axis='x', rotation=45)
            return ax
        except Exception as e:
            print(f"Error plotting win rates: {e}")
            return None

    @staticmethod
    def plot_profit_distribution(df: pd.DataFrame, ax=None):
        """
        Plot profit distribution with validation

        Args:
            - df (pd.DataFrame): DataFrame containing player statistics and strategies.
            - ax (matplotlib.axes.Axes, optional): Axes to plot on. If None, a new figure is created.

        Returns:
            - ax (matplotlib.axes.Axes): Axes with the plot.
        """
        if df is None or df.empty or 'Error' in df.columns:
            return None

        if ax is None:
            _, ax = plt.subplots(figsize=(10, 6))

        try:
            sns.barplot(data=df, x='Strategy', y='Avg Profit', ax=ax)
            ax.set_title('Average Profit by Strategy')
            ax.set_ylabel('Average Profit ($)')
            ax.tick_params(axis='x', rotation=45)
            return ax
        except Exception as e:
            print(f"Error plotting profit distribution: {e}")
            return None

    @staticmethod
    def analyze_player_performance(player_profiles: List[Player]) -> pd.DataFrame:
        """
        Analyze detailed player performance with validation

        Args:
            - player_profiles (List[Player]): List of player profiles to analyze.

        Returns:
            - pd.DataFrame: DataFrame containing detailed player performance statistics.
        """
        if not player_profiles:
            return pd.DataFrame({'Error': ['No player profiles provided']})

        data = []
        for profile in player_profiles:
            if not profile or not hasattr(profile, 'stats'):
                continue
                
            data.append({
                'Strategy': getattr(profile, 'strategy_name', 'Unknown'),
                'Hands Played': profile.stats.get('hands_played', 0),
                'Win Rate': getattr(profile, 'get_win_rate', lambda: 0)(),
                'Avg Profit': profile.stats.get('total_profit', 0) / max(1, profile.stats.get('hands_played', 1)),
                'Bluff Success': getattr(profile, 'get_bluff_success_rate', lambda: 0)(),
                'Early Position WR': getattr(profile, 'get_position_win_rate', lambda _: 0)('early'),
                'Middle Position WR': getattr(profile, 'get_position_win_rate', lambda _: 0)('middle'),
                'Late Position WR': getattr(profile, 'get_position_win_rate', lambda _: 0)('late')
            })
        
        return pd.DataFrame(data) if data else pd.DataFrame({'Error': ['No valid player profiles']})
