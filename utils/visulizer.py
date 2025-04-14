import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any, Optional, Union, Tuple
import os

class CricketVisualizer:
    """
    A class for creating visualizations of cricket statistics.
    """
    
    def __init__(self, data: pd.DataFrame = None, output_dir: str = 'plots'):
        """
        Initialize the visualizer with cricket data.
        
        Args:
            data: Pandas DataFrame containing cricket data
            output_dir: Directory to save plots
        """
        self.data = data
        self.output_dir = output_dir
        self._setup_style()
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def _setup_style(self):
        """Set up the plotting style."""
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette('Set2')
        
    def set_data(self, data: pd.DataFrame):
        """
        Set the data to be visualized.
        
        Args:
            data: Pandas DataFrame containing cricket data
        """
        self.data = data
    
    def _check_data(self):
        """
        Check if data is available for visualization.
        
        Raises:
            ValueError: If data is not loaded
        """
        if self.data is None:
            raise ValueError("Data not set. Please use set_data() method first.")
    
    def player_performance(self, player_name: str, metrics: List[str] = None, 
                          save: bool = False, filename: str = None) -> plt.Figure:
        """
        Visualize a player's performance across multiple metrics.
        
        Args:
            player_name: Name of the player
            metrics: List of metrics to visualize (e.g., 'Runs', 'Wickets')
            save: Whether to save the plot to a file
            filename: Name of the file to save the plot to
            
        Returns:
            Matplotlib Figure object
        """
        self._check_data()
        
        player_data = self.data[self.data['Player'] == player_name]
        
        if player_data.empty:
            raise ValueError(f"No data found for player: {player_name}")
            
        if metrics is None:
            # Default metrics (numeric columns that make sense for tracking over time)
            potential_metrics = ['Runs', 'Wickets', 'Strike Rate', 'Economy Rate', 'Batting Average']
            metrics = [m for m in potential_metrics if m in player_data.columns]
            
        if not metrics:
            raise ValueError("No valid metrics available for visualization")
            
        # Sort by date if available
        if 'Match Date' in player_data.columns:
            player_data = player_data.sort_values('Match Date')
            x_label = 'Match Date'
            x_values = player_data['Match Date']
        else:
            # Use match index as x-axis
            x_label = 'Match Number'
            x_values = range(len(player_data))
        
        # Create figure
        fig, axes = plt.subplots(len(metrics), 1, figsize=(10, 3 * len(metrics)), sharex=True)
        
        # If only one metric, axes won't be an array
        if len(metrics) == 1:
            axes = [axes]
        
        # Plot each metric
        for i, metric in enumerate(metrics):
            if metric not in player_data.columns:
                continue
                
            ax = axes[i]
            ax.plot(x_values, player_data[metric], marker='o', linestyle='-', linewidth=2)
            
            # Add opponent labels
            if 'Opponent' in player_data.columns:
                for j, (x, y, opp) in enumerate(zip(x_values, player_data[metric], player_data['Opponent'])):
                    ax.annotate(opp, (x, y), textcoords="offset points", 
                               xytext=(0, 5), ha='center', fontsize=8)
            
            # Set axis labels and title
            ax.set_ylabel(metric)
            ax.set_title(f"{player_name}'s {metric}")
            
            # Add grid
            ax.grid(True, alpha=0.3)
            
        # Set common xlabel
        axes[-1].set_xlabel(x_label)
        
        # Add overall title
        plt.suptitle(f"{player_name}'s Performance Analysis", fontsize=16, y=1.02)
        plt.tight_layout()
        
        # Save if requested
        if save:
            if filename is None:
                filename = f"{player_name.replace(' ', '_')}_performance.png"
            plt.savefig(os.path.join(self.output_dir, filename), dpi=300, bbox_inches='tight')
        
        return fig
    
    def team_comparison(self, teams: List[str], metric: str, 
                       aggregate: str = 'mean', save: bool = False, 
                       filename: str = None) -> plt.Figure:
        """
        Compare teams based on a specific metric.
        
        Args:
            teams: List of team names to compare
            metric: Metric to compare (e.g., 'Runs', 'Wickets')
            aggregate: Aggregation function ('mean', 'sum', 'max')
            save: Whether to save the plot to a file
            filename: Name of the file to save the plot to
            
        Returns:
            Matplotlib Figure object
        """
        self._check_data()
        
        if metric not in self.data.columns:
            raise ValueError(f"Metric '{metric}' not found in data")
        
        # Filter for specified teams
        team_data = self.data[self.data['Team'].isin(teams)]
        
        if team_data.empty:
            raise ValueError(f"No data found for the specified teams")
        
        # Aggregate data
        if aggregate == 'mean':
            agg_data = team_data.groupby('Team')[metric].mean()
        elif aggregate == 'sum':
            agg_data = team_data.groupby('Team')[metric].sum()
        elif aggregate == 'max':
            agg_data = team_data.groupby('Team')[metric].max()
        else:
            raise ValueError(f"Unsupported aggregation: {aggregate}")
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(agg_data.index, agg_data.values)
        
        # Add data labels
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),  # 3 points vertical offset
                       textcoords="offset points",
                       ha='center', va='bottom')
        
        # Set labels and title
        ax.set_xlabel('Team')
        ax.set_ylabel(metric)
        ax.set_title(f'Team Comparison: {metric} ({aggregate})')
        
        # Rotate x labels if needed
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save if requested
        if save:
            if filename is None:
                filename = f"team_comparison_{metric}.png"
            plt.savefig(os.path.join(self.output_dir, filename), dpi=300, bbox_inches='tight')
        
        return fig
    
    def player_comparison(self, players: List[str], metrics: List[str], 
                         save: bool = False, filename: str = None) -> plt.Figure:
        """
        Compare multiple players across different metrics.
        
        Args:
            players: List of player names to compare
            metrics: List of metrics to compare
            save: Whether to save the plot to a file
            filename: Name of the file to save the plot to
            
        Returns:
            Matplotlib Figure object
        """
        self._check_data()
        
        # Filter data for specified players
        player_data = self.data[self.data['Player'].isin(players)]
        
        if player_data.empty:
            raise ValueError(f"No data found for the specified players")
        
        # Check if metrics exist
        for metric in metrics:
            if metric not in player_data.columns:
                raise ValueError(f"Metric '{metric}' not found in data")
        
        # Aggregate data for each player and metric
        agg_data = {}
        for player in players:
            player_metrics = {}
            for metric in metrics:
                player_metrics[metric] = player_data[player_data['Player'] == player][metric].mean()
            agg_data[player] = player_metrics
        
        # Convert to DataFrame for easier plotting
        comparison_df = pd.DataFrame(agg_data)
        
        # Create radar chart
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(polar=True))
        
        # Angles for metrics
        angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]  # Close the loop
        
        # Set ax labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        
        # Plot each player
        for player in players:
            values = [comparison_df.loc[metric, player] for metric in metrics]
            values += values[:1]  # Close the loop
            
            # Normalize values for better visualization
            max_vals = comparison_df.max(axis=1)
            normalized = [v/max_vals[metrics[i]] for i, v in enumerate(values[:-1])]
            normalized += normalized[:1]  # Close the loop
            
            ax.plot(angles, normalized, linewidth=2, linestyle='solid', label=player)
            ax.fill(angles, normalized, alpha=0.1)
        
        # Add legend
        ax.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        
        plt.title('Player Comparison Across Metrics', size=15)
        plt.tight_layout()
        
        # Save if requested
        if save:
            if filename is None:
                filename = "player_comparison_radar.png"
            plt.savefig(os.path.join(self.output_dir, filename), dpi=300, bbox_inches='tight')
        
        return fig
    
    def match_analysis(self, match_id: Union[str, int], save: bool = False, 
                      filename: str = None) -> plt.Figure:
        """
        Generate a comprehensive analysis for a specific match.
        
        Args:
            match_id: ID of the match to analyze
            save: Whether to save the plot to a file
            filename: Name of the file to save the plot to
            
        Returns:
            Matplotlib Figure object
        """
        self._check_data()
        
        # Filter data for the specific match
        if 'Match ID' in self.data.columns:
            match_data = self.data[self.data['Match ID'] == match_id]
        elif 'Match' in self.data.columns:
            match_data = self.data[self.data['Match'] == match_id]
        else:
            raise ValueError("No 'Match ID' or 'Match' column found in data")
        
        if match_data.empty:
            raise ValueError(f"No data found for match ID: {match_id}")
        
        # Get teams involved
        teams = match_data['Team'].unique()
        
        # Create a 2x2 subplot
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Top batsmen (most runs)
        ax1 = axes[0, 0]
        top_batsmen = match_data.nlargest(5, 'Runs')
        sns.barplot(x='Runs', y='Player', hue='Team', data=top_batsmen, ax=ax1)
        ax1.set_title('Top Batsmen')
        ax1.set_xlabel('Runs')
        ax1.set_ylabel('Player')
        
        # Top bowlers (most wickets)
        ax2 = axes[0, 1]
        if 'Wickets' in match_data.columns:
            top_bowlers = match_data.nlargest(5, 'Wickets')
            sns.barplot(x='Wickets', y='Player', hue='Team', data=top_bowlers, ax=ax2)
            ax2.set_title('Top Bowlers')
            ax2.set_xlabel('Wickets')
            ax2.set_ylabel('Player')
        else:
            ax2.text(0.5, 0.5, 'No wicket data available', 
                    horizontalalignment='center', verticalalignment='center')
        
        # Team totals
        ax3 = axes[1, 0]
        team_runs = match_data.groupby('Team')['Runs'].sum()
        team_runs.plot(kind='bar', ax=ax3)
        ax3.set_title('Team Total Runs')
        ax3.set_xlabel('Team')
        ax3.set_ylabel('Total Runs')
        
        # Run rate analysis
        ax4 = axes[1, 1]
        if 'Over' in match_data.columns:
            for team in teams:
                team_overs = match_data[match_data['Team'] == team]
                if not team_overs.empty:
                    team_overs = team_overs.sort_values('Over')
                    ax4.plot(team_overs['Over'], team_overs['Runs'].cumsum(), 
                            label=f"{team} Run Rate", marker='o')
            
            ax4.set_title('Run Rate Progression')
            ax4.set_xlabel('Over')
            ax4.set_ylabel('Cumulative Runs')
            ax4.legend()
        else:
            ax4.text(0.5, 0.5, 'No over-by-over data available', 
                    horizontalalignment='center', verticalalignment='center')
        
        # Add match details as suptitle
        if 'Match Date' in match_data.columns:
            match_date = match_data['Match Date'].iloc[0]
            plt.suptitle(f"Match Analysis: {teams[0]} vs {teams[1]} ({match_date})", 
                        fontsize=16, y=0.98)
        else:
            plt.suptitle(f"Match Analysis: {teams[0]} vs {teams[1]}", fontsize=16, y=0.98)
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        # Save if requested
        if save:
            if filename is None:
                filename = f"match_analysis_{match_id}.png"
            plt.savefig(os.path.join(self.output_dir, filename), dpi=300, bbox_inches='tight')
        
        return fig
    
    def season_trends(self, season: Union[str, int], metric: str, 
                     top_n: int = 5, save: bool = False, 
                     filename: str = None) -> plt.Figure:
        """
        Visualize trends for a specific season.
        
        Args:
            season: Season identifier
            metric: Metric to analyze trends for
            top_n: Number of top players to include
            save: Whether to save the plot to a file
            filename: Name of the file to save the plot to
            
        Returns:
            Matplotlib Figure object
        """
        self._check_data()
        
        # Check if season column exists
        if 'Season' not in self.data.columns:
            raise ValueError("No 'Season' column found in data")
        
        # Filter data for the specific season
        season_data = self.data[self.data['Season'] == season]
        
        if season_data.empty:
            raise ValueError(f"No data found for season: {season}")
        
        if metric not in season_data.columns:
            raise ValueError(f"Metric '{metric}' not found in data")
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
        
        # Top performers for the metric
        top_players = season_data.groupby('Player')[metric].sum().nlargest(top_n)
        top_players.sort_values().plot(kind='barh', ax=ax1)
        ax1.set_title(f'Top {top_n} Players by {metric}')
        ax1.set_xlabel(metric)
        ax1.set_ylabel('Player')
        
        # Team performance
        team_performance = season_data.groupby('Team')[metric].mean()
        team_performance.sort_values().plot(kind='barh', ax=ax2)
        ax2.set_title(f'Team Average {metric}')
        ax2.set_xlabel(f'Average {metric}')
        ax2.set_ylabel('Team')
        
        plt.suptitle(f"Season {season} - {metric} Analysis", fontsize=16)
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        
        # Save if requested
        if save:
            if filename is None:
                filename = f"season_{season}_{metric}_analysis.png"
            plt.savefig(os.path.join(self.output_dir, filename), dpi=300, bbox_inches='tight')
        
        return fig
