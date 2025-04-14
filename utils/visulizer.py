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
            ax.set