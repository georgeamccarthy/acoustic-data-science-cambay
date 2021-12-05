import glob
import sys
from pathlib import Path
import os
import logging

project_dir = Path(__file__).resolve().parents[1]

interim_data_path = os.path.join(project_dir, 'data/interim')
processed_data_path = os.path.join(project_dir, 'data/processed')
raw_csvs_path = os.path.join(project_dir, 'data/raw/reorganised_tols')
raw_feathers_path = os.path.join(project_dir, 'data/raw/raw_feathers')

log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

file_log_handler = logging.FileHandler(os.path.join(project_dir, 'acoustic_data_science/logs.log'))
stdout_log_handler = logging.StreamHandler(sys.stdout)

logging.basicConfig(level=logging.INFO, format=log_fmt, handlers=(file_log_handler, stdout_log_handler))
#logger.setLevel(level='INFO')

figure_ending = '.png'

monthly_transient_durations_path = os.path.join(project_dir, 'acoustic_data_science/analysis/monthly_transient_durations.npy')
whole_year_path = os.path.join(processed_data_path, 'whole_year/whole_year.feather')

figures_path = os.path.join(project_dir, 'figures')