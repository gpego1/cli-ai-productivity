import pandas as pd
from pathlib import Path

def read_csv_file(file_path: str) -> str:
    suffix = Path(file_path).suffix()
    if suffix == 'csv':
        data = pd.read_csv(file_path)
        print(data.describe())
        print(data.value_counts())
    else:
        print('The input file its not a CSV file.')

def report():
    read_csv_file('../products.csv')