from re import sub
import glob
import logging

from acoustic_data_science import config


def snake_case(s):
    """
    Converts a given string s to snake case e.g. 'Snake Case!' becomes
    'snake_case'.
    """
    return '_'.join(
        sub('([A-Z][a-z]+)', r' \1',
        sub('([A-Z]+)', r' \1',
        s.replace('-', ' '))).split()).lower()


def get_month_name_from_path(feather_path):
    return feather_path.split('/')[-1]


def get_feather_paths(data_path):
    return sorted(glob.glob(f'{data_path}/*.feather'))


def get_months(data_path):
    logging.info(f"Getting month paths in {'/'.join(data_path.split('/')[:-1])}.")
    months = []
    for feather_path in get_feather_paths(data_path):
            months.append(feather_path.split('/')[-1][:-len('.feather')])

    return months

