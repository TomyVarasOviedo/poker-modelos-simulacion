import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict
import numpy as np


class PokerVisualizer:
    def create_interactive_dashboard(self, results: Dict) -> go.Figure:
        """
        Create interactive dashboard with Plotly

        Args:
            - results [Dict]: Dictionary containing the results of the poker game

        Returns:
            - fig [go.Figure]: Plotly figure object containing the dashboard
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Win Rates by Strategy',
                'Profit Distribution',
                'Position Performance',
                'Bluff Success Rate'
            ),
            specs=[[{'type': 'bar'}, {'type': 'bar'}],
                   [{'type': 'bar'}, {'type': 'bar'}]]
        )

        # Win rates plot
        win_rates = [stats['hands_won'] / max(1, stats['hands_played'])
                     for stats in results['player_stats']]
        fig.add_trace(
            go.Bar(
                name='Win Rate',
                x=results['strategies'],
                y=win_rates,
                text=[f'{wr:.1%}' for wr in win_rates],
                textposition='auto',
                hovertemplate='Strategy: %{x}<br>Win Rate: %{text}<extra></extra>'
            ),
            row=1, col=1
        )

        # Profit distribution
        profits = [stats['total_profit'] for stats in results['player_stats']]
        fig.add_trace(
            go.Bar(
                name='Total Profit',
                x=results['strategies'],
                y=profits,
                text=[f'${p:.2f}' for p in profits],
                textposition='auto',
                hovertemplate='Strategy: %{x}<br>Profit: %{text}<extra></extra>'
            ),
            row=1, col=2
        )

        # Position performance
        for i, position in enumerate(['early', 'middle', 'late']):
            position_stats = []
            for stats in results['player_stats']:
                pos = stats['position_stats'][position]
                wr = pos['won'] / max(1, pos['played'])
                position_stats.append(wr)

            fig.add_trace(
                go.Bar(
                    name=f'{position.title()} Position',
                    x=results['strategies'],
                    y=position_stats,
                    text=[f'{wr:.1%}' for wr in position_stats],
                    textposition='auto',
                ),
                row=2, col=1
            )

        # Bluff success rate
        bluff_rates = []
        for stats in results['player_stats']:
            success_rate = (stats['bluffs_successful'] /
                            max(1, stats['bluffs_attempted']))
            bluff_rates.append(success_rate)

        fig.add_trace(
            go.Bar(
                name='Bluff Success Rate',
                x=results['strategies'],
                y=bluff_rates,
                text=[f'{br:.1%}' for br in bluff_rates],
                textposition='auto',
                hovertemplate='Strategy: %{x}<br>Success Rate: %{text}<extra></extra>'
            ),
            row=2, col=2
        )

        # Update layout
        fig.update_layout(
            title_text='Poker Strategy Analysis Dashboard',
            showlegend=True,
            template='plotly_dark',
            height=800,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.05
            ),
            hoverlabel=dict(
                bgcolor="white",
                font_size=16,
                font_family="Rockwell"
            )
        )

        return fig
