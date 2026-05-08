"""
Utility functions for protein analysis project.

Contains helper functions for logging, file handling, and data processing.
"""

import logging
import json
import pickle
from pathlib import Path
from typing import Any, Dict, List
import numpy as np
import pandas as pd
from datetime import datetime


def setup_logging(log_file: str = "logs/analysis.log", level: str = "INFO") -> None:
    """
    Set up logging configuration.

    Parameters
    ----------
    log_file : str
        Path to log file
    level : str
        Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Create logs directory if it doesn't exist
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


def save_model(model: Any, filepath: str) -> None:
    """
    Save trained model to disk.

    Parameters
    ----------
    model : Any
        Trained model object
    filepath : str
        Path to save model
    """
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'wb') as f:
        pickle.dump(model, f)
    print(f"Model saved to {filepath}")


def load_model(filepath: str) -> Any:
    """
    Load trained model from disk.

    Parameters
    ----------
    filepath : str
        Path to model file

    Returns
    -------
    Any
        Loaded model
    """
    with open(filepath, 'rb') as f:
        model = pickle.load(f)
    return model


def save_dataframe(df: pd.DataFrame, filepath: str, format: str = 'csv') -> None:
    """
    Save DataFrame to file.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to save
    filepath : str
        Output file path
    format : str
        File format ('csv', 'excel', 'parquet', 'feather')
    """
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    if format == 'csv':
        df.to_csv(filepath, index=False)
    elif format == 'excel':
        df.to_excel(filepath, index=False)
    elif format == 'parquet':
        df.to_parquet(filepath, index=False)
    elif format == 'feather':
        df.to_feather(filepath)
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    print(f"DataFrame saved to {filepath}")


def load_dataframe(filepath: str) -> pd.DataFrame:
    """
    Load DataFrame from file.

    Parameters
    ----------
    filepath : str
        Path to data file

    Returns
    -------
    pd.DataFrame
        Loaded DataFrame
    """
    filepath = Path(filepath)
    
    if filepath.suffix == '.csv':
        return pd.read_csv(filepath)
    elif filepath.suffix in ['.xls', '.xlsx']:
        return pd.read_excel(filepath)
    elif filepath.suffix == '.parquet':
        return pd.read_parquet(filepath)
    elif filepath.suffix == '.feather':
        return pd.read_feather(filepath)
    else:
        raise ValueError(f"Unsupported file format: {filepath.suffix}")


def save_json(data: Dict, filepath: str, indent: int = 2) -> None:
    """
    Save dictionary to JSON file.

    Parameters
    ----------
    data : dict
        Data to save
    filepath : str
        Output file path
    indent : int
        JSON indentation level
    """
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=indent)
    print(f"Data saved to {filepath}")


def load_json(filepath: str) -> Dict:
    """
    Load dictionary from JSON file.

    Parameters
    ----------
    filepath : str
        Path to JSON file

    Returns
    -------
    dict
        Loaded data
    """
    with open(filepath, 'r') as f:
        return json.load(f)


def handle_missing_values(df: pd.DataFrame, method: str = 'mean') -> pd.DataFrame:
    """
    Handle missing values in DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with potential missing values
    method : str
        Imputation method ('mean', 'median', 'drop')

    Returns
    -------
    pd.DataFrame
        DataFrame with handled missing values
    """
    if method == 'mean':
        return df.fillna(df.mean(numeric_only=True))
    elif method == 'median':
        return df.fillna(df.median(numeric_only=True))
    elif method == 'drop':
        return df.dropna()
    else:
        raise ValueError(f"Unknown method: {method}")


def normalize_features(df: pd.DataFrame, columns: List[str] = None) -> pd.DataFrame:
    """
    Normalize features to unit variance.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    columns : list, optional
        Columns to normalize. If None, normalize all numeric columns.

    Returns
    -------
    pd.DataFrame
        DataFrame with normalized features
    """
    df_norm = df.copy()
    
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns
    
    for col in columns:
        mean = df_norm[col].mean()
        std = df_norm[col].std()
        if std > 0:
            df_norm[col] = (df_norm[col] - mean) / std
    
    return df_norm


def create_feature_report(features: Dict, output_file: str = None) -> str:
    """
    Generate a text report of features.

    Parameters
    ----------
    features : dict
        Dictionary of features and values
    output_file : str, optional
        File to save report

    Returns
    -------
    str
        Formatted report text
    """
    report = []
    report.append("=" * 60)
    report.append("FEATURE EXTRACTION REPORT")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 60)
    report.append("")
    
    for feature, value in features.items():
        if isinstance(value, float):
            report.append(f"{feature:.<40} {value:>15.6f}")
        else:
            report.append(f"{feature:.<40} {str(value):>15}")
    
    report.append("")
    report.append("=" * 60)
    
    report_text = "\n".join(report)
    
    if output_file:
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(report_text)
        print(f"Report saved to {output_file}")
    
    return report_text


def create_summary_statistics(df: pd.DataFrame, output_file: str = None) -> pd.DataFrame:
    """
    Generate summary statistics for DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    output_file : str, optional
        File to save statistics

    Returns
    -------
    pd.DataFrame
        Summary statistics
    """
    stats = df.describe().T
    
    # Add additional statistics
    stats['skewness'] = df.skew()
    stats['kurtosis'] = df.kurtosis()
    
    if output_file:
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        stats.to_csv(output_file)
        print(f"Statistics saved to {output_file}")
    
    return stats


def validate_config(config: Dict, required_keys: List[str]) -> bool:
    """
    Validate configuration dictionary.

    Parameters
    ----------
    config : dict
        Configuration to validate
    required_keys : list
        List of required keys

    Returns
    -------
    bool
        True if valid
    """
    for key in required_keys:
        if key not in config:
            raise KeyError(f"Missing required configuration key: {key}")
    return True


def get_file_size(filepath: str) -> str:
    """
    Get human-readable file size.

    Parameters
    ----------
    filepath : str
        Path to file

    Returns
    -------
    str
        Formatted file size
    """
    size = Path(filepath).stat().st_size
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    
    return f"{size:.2f} TB"


def list_files_by_type(directory: str, extension: str) -> List[Path]:
    """
    List files by extension in directory.

    Parameters
    ----------
    directory : str
        Directory to search
    extension : str
        File extension (e.g., '.csv', '.pdb')

    Returns
    -------
    list
        List of file paths
    """
    dir_path = Path(directory)
    return list(dir_path.glob(f'*{extension}'))


def create_directory_structure(base_dir: str, structure: Dict) -> None:
    """
    Create directory structure.

    Parameters
    ----------
    base_dir : str
        Base directory path
    structure : dict
        Dictionary defining directory structure
    """
    base_path = Path(base_dir)
    
    for name in structure:
        (base_path / name).mkdir(parents=True, exist_ok=True)


def batch_process(items: List[Any], function, batch_size: int = 10) -> List[Any]:
    """
    Process items in batches.

    Parameters
    ----------
    items : list
        Items to process
    function : callable
        Function to apply to each item
    batch_size : int
        Batch size

    Returns
    -------
    list
        Processed results
    """
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        batch_results = [function(item) for item in batch]
        results.extend(batch_results)
    
    return results


if __name__ == "__main__":
    # Example usage
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Utilities module loaded successfully")
