from re import sub
import glob
import logging
import numpy as np
import os

from acoustic_data_science import config


def snake_case(s):
    """
    Converts a given string s to snake case e.g. 'Snake Case!' becomes
    'snake_case'.
    """
    return '_'.join(
        sub('([A-Z][a-z]+)', r' \1',
        sub('([A-Z]+)', r' \1',
        s.replace('-', ' '))).split()).lower().strip(".")


def month_name_from_month_path(month_path):
    return month_path.split('/')[-1]


def feather_path_from_month_name(data_path, month_name):
    return os.path.join(data_path, month_name + '.feather')


def get_feather_paths(data_path):
    return sorted(glob.glob(f'{data_path}/*.feather'))


def load_monthly_transient_durations():
    return list(np.load(config.monthly_transient_durations_path, allow_pickle=True))


def get_tols_df(df):
    return df.loc[:, "25":"25119"]


def get_month_paths(data_path):
    month_paths = []
    for month_name in os.listdir(data_path):
        month_path = os.path.join(data_path, month_name.split('.')[0])
        if month_name[:2] == '20':
            month_paths.append(month_path)
    
    month_paths.sort()

    return month_paths


def get_month_names(data_path):
    month_paths = get_month_paths(data_path)
    month_names = [month_name_from_month_path(month_path) for month_path in month_paths]

    return month_names


def get_figure_path(figure_name, folder=''):

        if folder == '':
            folder = figure_name

        figure_path = os.path.join(
            config.figures_path,
            folder,
            figure_name + config.figure_ending,
        )

        return figure_path