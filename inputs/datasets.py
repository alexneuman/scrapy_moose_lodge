
import csv
import os
import logging
from itertools import islice
# try:
#     import pandas as pd
# except:
#     logging.info('Pandas is not installed. Datasets will not be available for use')

path = os.path.dirname(__file__) + '/dataset_files'

def lat_lng_dataset():
    """
        Returns a tuple of dictionaries of lat/lngs of all zip codes in the US
        keys: ZIP,LAT,LNG
    """
    file = os.path.join(path, 'lat_lngs_us.csv')
    with open(file) as f:
        reader = csv.DictReader(f)
        return tuple(reader)
    
def zips_dataset(state_filter=None, step=None):
    """
    Returns a tuple of dictionaries of 
    keys: state_fips, state, abbr, zip, county, city
    """
    if isinstance(state_filter, str):
        filter_row_name = 'state'
        if state_filter:
            filter_row_name = 'state'
        state_filter = [state_filter]
    
    file = os.path.join(path, 'zips_us.csv')
    records = []

    with open(file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            row['zip'] = row['zip'].zfill(5)
            if state_filter:
                state_filter = [state.lower() for state in state_filter]
                if row[filter_row_name].lower() in state_filter:
                    records.append(row)
            else:
                records.append(row)
    
    if step:
        records = list(islice(records, 0, len(records), step))
    
    return tuple(records)
    
def us_cities_dataset():
    """
        Returns a tuple of dictionaries of the top 1000 US cities
        keys: city, state, population, lat, lon
    """
    
    file = os.path.join(path, 'us_cities.csv')
    records = []
    with open(file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    return records    