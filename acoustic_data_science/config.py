import glob
import sys
from pathlib import Path
import os
import logging

project_dir = Path(__file__).resolve().parents[1]
sys.path.append(project_dir)

interim_data_path = os.path.join(project_dir, 'data/interim')
processed_data_path = os.path.join(project_dir, 'data/processed')
raw_csvs_path = os.path.join(project_dir, 'data/raw/reorganised_tols')
raw_feathers_path = os.path.join(project_dir, 'data/raw/raw_feathers')

log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_fmt)

def get_feather_paths(data_path):
    return sorted(glob.glob(f'{data_path}/*.feather'))

def get_months(data_path):
    months = []
    for feather_path in get_feather_paths(data_path):
            months.append(feather_path.split('/')[-1][:-len('.feather')])

    return months