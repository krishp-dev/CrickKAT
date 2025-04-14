import pandas as pd
import os
from typing import Optional, List, Dict, Any, Union

class DataLoader:
    """
    A class for loading and preprocessing cricket data.
    """
    
    def __init__(self, data_dir: str = 'data'):
        """
        Initialize the DataLoader with the path to the data directory.
        
        Args:
            data_dir: Path to the directory containing cricket data files
        """
        self.data_dir = data_dir
        self.data = None
        self.available_files = self._get_available_files()
        
    def _get_available_files(self) -> List[str]:
        """
        Get a list of available CSV files in the data directory.
        
        Returns:
            List of CSV filenames
        """
        if not os.path.exists(self.data_dir):
            print(f"Data directory '{self.data_dir}' not found.")
            return []
            
        return [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
    
    def load_data(self, filename: str = None) -> pd.DataFrame:
        """
        Load data from a CSV file.
        
        Args:
            filename: Name of the CSV file to load. If None, loads the first available file.
            
        Returns:
            Pandas DataFrame containing cricket data
        """
        if not self.available_files:
            raise FileNotFoundError(f"No CSV files found in '{self.data_dir}'")
            
        if filename is None:
            filename = self.available_files[0]
        elif filename not in self.available_files:
            raise FileNotFoundError(f"File '{filename}' not found in '{self.data_dir}'")
            
        file_path = os.path.join(self.data_dir, filename)
        self.data = pd.read_csv(file_path)
        
        # Convert date columns to datetime
        if 'Match Date' in self.data.columns:
            self.data['Match Date'] = pd.to_datetime(self.data['Match Date'])
            
        return self.data
    
    def get_players(self) -> List[str]:
        """
        Get a list of all players in the dataset.
        
        Returns:
            List of player names
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")
            
        return self.data['Player'].unique().tolist()
    
    def get_teams(self) -> List[str]:
        """
        Get a list of all teams in the dataset.
        
        Returns:
            List of team names
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")
            
        teams = set(self.data['Team'].unique()) | set(self.data['Opponent'].unique())
        return sorted(list(teams))
    
    def filter_data(self, 
                   player: Optional[str] = None,
                   team: Optional[str] = None,
                   opponent: Optional[str] = None,
                   date_range: Optional[tuple] = None) -> pd.DataFrame:
        """
        Filter the data based on provided criteria.
        
        Args:
            player: Player name to filter by
            team: Team name to filter by
            opponent: Opponent team name to filter by
            date_range: Tuple of (start_date, end_date) to filter by
            
        Returns:
            Filtered pandas DataFrame
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")
            
        filtered_data = self.data.copy()
        
        if player:
            filtered_data = filtered_data[filtered_data['Player'] == player]
            
        if team:
            filtered_data = filtered_data[filtered_data['Team'] == team]
            
        if opponent:
            filtered_data = filtered_data[filtered_data['Opponent'] == opponent]
            
        if date_range:
            start_date, end_date = date_range
            filtered_data = filtered_data[(filtered_data['Match Date'] >= start_date) & 
                                          (filtered_data['Match Date'] <= end_date)]
            
        return filtered_data
    
    def get_column_names(self) -> List[str]:
        """
        Get the column names of the loaded data.
        
        Returns:
            List of column names
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")
            
        return self.data.columns.tolist()
    
    def get_summary_stats(self, columns: List[str] = None) -> pd.DataFrame:
        """
        Get summary statistics for numerical columns.
        
        Args:
            columns: List of columns to get statistics for. If None, use all numerical columns.
            
        Returns:
            DataFrame with summary statistics
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")
            
        if columns is None:
            # Select numeric columns only
            numeric_columns = self.data.select_dtypes(include=['int64', 'float64']).columns
            columns = numeric_columns
        
        return self.data[columns].describe()
    
    def get_data_info(self) -> Dict[str, Any]:
        """
        Get basic information about the loaded data.
        
        Returns:
            Dictionary containing metadata about the dataset
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")
            
        info = {
            'num_rows': len(self.data),
            'num_columns': len(self.data.columns),
            'column_names': self.data.columns.tolist(),
            'players': self.get_players(),
            'teams': self.get_teams(),
            'date_range': [self.data['Match Date'].min(), self.data['Match Date'].max()] if 'Match Date' in self.data.columns else None,
        }
        
        return info