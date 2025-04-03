import os
from typing import List


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