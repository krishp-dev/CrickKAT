#!/usr/bin/env python3
import os
import sys
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Optional

# Add utils directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import CrickKAT modules
from utils.data_loader import DataLoader
from utils.analyzer import CricketAnalyzer
from utils.visulizer import CricketVisualizer

class CrickKAT:
    """
    Cricket Knowledge and Analysis Tool (CrickKAT)
    A comprehensive cricket analysis system.
    """
    
    def __init__(self):
        """Initialize CrickKAT with all components."""
        self.data_loader = DataLoader(data_dir='data')
        self.analyzer = CricketAnalyzer()
        self.visualizer = CricketVisualizer(output_dir='plots')
        self.data = None
        self.current_file = None
        
        # Check if data directory exists
        if not os.path.exists('data'):
            os.makedirs('data')
            print("Created 'data' directory. Please add cricket data files (.csv) to this directory.")
            
        # Check if plots directory exists
        if not os.path.exists('plots'):
            os.makedirs('plots')
        
        # Try to load data automatically
        self._load_initial_data()
        
    def _load_initial_data(self):
        """Attempt to load the first available data file."""
        available_files = self.data_loader.available_files
        if available_files:
            self.current_file = available_files[0]
            self.data = self.data_loader.load_data(self.current_file)
            self.analyzer.set_data(self.data)
            self.visualizer.set_data(self.data)
            print(f"Loaded data from '{self.current_file}'")
            
            # Display data summary
            self._display_data_summary()
        else:
            print("No data files found. Please add cricket data files (.csv) to the 'data' directory.")
            
    def _display_data_summary(self):
        """Display a summary of the loaded data."""
        if self.data is None:
            print("No data loaded.")
            return
            
        info = self.data_loader.get_data_info()
        
        print("\n" + "="*50)
        print(f"Data Summary: {self.current_file}")
        print("="*50)
        print(f"Number of records: {info['num_rows']}")
        print(f"Number of columns: {info['num_columns']}")
        print(f"Players: {len(info['players'])}")
        print(f"Teams: {', '.join(info['teams'])}")
        
        if info.get('date_range'):
            print(f"Date range: {info['date_range'][0].strftime('%Y-%m-%d')} to {info['date_range'][1].strftime('%Y-%m-%d')}")
            
        print("="*50 + "\n")
    
    def _print_help(self):
        """Print help information."""
        help_text = """
Cricket Knowledge and Analysis Tool (CrickKAT)
=============================================

Available Commands:
------------------

help                          - Show this help message
quit                          - Exit CrickKAT

Data Loading:
load <filename>               - Load a specific data file
files                         - List available data files
info                          - Show summary of current data

Player Analysis:
player <name>                 - Show comprehensive stats for a player
compare <player1,player2,...> - Compare multiple players
ranking <metric>              - Show team/player rankings (default: Win Percentage)

Team Analysis:
team <name>                   - Show team performance stats
h2h <team1> <team2>           - Show head-to-head stats between teams
teams                         - List all teams in the data

Visualization:
plot player <name> [metrics]  - Plot player performance (comma-separated metrics)
plot team <name> [metrics]    - Plot team performance (comma-separated metrics)
plot compare <p1,p2> <metric> - Compare players on a metric
plot h2h <team1> <team2>      - Visualize head-to-head stats
plot ranking [metric]         - Visualize team rankings
plot save <filename>          - Save last plot to file

Filtering:
filter player <name>          - Filter data by player
filter team <name>            - Filter data by team
filter opponent <name>        - Filter data by opponent
filter date <start> <end>     - Filter by date range (YYYY-MM-DD)
filter reset                  - Reset all filters

Examples:
---------
player Virat Kohli            - Show Virat Kohli's stats
compare Virat Kohli,Steve Smith,Babar Azam - Compare these players
plot player Virat Kohli Runs,Wickets - Plot Virat's runs and wickets
"""
        print(help_text)
    
    def run(self):
        """Run the CrickKAT command-line interface."""
        print("\nWelcome to CrickKAT - Cricket Knowledge and Analysis Tool!")
        print("Type 'help' for a list of commands or 'quit' to exit.")
        
        last_plot = None
        
        while True:
            try:
                # Get command from user
                command = input("\nCrickKAT> ").strip()
                
                if not command:
                    continue
                    
                # Split command into parts
                parts = command.split()
                cmd = parts[0].lower()
                
                # Process commands
                if cmd == "quit" or cmd == "exit":
                    print("Exiting CrickKAT. Goodbye!")
                    break
                    
                elif cmd == "help":
                    self._print_help()
                    
                # Data loading commands
                elif cmd == "load":
                    if len(parts) < 2:
                        print("Error: Please specify a file to load.")
                        continue
                        
                    filename = parts[1]
                    try:
                        self.data = self.data_loader.load_data(filename)
                        self.current_file = filename
                        self.analyzer.set_data(self.data)
                        self.visualizer.set_data(self.data)
                        print(f"Successfully loaded data from '{filename}'")
                        self._display_data_summary()
                    except FileNotFoundError as e:
                        print(f"Error: {str(e)}")
                        
                elif cmd == "files":
                    files = self.data_loader.available_files
                    if files:
                        print("Available data files:")
                        for i, file in enumerate(files, 1):
                            print(f"  {i}. {file}")
                    else:
                        print("No data files found.")
                        
                elif cmd == "info":
                    self._display_data_summary()
                    
                # Player analysis commands
                elif cmd == "player":
                    if len(parts) < 2:
                        print("Error: Please specify a player name.")
                        continue
                        
                    player_name = " ".join(parts[1:])
                    try:
                        player_stats = self.analyzer.get_player_stats(player_name)
                        if "error" in player_stats:
                            print(f"Error: {player_stats['error']}")
                            continue
                            
                        print("\n" + "="*50)
                        print(f"Player Stats: {player_name}")
                        print("="*50)
                        
                        # Print batting stats
                        if "total_runs" in player_stats:
                            print("\nBatting:")
                            print(f"  Total Runs: {player_stats['total_runs']}")
                            print(f"  Highest Score: {player_stats['highest_score']}")
                            print(f"  Average: {player_stats['average_runs']}")
                            print(f"  Fifties: {player_stats['fifties']}")
                            print(f"  Hundreds: {player_stats['hundreds']}")
                            if "average_strike_rate" in player_stats:
                                print(f"  Strike Rate: {player_stats['average_strike_rate']}")
                                
                        # Print bowling stats
                        if "total_wickets" in player_stats:
                            print("\nBowling:")
                            print(f"  Total Wickets: {player_stats['total_wickets']}")
                            print(f"  Best Bowling: {player_stats['best_bowling']}")
                            print(f"  Average: {player_stats['average_wickets_per_match']}")
                            if "economy_rate" in player_stats:
                                print(f"  Economy Rate: {player_stats['economy_rate']}")
                                
                        # Print fielding stats
                        if "total_catches" in player_stats or "total_stumpings" in player_stats:
                            print("\nFielding:")
                            if "total_catches" in player_stats:
                                print(f"  Catches: {player_stats['total_catches']}")
                            if "total_stumpings" in player_stats:
                                print(f"  Stumpings: {player_stats['total_stumpings']}")
                                
                        # Print general info
                        print("\nGeneral:")
                        print(f"  Matches: {player_stats['total_matches']}")
                        print(f"  Teams: {', '.join(player_stats['teams_played_for'])}")
                        if "average_win_percentage" in player_stats:
                            print(f"  Win Percentage: {player_stats['average_win_percentage']}%")
                            
                        print("="*50)
                        
                    except Exception as e:
                        print(f"Error analyzing player: {str(e)}")
                        
                elif cmd == "compare":
                    if len(parts) < 2:
                        print("Error: Please specify players to compare (comma-separated).")
                        continue
                        
                    players = parts[1].split(',')
                    
                    # Check for additional metric specifications
                    metrics = None
                    if len(parts) > 2:
                        metrics = parts[2].split(',')
                        
                    try:
                        comparison = self.analyzer.compare_players(players, metrics)
                        if comparison.empty:
                            print("No data found for the specified players.")
                            continue
                            
                        print("\n" + "="*50)
                        print(f"Player Comparison: {', '.join(players)}")
                        print("="*50)
                        print(comparison)
                        print("="*50)
                        
                    except Exception as e:
                        print(f"Error comparing players: {str(e)}")
                        
                elif cmd == "ranking":
                    metric = "Win Percentage"
                    if len(parts) > 1:
                        metric = " ".join(parts[1:])
                        
                    try:
                        rankings = self.analyzer.calculate_ranking(metric)
                        if rankings.empty:
                            print("No data available for rankings.")
                            continue
                            
                        print("\n" + "="*50)
                        print(f"Team Rankings by {metric}")
                        print("="*50)
                        print(rankings)
                        print("="*50)
                        
                    except Exception as e:
                        print(f"Error calculating rankings: {str(e)}")
                        
                # Team analysis commands
                elif cmd == "team":
                    if len(parts) < 2:
                        print("Error: Please specify a team name.")
                        continue
                        
                    team_name = " ".join(parts[1:])
                    try:
                        team_stats = self.analyzer.team_performance(team_name)
                        if "error" in team_stats:
                            print(f"Error: {team_stats['error']}")
                            continue
                            
                        print("\n" + "="*50)
                        print(f"Team Stats: {team_name}")
                        print("="*50)
                        
                        # Print general info
                        print(f"Total Matches: {team_stats['total_matches']}")
                        print(f"Players: {len(team_stats['players'])}")
                        if "average_win_percentage" in team_stats and team_stats['average_win_percentage']:
                            print(f"Win Percentage: {team_stats['average_win_percentage']}%")
                            
                        # Print batting stats
                        if "total_runs" in team_stats and team_stats['total_runs']:
                            print("\nBatting:")
                            print(f"  Total Runs: {team_stats['total_runs']}")
                            print(f"  Average Runs/Match: {team_stats['average_runs_per_match']}")
                            if "highest_team_score" in team_stats:
                                print(f"  Highest Team Score: {team_stats['highest_team_score']}")
                                
                        # Print bowling stats
                        if "total_wickets" in team_stats and team_stats['total_wickets']:
                            print("\nBowling:")
                            print(f"  Total Wickets: {team_stats['total_wickets']}")
                            print(f"  Average Wickets/Match: {team_stats['average_wickets_per_match']}")
                            
                        # Print performance against opponents
                        if "opponent_stats" in team_stats:
                            print("\nPerformance against opponents:")
                            for opponent, stats in team_stats["opponent_stats"].items():
                                win_pct = stats.get("avg_win_percentage")
                                win_str = f", Win %: {win_pct}%" if win_pct else ""
                                print(f"  vs {opponent}: {stats['matches']} matches{win_str}")
                                
                        # Print top performers
                        if "top_run_scorers" in team_stats:
                            print("\nTop Run Scorers:")
                            for player, runs in team_stats["top_run_scorers"].items():
                                print(f"  {player}: {runs} runs")
                                
                        if "top_wicket_takers" in team_stats:
                            print("\nTop Wicket Takers:")
                            for player, wickets in team_stats["top_wicket_takers"].items():
                                print(f"  {player}: {wickets} wickets")
                                
                        print("="*50)
                        
                    except Exception as e:
                        print(f"Error analyzing team: {str(e)}")
                        
                elif cmd == "h2h":
                    if len(parts) < 3:
                        print("Error: Please specify two teams for head-to-head analysis.")
                        continue
                        
                    team1 = parts[1]
                    team2 = parts[2]
                    
                    try:
                        h2h_stats = self.analyzer.head_to_head(team1, team2)
                        if "error" in h2h_stats:
                            print(f"Error: {h2h_stats['error']}")
                            continue
                            
                        print("\n" + "="*50)
                        print(f"Head-to-Head: {team1} vs {team2}")
                        print("="*50)
                        
                        print(f"Total Matches: {h2h_stats['total_matches']}")
                        
                        # Team 1 stats
                        t1_stats = h2h_stats["team1_stats"]
                        print(f"\n{team1} Stats:")
                        print(f"  Matches: {t1_stats['matches']}")
                        if t1_stats.get('avg_win_percentage'):
                            print(f"  Win Percentage: {t1_stats['avg_win_percentage']}%")
                        if t1_stats.get('total_runs'):
                            print(f"  Total Runs: {t1_stats['total_runs']}")
                        if t1_stats.get('total_wickets'):
                            print(f"  Total Wickets: {t1_stats['total_wickets']}")
                            
                        # Team 2 stats
                        t2_stats = h2h_stats["team2_stats"]
                        print(f"\n{team2} Stats:")
                        print(f"  Matches: {t2_stats['matches']}")
                        if t2_stats.get('avg_win_percentage'):
                            print(f"  Win Percentage: {t2_stats['avg_win_percentage']}%")
                        if t2_stats.get('total_runs'):
                            print(f"  Total Runs: {t2_stats['total_runs']}")
                        if t2_stats.get('total_wickets'):
                            print(f"  Total Wickets: {t2_stats['total_wickets']}")
                            
                        # Top performers
                        if "top_run_scorers" in h2h_stats:
                            print("\nTop Run Scorers:")
                            for player, runs in h2h_stats["top_run_scorers"].items():
                                print(f"  {player}: {runs} runs")
                                
                        if "top_wicket_takers" in h2h_stats:
                            print("\nTop Wicket Takers:")
                            for player, wickets in h2h_stats["top_wicket_takers"].items():
                                print(f"  {player}: {wickets} wickets")
                                
                        print("="*50)
                        
                    except Exception as e:
                        print(f"Error analyzing head-to-head: {str(e)}")
                        
                elif cmd == "teams":
                    if self.data is None:
                        print("No data loaded.")
                        continue
                        
                    teams = self.data_loader.get_teams()
                    print("\nTeams in the dataset:")
                    for i, team in enumerate(teams, 1):
                        print(f"  {i}. {team}")
                        
                # Visualization commands
                elif cmd == "plot":
                    if len(parts) < 2:
                        print("Error: Please specify what to plot.")
                        continue
                        
                    plot_type = parts[1].lower()
                    
                    if plot_type == "player":
                        if len(parts) < 3:
                            print("Error: Please specify a player name.")
                            continue
                            
                        player_name = parts[2]
                        
                        # Check for metrics
                        metrics = None
                        if len(parts) > 3:
                            metrics = parts[3].split(',')
                            
                        try:
                            fig = self.visualizer.player_performance(player_name, metrics)
                            last_plot = fig
                            plt.tight_layout()
                            plt.show()
                        except Exception as e:
                            print(f"Error plotting player performance: {str(e)}")
                            
                    elif plot_type == "team":
                        if len(parts) < 3:
                            print("Error: Please specify a team name.")
                            continue
                            
                        team_name = parts[2]
                        
                        # Check for metrics
                        metrics = None
                        if len(parts) > 3:
                            metrics = parts[3].split(',')
                            
                        try:
                            fig = self.visualizer.team_performance(team_name, metrics)
                            last_plot = fig
                            plt.tight_layout()
                            plt.show()
                        except Exception as e:
                            print(f"Error plotting team performance: {str(e)}")
                            
                    elif plot_type == "compare":
                        if len(parts) < 4:
                            print("Error: Please specify players to compare and a metric.")
                            continue
                            
                        players = parts[2].split(',')
                        metric = parts[3]
                        
                        try:
                            fig = self.visualizer.compare_players(players, metric)
                            last_plot = fig
                            plt.tight_layout()
                            plt.show()
                        except Exception as e:
                            print(f"Error plotting player comparison: {str(e)}")
                            
                    elif plot_type == "h2h":
                        if len(parts) < 4:
                            print("Error: Please specify two teams for head-to-head visualization.")
                            continue
                            
                        team1 = parts[2]
                        team2 = parts[3]
                        
                        try:
                            fig = self.visualizer.head_to_head_comparison(team1, team2)
                            last_plot = fig
                            plt.tight_layout()
                            plt.show()
                        except Exception as e:
                            print(f"Error plotting head-to-head comparison: {str(e)}")
                            
                    elif plot_type == "ranking":
                        metric = "Win Percentage"
                        if len(parts) > 2:
                            metric = parts[2]
                            
                        try:
                            fig = self.visualizer.plot_rankings(metric)
                            last_plot = fig
                            plt.tight_layout()
                            plt.show()
                        except Exception as e:
                            print(f"Error plotting rankings: {str(e)}")
                            
                    elif plot_type == "save":
                        if last_plot is None:
                            print("No plot to save. Generate a plot first.")
                            continue
                            
                        filename = "plot.png"
                        if len(parts) > 2:
                            filename = parts[2]
                            if not filename.endswith(('.png', '.jpg', '.pdf')):
                                filename += '.png'
                                
                        try:
                            save_path = os.path.join(self.visualizer.output_dir, filename)
                            last_plot.savefig(save_path, dpi=300, bbox_inches='tight')
                            print(f"Plot saved to {save_path}")
                        except Exception as e:
                            print(f"Error saving plot: {str(e)}")
                            
                    else:
                        print(f"Unknown plot type: {plot_type}")
                        print("Available plot types: player, team, compare, h2h, ranking, save")
                        
                # Filtering commands
                elif cmd == "filter":
                    if len(parts) < 2:
                        print("Error: Please specify a filter type.")
                        continue
                        
                    filter_type = parts[1].lower()
                    
                    if filter_type == "reset":
                        # Reset to original data
                        if self.current_file:
                            self.data = self.data_loader.load_data(self.current_file)
                            self.analyzer.set_data(self.data)
                            self.visualizer.set_data(self.data)
                            print("Filters reset. All data loaded.")
                            
                    elif filter_type == "player":
                        if len(parts) < 3:
                            print("Error: Please specify a player name.")
                            continue
                            
                        player_name = " ".join(parts[2:])
                        try:
                            filtered_data = self.data_loader.filter_data(player=player_name)
                            if filtered_data.empty:
                                print(f"No data found for player: {player_name}")
                                continue
                                
                            self.data = filtered_data
                            self.analyzer.set_data(self.data)
                            self.visualizer.set_data(self.data)
                            print(f"Data filtered for player: {player_name}")
                            print(f"Filtered dataset has {len(filtered_data)} records.")
                        except Exception as e:
                            print(f"Error filtering data: {str(e)}")
                            
                    elif filter_type == "team":
                        if len(parts) < 3:
                            print("Error: Please specify a team name.")
                            continue
                            
                        team_name = " ".join(parts[2:])
                        try:
                            filtered_data = self.data_loader.filter_data(team=team_name)
                            if filtered_data.empty:
                                print(f"No data found for team: {team_name}")
                                continue
                                
                            self.data = filtered_data
                            self.analyzer.set_data(self.data)
                            self.visualizer.set_data(self.data)
                            print(f"Data filtered for team: {team_name}")
                            print(f"Filtered dataset has {len(filtered_data)} records.")
                        except Exception as e:
                            print(f"Error filtering data: {str(e)}")
                            
                    elif filter_type == "opponent":
                        if len(parts) < 3:
                            print("Error: Please specify an opponent name.")
                            continue
                            
                        opponent_name = " ".join(parts[2:])
                        try:
                            filtered_data = self.data_loader.filter_data(opponent=opponent_name)
                            if filtered_data.empty:
                                print(f"No data found for opponent: {opponent_name}")
                                continue
                                
                            self.data = filtered_data
                            self.analyzer.set_data(self.data)
                            self.visualizer.set_data(self.data)
                            print(f"Data filtered for opponent: {opponent_name}")
                            print(f"Filtered dataset has {len(filtered_data)} records.")
                        except Exception as e:
                            print(f"Error filtering data: {str(e)}")
                            
                    elif filter_type == "date":
                        if len(parts) < 4:
                            print("Error: Please specify start and end dates (YYYY-MM-DD).")
                            continue
                            
                        start_date = parts[2]
                        end_date = parts[3]
                        
                        try:
                            start_date = pd.to_datetime(start_date)
                            end_date = pd.to_datetime(end_date)
                            filtered_data = self.data_loader.filter_data(date_range=(start_date, end_date))
                            
                            if filtered_data.empty:
                                print(f"No data found between {start_date.strftime('%Y-%m-%d')} and {end_date.strftime('%Y-%m-%d')}")
                                continue
                                
                            self.data = filtered_data
                            self.analyzer.set_data(self.data)
                            self.visualizer.set_data(self.data)
                            print(f"Data filtered for date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
                            print(f"Filtered dataset has {len(filtered_data)} records.")
                        except Exception as e:
                            print(f"Error filtering data: {str(e)}")
                            
                    else:
                        print(f"Unknown filter type: {filter_type}")
                        print("Available filter types: player, team, opponent, date, reset")
                        
                else:
                    print(f"Unknown command: {cmd}")
                    print("Type 'help' to see available commands.")
                    
            except Exception as e:
                print(f"Error: {str(e)}")
                
        # Clean up before exiting
        plt.close('all')

if __name__ == "__main__":
    app = CrickKAT()
    app.run()