from typing import List
import pandas as pd

from .snapshot import load_and_process_snapshot


def save_dataframe(df: pd.DataFrame, filepath: str):
    """
    Saves the DataFrame to a pickle file.

    Parameters:
        df (pd.DataFrame): The DataFrame to save.
        filepath (str): The path to the pickle file.
    """
    df.to_pickle(filepath)
    print(f"DataFrame saved to {filepath}")


def load_dataframe(filepath: str) -> pd.DataFrame:
    """
    Loads the DataFrame from a pickle file.

    Parameters:
        filepath (str): The path to the pickle file.

    Returns:
        pd.DataFrame: The loaded DataFrame.
    """
    df = pd.read_pickle(filepath)
    print(f"DataFrame loaded from {filepath}")
    return df


def extract_timestamp_from_filepath(filepath: str) -> pd.Timestamp:
    """
    Extracts a timestamp from the filepath.

    Assumes the filepath is of the format: 'data/YYYY-MM-DD/orderbook_HH-MM.json'

    Parameters:
        filepath (str): The full path to the snapshot file.

    Returns:
        pd.Timestamp: The extracted timestamp.
    """
    import re
    from datetime import datetime

    # Adjust the regex pattern to match the new filepath format
    pattern = r'.*/(\d{4}-\d{2}-\d{2})/orderbook_(\d{2}-\d{2}).json$'
    match = re.match(pattern, filepath)
    if match:
        date_str = match.group(1)      # Extracts 'YYYY-MM-DD'
        time_str = match.group(2)      # Extracts 'HH-MM'
        datetime_str = f"{date_str} {time_str}"
        timestamp = datetime.strptime(datetime_str, '%Y-%m-%d %H-%M')
        return pd.Timestamp(timestamp)
    else:
        # If no timestamp found, return NaT (Not a Time)
        return pd.NaT


def load_snapshots_to_dataframe(filepaths: List[str]) -> pd.DataFrame:
    """
    Loads and processes snapshots from a list of filepaths to create a DataFrame.

    Parameters:
        filepaths (List[str]): List of snapshot filepaths.

    Returns:
        pd.DataFrame: DataFrame containing computed analysis for each snapshot.
    """
    records = []
    for filepath in filepaths:
        timestamp = extract_timestamp_from_filepath(filepath)
        if pd.isnull(timestamp):
            continue  # Skip files without a valid timestamp
        snapshot_stats = load_and_process_snapshot(filepath, timestamp)
        records.append(snapshot_stats)

    df_stats = pd.DataFrame(records)
    df_stats.set_index('timestamp', inplace=True)
    df_stats.sort_index(inplace=True)
    return df_stats