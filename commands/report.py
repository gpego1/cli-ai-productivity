import pandas as pd
from pathlib import Path

def read_csv_file(file_path: str) -> list| None:
    suffix = Path(file_path).suffix
    if suffix == '.csv':
        data = pd.read_csv(file_path)
        summary = data.describe() # make a statistic summary of the csv file data
        data_value_count = data.value_counts() # return unique values
        
        return list(summary, data_value_count)
    else:
        print('The input file its not a CSV file.')
        return None


def report(file_path: str) -> pd.DataFrame | None:
    pass