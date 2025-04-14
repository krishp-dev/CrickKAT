import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime

class CricketAnalyzer:
    """
    A class for analyzing cricket performance data.
    """
    
    def __init__(self, data: pd.DataFrame = None):
        """
        Initialize the analyzer with cricket data.
        
        Args:
            data: Pandas DataFrame containing cricket data
        """
        self.data = data
        
    def set_data(self, data: pd.DataFrame):
        """
        Set the data to be analyzed.
        
        Args:
            data: Pandas DataFrame containing cricket data
        """
        self.data = data
        
    def _check_data(self):
        """
        Check if data is available for analysis.
        
        Raises:
            ValueError: If data is not loaded
        """
        if self.data is None:
            raise ValueError("Data not set. Please use set_data() method first.")
            
    def get_player_stats(self, player_name: str) -> Dict[str, Any]:
        """
        Get comprehensive stats for a specific player.
        
        Args:
            player_name: Name of the player
            
        Returns:
            Dictionary containing various player statistics
        """
        self._check_data()
        
        player_data = self.data[self.data['Player'] == player_name]
        
        if player_data.empty:
            return {"error": f"No data found for player: {player_name}"}
            
        # Calculate basic stats
        stats = {
            "name": player_name,
            "total_matches": len(player_data),
            "teams_played_for": player_data['Team'].unique().tolist(),
            "opponents_faced": player_data['Opponent'].unique().tolist(),
        }
        
        # Batting stats
        if 'Runs' in player_data.columns:
            stats.update({
                "total_runs": player_data['Runs'].sum(),
                "highest_score": player_data['Runs'].max(),
                "average_runs": round(player_data['Runs'].mean(), 2),
                "fifties": len(player_data[player_data['Runs'] >= 50]),
                "hundreds": len(player_data[player_data['Runs'] >= 100]),
            })
            
        # Calculate strike rate if relevant columns exist
        if 'Runs' in player_data.columns and 'Balls Faced' in player_data.columns:
            valid_innings = player_data[player_data['Balls Faced'] > 0]
            if not valid_innings.empty:
                avg_strike_rate = (valid_innings['Runs'] / valid_innings['Balls Faced'] * 100).mean()
                stats["average_strike_rate"] = round(avg_strike_rate, 2)
        
        # Bowling stats
        if 'Wickets' in player_data.columns:
            stats.update({
                "total_wickets": player_data['Wickets'].sum(),
                "best_bowling": player_data['Wickets'].max(),
                "average_wickets_per_match": round(player_data['Wickets'].mean(), 2),
                "five_wicket_hauls": len(player_data[player_data['Wickets'] >= 5]),
            })
            
        # Calculate economy rate if relevant columns exist
        if 'Overs Bowled' in player_data.columns and player_data['Overs Bowled'].sum() > 0:
            stats["economy_rate"] = round(player_data['Economy Rate'].mean(), 2)
            
        # Fielding stats
        if 'Catches' in player_data.columns:
            stats["total_catches"] = player_data['Catches'].sum()
            
        if 'Stumpings' in player_data.columns:
            stats["total_stumpings"] = player_data['Stumpings'].sum()
            
        # Win percentage
        if 'Win Percentage' in player_data.columns:
            stats["average_win_percentage"] = round(player_data['Win Percentage'].mean(), 2)
            
        return stats
    
    def compare_players(self, players: List[str], metrics: List[str] = None) -> pd.DataFrame:
        """
        Compare multiple players across specified metrics.
        
        Args:
            players: List of player names to compare
            metrics: List of metrics to compare (e.g., 'Runs', 'Wickets'). If None, includes all numeric metrics.
            
        Returns:
            DataFrame with players as index and metrics as columns
        """
        self._check_data()
        
        if not players:
            raise ValueError("Please provide a list of players to compare.")
            
        if metrics is None:
            # Default metrics (numeric columns only)
            numeric_cols = self.data.select_dtypes(include=[np.number]).columns
            metrics = [col for col in numeric_cols if col not in ['Match Date']]
        
        comparison = {}
        
        for player in players:
            player_data = self.data[self.data['Player'] == player]
            
            if player_data.empty:
                continue
                
            player_stats = {}
            
            for metric in metrics:
                if metric not in player_data.columns:
                    player_stats[metric] = None
                    continue
                    
                # Handle different types of metrics
                if metric in ['Runs', 'Wickets', 'Catches', 'Stumpings']:
                    player_stats[f"Total {metric}"] = player_data[metric].sum()
                    player_stats[f"Avg {metric}"] = round(player_data[metric].mean(), 2)
                    
                elif metric in ['Strike Rate', 'Economy Rate', 'Batting Average', 'Win Percentage']:
                    player_stats[f"Avg {metric}"] = round(player_data[metric].mean(), 2)
                    
                else:
                    player_stats[metric] = round(player_data[metric].mean(), 2)
                    
            comparison[player] = player_stats
            
        return pd.DataFrame.from_dict(comparison, orient='index')
    
    def team_performance(self, team_name: str) -> Dict[str, Any]:
        """
        Analyze the performance of a specific team.
        
        Args:
            team_name: Name of the team to analyze
            
        Returns:
            Dictionary containing team performance statistics
        """
        self._check_data()
        
        team_data = self.data[self.data['Team'] == team_name]
        
        if team_data.empty:
            return {"error": f"No data found for team: {team_name}"}
            
        # Get unique players
        players = team_data['Player'].unique().tolist()
        
        # Calculate team stats
        stats = {
            "name": team_name,
            "total_matches": len(team_data),
            "players": players,
            "opponents_faced": team_data['Opponent'].unique().tolist(),
            "average_win_percentage": round(team_data['Win Percentage'].mean(), 2) if 'Win Percentage' in team_data.columns else None,
        }
        
        # Batting stats
        if 'Runs' in team_data.columns:
            stats.update({
                "total_runs": team_data['Runs'].sum(),
                "average_runs_per_match": round(team_data['Runs'].mean(), 2),
                "highest_team_score": team_data.groupby('Match Date')['Runs'].sum().max() if 'Match Date' in team_data.columns else team_data['Runs'].max(),
            })
            
        # Bowling stats
        if 'Wickets' in team_data.columns:
            stats.update({
                "total_wickets": team_data['Wickets'].sum(),
                "average_wickets_per_match": round(team_data['Wickets'].mean(), 2),
            })
            
        # Performance against specific opponents
        opponent_stats = {}
        for opponent in stats["opponents_faced"]:
            vs_data = team_data[team_data['Opponent'] == opponent]
            win_pct = vs_data['Win Percentage'].mean() if 'Win Percentage' in vs_data.columns else None
            opponent_stats[opponent] = {
                "matches": len(vs_data),
                "avg_win_percentage": round(win_pct, 2) if win_pct is not None else None,
            }
            
        stats["opponent_stats"] = opponent_stats
        
        # Top performers
        if 'Runs' in team_data.columns:
            top_batsmen = team_data.groupby('Player')['Runs'].sum().sort_values(ascending=False).head(3)
            stats["top_run_scorers"] = top_batsmen.to_dict()
            
        if 'Wickets' in team_data.columns:
            top_bowlers = team_data.groupby('Player')['Wickets'].sum().sort_values(ascending=False).head(3)
            stats["top_wicket_takers"] = top_bowlers.to_dict()
            
        return stats
    
    def head_to_head(self, team1: str, team2: str) -> Dict[str, Any]:
        """
        Analyze head-to-head statistics between two teams.
        
        Args:
            team1: Name of the first team
            team2: Name of the second team
            
        Returns:
            Dictionary containing head-to-head statistics
        """
        self._check_data()
        
        # Matches where team1 is playing against team2
        matches1 = self.data[(self.data['Team'] == team1) & (self.data['Opponent'] == team2)]
        
        # Matches where team2 is playing against team1
        matches2 = self.data[(self.data['Team'] == team2) & (self.data['Opponent'] == team1)]
        
        if matches1.empty and matches2.empty:
            return {"error": f"No head-to-head data found between {team1} and {team2}"}
            
        # Combined stats
        h2h_stats = {
            "team1": team1,
            "team2": team2,
            "total_matches": len(matches1) + len(matches2),
        }
        
        # Team 1 stats
        team1_stats = {
            "matches": len(matches1),
            "avg_win_percentage": round(matches1['Win Percentage'].mean(), 2) if 'Win Percentage' in matches1.columns and not matches1.empty else None,
            "total_runs": matches1['Runs'].sum() if 'Runs' in matches1.columns else None,
            "total_wickets": matches1['Wickets'].sum() if 'Wickets' in matches1.columns else None,
        }
        
        # Team 2 stats
        team2_stats = {
            "matches": len(matches2),
            "avg_win_percentage": round(matches2['Win Percentage'].mean(), 2) if 'Win Percentage' in matches2.columns and not matches2.empty else None,
            "total_runs": matches2['Runs'].sum() if 'Runs' in matches2.columns else None,
            "total_wickets": matches2['Wickets'].sum() if 'Wickets' in matches2.columns else None,
        }
        
        h2h_stats["team1_stats"] = team1_stats
        h2h_stats["team2_stats"] = team2_stats
        
        # Top performers in head-to-head
        all_h2h = pd.concat([matches1, matches2])
        
        if not all_h2h.empty and 'Runs' in all_h2h.columns:
            top_batsmen = all_h2h.groupby(['Team', 'Player'])['Runs'].sum().sort_values(ascending=False).head(5)
            h2h_stats["top_run_scorers"] = {f"{team}:{player}": runs for (team, player), runs in top_batsmen.items()}
            
        if not all_h2h.empty and 'Wickets' in all_h2h.columns:
            top_bowlers = all_h2h.groupby(['Team', 'Player'])['Wickets'].sum().sort_values(ascending=False).head(5)
            h2h_stats["top_wicket_takers"] = {f"{team}:{player}": wickets for (team, player), wickets in top_bowlers.items()}
            
        return h2h_stats
    
    def performance_trend(self, player_name: str = None, team_name: str = None, metric: str = 'Runs') -> pd.DataFrame:
        """
        Calculate performance trend over time for a player or team.
        
        Args:
            player_name: Name of the player (optional)
            team_name: Name of the team (optional)
            metric: Performance metric to track
            
        Returns:
            DataFrame with performance over time
        """
        self._check_data()
        
        if player_name is None and team_name is None:
            raise ValueError("Please provide either a player name or a team name.")
            
        if 'Match Date' not in self.data.columns:
            raise ValueError("Match Date column is required for trend analysis.")
            
        if metric not in self.data.columns:
            raise ValueError(f"Metric '{metric}' not found in the data.")
            
        # Filter data
        if player_name:
            filtered_data = self.data[self.data['Player'] == player_name].copy()
            if filtered_data.empty:
                return pd.DataFrame()
        elif team_name:
            filtered_data = self.data[self.data['Team'] == team_name].copy()
            if filtered_data.empty:
                return pd.DataFrame()
        
        # Sort by date
        filtered_data = filtered_data.sort_values('Match Date')
        
        # Calculate rolling average (last 3 matches)
        filtered_data[f'{metric}_Rolling_Avg'] = filtered_data[metric].rolling(window=3, min_periods=1).mean()
        
        # Select relevant columns
        trend_data = filtered_data[['Match Date', 'Opponent', metric, f'{metric}_Rolling_Avg']]
        
        return trend_data
    
    def find_best_performers(self, metric: str = 'Runs', top_n: int = 5) -> pd.DataFrame:
        """
        Find the best performers based on a specific metric.
        
        Args:
            metric: Performance metric (e.g., 'Runs', 'Wickets')
            top_n: Number of top performers to return
            
        Returns:
            DataFrame with top performers
        """
        self._check_data()
        
        if metric not in self.data.columns:
            raise ValueError(f"Metric '{metric}' not found in the data.")
            
        # Group by player and calculate total and average
        player_stats = self.data.groupby('Player').agg({
            metric: ['sum', 'mean', 'max'],
            'Team': lambda x: list(set(x)),
        })
        
        # Rename columns
        player_stats.columns = [f'total_{metric.lower()}', f'avg_{metric.lower()}', f'best_{metric.lower()}', 'teams']
        
        # Sort by total and return top N
        top_performers = player_stats.sort_values(f'total_{metric.lower()}', ascending=False).head(top_n)
        
        return top_performers
    
    def match_analysis(self, match_date: Union[str, datetime]) -> Dict[str, Any]:
        """
        Analyze a specific match.
        
        Args:
            match_date: Date of the match
            
        Returns:
            Dictionary with match analysis
        """
        self._check_data()
        
        if 'Match Date' not in self.data.columns:
            raise ValueError("Match Date column is required for match analysis.")
            
        if isinstance(match_date, str):
            match_date = pd.to_datetime(match_date)
            
        match_data = self.data[self.data['Match Date'] == match_date]
        
        if match_data.empty:
            return {"error": f"No data found for match date: {match_date}"}
            
        # Get teams
        teams = match_data['Team'].unique()
        
        if len(teams) == 1:
            # Only one team's data available
            team = teams[0]
            opponent = match_data['Opponent'].iloc[0]
            
            analysis = {
                "match_date": match_date,
                "team": team,
                "opponent": opponent,
                "win_percentage": round(match_data['Win Percentage'].mean(), 2) if 'Win Percentage' in match_data.columns else None,
            }
            
            # Batting performance
            if 'Runs' in match_data.columns:
                top_scorer = match_data.loc[match_data['Runs'].idxmax()]
                analysis["total_runs"] = match_data['Runs'].sum()
                analysis["top_scorer"] = {
                    "name": top_scorer['Player'],
                    "runs": top_scorer['Runs'],
                    "balls_faced": top_scorer['Balls Faced'] if 'Balls Faced' in top_scorer else None,
                    "strike_rate": top_scorer['Strike Rate'] if 'Strike Rate' in top_scorer else None,
                }
                
            # Bowling performance
            if 'Wickets' in match_data.columns:
                top_bowler_idx = match_data['Wickets'].idxmax()
                if pd.notna(top_bowler_idx):
                    top_bowler = match_data.loc[top_bowler_idx]
                    analysis["total_wickets"] = match_data['Wickets'].sum()
                    analysis["top_bowler"] = {
                        "name": top_bowler['Player'],
                        "wickets": top_bowler['Wickets'],
                        "overs": top_bowler['Overs Bowled'] if 'Overs Bowled' in top_bowler else None,
                        "economy": top_bowler['Economy Rate'] if 'Economy Rate' in top_bowler else None,
                    }
                
            # Player performances
            analysis["player_performances"] = []
            for _, player_row in match_data.iterrows():
                performance = {
                    "name": player_row['Player'],
                    "runs": player_row['Runs'] if 'Runs' in player_row else None,
                    "wickets": player_row['Wickets'] if 'Wickets' in player_row else None,
                    "catches": player_row['Catches'] if 'Catches' in player_row else None,
                }
                analysis["player_performances"].append(performance)
                
        else:
            # Multiple teams' data available
            analysis = {
                "match_date": match_date,
                "teams": teams.tolist(),
                "team_performances": {},
            }
            
            for team in teams:
                team_data = match_data[match_data['Team'] == team]
                opponent = team_data['Opponent'].iloc[0]
                
                team_analysis = {
                    "opponent": opponent,
                    "win_percentage": round(team_data['Win Percentage'].mean(), 2) if 'Win Percentage' in team_data.columns else None,
                    "total_runs": team_data['Runs'].sum() if 'Runs' in team_data.columns else None,
                    "total_wickets": team_data['Wickets'].sum() if 'Wickets' in team_data.columns else None,
                }
                
                analysis["team_performances"][team] = team_analysis
                
        return analysis
    
    def calculate_ranking(self, metric: str = 'Win Percentage') -> pd.DataFrame:
        """
        Calculate team rankings based on a specified metric.
        
        Args:
            metric: Metric to base the ranking on
            
        Returns:
            DataFrame with team rankings
        """
        self._check_data()
        
        if metric not in self.data.columns:
            raise ValueError(f"Metric '{metric}' not found in the data.")
            
        # Get all teams
        all_teams = set(self.data['Team'].unique()) | set(self.data['Opponent'].unique())
        
        rankings = []
        
        for team in all_teams:
            team_data = self.data[self.data['Team'] == team]
            
            if team_data.empty:
                continue
                
            team_stats = {
                "team": team,
                f"avg_{metric.lower()}": round(team_data[metric].mean(), 2),
                "matches": len(team_data),
            }
            
            # Additional stats
            if 'Runs' in team_data.columns:
                team_stats["total_runs"] = team_data['Runs'].sum()
                team_stats["avg_runs"] = round(team_data['Runs'].mean(), 2)
                
            if 'Wickets' in team_data.columns:
                team_stats["total_wickets"] = team_data['Wickets'].sum()
                team_stats["avg_wickets"] = round(team_data['Wickets'].mean(), 2)
                
            rankings.append(team_stats)
            
        # Convert to DataFrame and sort
        rankings_df = pd.DataFrame(rankings)
        if not rankings_df.empty:
            rankings_df = rankings_df.sort_values(f"avg_{metric.lower()}", ascending=False)
            rankings_df['rank'] = range(1, len(rankings_df) + 1)
            
            # Reorder columns to put rank first
            cols = rankings_df.columns.tolist()
            cols = ['rank'] + [col for col in cols if col != 'rank']
            rankings_df = rankings_df[cols]
            
        return rankings_df