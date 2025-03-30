# utils.py

import csv
import os


def read_names_from_csv(csv_path):
    """
    Read names from a CSV file (single column with names).

    Args:
        csv_path: Path to the CSV file

    Returns:
        List of names (strings)
    """
    names = []

    # Determine the encoding to use
    encodings = ['utf-8-sig', 'utf-8', 'latin-1']

    for encoding in encodings:
        try:
            with open(csv_path, 'r', newline='', encoding=encoding) as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row and len(row) > 0 and row[0].strip():
                        names.append(row[0].strip())

            # If we reached here without error, break the loop
            break
        except UnicodeDecodeError:
            # Try the next encoding
            continue
        except Exception as e:
            # Re-raise other exceptions
            raise e

    return names


def ensure_dir(directory):
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        directory: Path to the directory
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
