# main.py

import os
from typing import List
from dataframe import load_snapshots_to_dataframe, load_dataframe, save_dataframe
from plot import plot_total_liquidity, plot_average_fee, plot_unique_makers


def get_snapshot_filepaths(directory_path: str) -> List[str]:
    """
    Traverses the directory containing daily snapshot directories to get a list of snapshot filepaths.

    Parameters:
        directory_path (str): The root directory containing daily snapshot directories.

    Returns:
        List[str]: List of snapshot filepaths.
    """
    snapshot_filepaths = []
    # List directories in the data directory
    for date_dir in sorted(os.listdir(directory_path)):
        full_date_dir = os.path.join(directory_path, date_dir)
        if os.path.isdir(full_date_dir):
            # List files in the date directory
            for filename in sorted(os.listdir(full_date_dir)):
                if filename.endswith('.json'):
                    filepath = os.path.join(full_date_dir, filename)
                    snapshot_filepaths.append(filepath)
    return snapshot_filepaths


def main():
    directory_path = 'data'  # Update this to your root directory path
    df_pickle_path = 'dataframe.pkl'  # Path to save the DataFrame

    # Check if the DataFrame pickle file exists
    if os.path.exists(df_pickle_path):
        df_stats = load_dataframe(df_pickle_path)
    else:
        filepaths = get_snapshot_filepaths(directory_path)
        df_stats = load_snapshots_to_dataframe(filepaths)
        save_dataframe(df_stats, df_pickle_path)

    # Now you can perform time series analysis on df_stats
    print(df_stats.head())

    # Plotting
    plot_total_liquidity(df_stats)
    plot_average_fee(df_stats)
    plot_unique_makers(df_stats)


if __name__ == "__main__":
    main()
