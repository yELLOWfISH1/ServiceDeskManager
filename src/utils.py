"""
Utilities module for common helper functions
"""
import pandas as pd
from pathlib import Path
from typing import List, Tuple
from datetime import datetime


def load_spreadsheet(file_path: str) -> pd.DataFrame | None:
    """
    Load spreadsheet file (xlsx, xls, csv)
    
    Args:
        file_path: Path to the spreadsheet
        
    Returns:
        DataFrame or None if load fails
    """
    try:
        path = Path(file_path)
        
        if path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        elif path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path)
        else:
            return None
        
        return df
    except Exception as e:
        print(f"Error loading spreadsheet: {e}")
        return None


def validate_spreadsheet_columns(df: pd.DataFrame, required_columns: List[str]) -> Tuple[bool, List[str]]:
    """
    Validate that spreadsheet contains required columns
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names (case-insensitive)
        
    Returns:
        Tuple of (is_valid, missing_columns)
    """
    df_cols = [col.lower() for col in df.columns]
    missing = []
    
    for col in required_columns:
        if col.lower() not in df_cols:
            missing.append(col)
    
    return len(missing) == 0, missing


def clean_dataframe(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Clean DataFrame by selecting columns, lowercasing headers, and removing NaN
    
    Args:
        df: DataFrame to clean
        columns: Columns to select
        
    Returns:
        Cleaned DataFrame
    """
    # Lowercase columns
    df.columns = df.columns.str.lower()
    
    # Select columns (case-insensitive)
    available_cols = [col for col in columns if col.lower() in df.columns]
    df = df[available_cols].dropna()
    
    return df


def generate_timestamp() -> str:
    """Generate timestamp for file names"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_dataframe_to_file(df: pd.DataFrame, file_path: str) -> bool:
    """
    Save DataFrame to file
    
    Args:
        df: DataFrame to save
        file_path: Path to save to
        
    Returns:
        True if successful
    """
    try:
        path = Path(file_path)
        
        if path.suffix.lower() in ['.xlsx', '.xls']:
            df.to_excel(file_path, index=False)
        elif path.suffix.lower() == '.csv':
            df.to_csv(file_path, index=False)
        else:
            return False
        
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False
