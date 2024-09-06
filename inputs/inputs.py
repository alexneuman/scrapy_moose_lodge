
from typing import List, Dict
# import pandas as pd

import csv

def inputs_from_csv(fp):
    with open(fp, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        records = []

        for row in reader:
            cleaned_row = {key: (value if value is not None else '') for key, value in row.items()}
            records.append(cleaned_row)

    return records