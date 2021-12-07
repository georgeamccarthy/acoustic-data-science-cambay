# -*- coding: utf-8 -*-
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import pandas as pd
import numpy as np
import datetime
import os
import glob

from acoustic_data_science import config, helpers


def combine_csvs(month):
    """
    Takes path to month folder which should contain all CSVs to be combined as
    top level files e.g. ../data/raw/reorganised_tols/
    Returns dataframe with CSVs contatenated and filenames column.
    """

    # List of csv files in month directory.
    files = glob.iglob(os.path.join(month, "*.csv"))
    # DataFrame generator for each CSV. Name of file saved in filename column.
    df_from_each_file = (
        pd.read_csv(f).assign(filename=os.path.basename(f).split("/")[-1])
        for f in files
    )
    # Concatenate each DataFrame.
    # Time ordering of rows preserved within each DF but DFs are in wrong order at this point.
    # Save in interim path as YYYY_MM.feather.
    return pd.concat(df_from_each_file, ignore_index=True)
    # .to_feather(os.path.join(config.interim_data_path,month.split('/')[-1]+'.feather'))


def get_timestamp(csv_name):
    """Takes CSV file name and returns datetime object.
    Example file name:
    ICLISTENHF1266_20180930T235802.000Z_TOL_1sHannWindow_50PercentOverlap.csv
    """
    try:
        time_str = csv_name[15:34]

        datetime_object = datetime.datetime(
            year=int(time_str[:4]),
            month=int(time_str[4:6]),
            day=int(time_str[6:8]),
            hour=int(time_str[9:11]),
            minute=int(time_str[11:13]),
            second=int(time_str[13:15]),
            microsecond=int(time_str[16:19]) * 1000,
        )
    except:
        datetime_object = np.nan

    return datetime_object


def get_timestamps(df):
    first_rows = np.unique(df["filename"].values, return_index=1)[1]
    first_rows.sort()
    first_rows
    last_rows = np.concatenate((first_rows[1:], [df.index[-1]])) - 1
    last_rows

    df["timestamp"] = df["filename"].apply(get_timestamp)

    time_windows = []
    file_lengths = last_rows - first_rows + 1
    file_lengths[-1] += 1
    for file_length in file_lengths:
        time_windows.append(
            np.arange(file_length) * datetime.timedelta(seconds=0.5)
        )

    # Flatten list.
    time_deltas = np.array(
        [val for sublist in time_windows for val in sublist]
    )

    df["timestamp"] = df["timestamp"] + time_deltas
    return df


def remove_nans(df):
    """
    Removes any rows containing nan values and two rows either side of each of
    these rows.
    """
    m = df.isna().any(axis=1)
    return df[
        ~(
            m
            | m.shift(fill_value=False)
            | m.shift(-1, fill_value=False)
            | m.shift(-2, fill_value=False)
        )
    ]


def inf_to_nans(df):
    return df.replace([np.inf, -np.inf], np.nan)


def broadband_func(x):
    return 10 ** (x / 10)


def calc_broadband_spl(df, noramlise=False):
    """
    Calculates unnormalised broadband SPL by averaging over TOLs.
    """

    unnormalised_broadband_spl = 10 * np.log10(
        df.loc[:, "25":"25119"].applymap(broadband_func).sum(axis=1)
    )

    if noramlise == False:
        logging.info(
            "Calculating unnormalised broadband SPL (normalise later)."
        )
        # Broadband SPL will be normalised later compared to other months.
        df["unnormalised_broadband_spl"] = unnormalised_broadband_spl

    else:
        logging.info("Calculating normalised broadband SPL.")
        df["broadband_spl"] = (
            unnormalised_broadband_spl - unnormalised_broadband_spl.max()
        )

    return df


def calc_background_spl(df, background_window_mins=10):
    """
    Calculate 'background' sound level using moving average of normalised
    background SPL.
    """

    # Background window is in half second intervals.
    background_window = background_window_mins * 60 * 2
    df["background_spl"] = (
        df["broadband_spl"].rolling(background_window_mins).mean()
    )

    # Start of data (duration of window) will be null so drop it.
    df = df.drop(df[pd.isnull(df["background_spl"])].index).reset_index(
        drop=True
    )

    return df


def tag_loud_events(df):
    logging.info(
        "Tagging loud events (where broadband SPL is 10 dB above"
        " background SPL)."
    )

    df["loud"] = df["broadband_spl"] > (df["background_spl"] + 10)

    return df


def tag_short_transients(df):
    """
    Tags loud events lasting less than 0.5 s as short transients.
    """

    logging.info("Tagging short transients.")

    df["trans_shft_down"] = np.concatenate((np.array([True]), df["loud"][:-1]))
    df["trans_shft_up"] = np.concatenate((df["loud"][1:], np.array([True])))
    df["short_transient"] = (
        df["loud"]
        & (df["trans_shft_down"] == False)
        & (df["trans_shft_up"] == False)
    )
    df.drop(columns=["trans_shft_down", "trans_shft_up"], inplace=True)

    return df


def tol_headers_to_ints(df):
    """
    Renames the TOL headers as integers so they are easier to type.
    """
    float_tol_columns = df.loc[
        :, "25.1188643150958":"25118.8643150958"
    ].columns
    int_tol_columns = np.round(
        df.loc[:, "25.1188643150958":"25118.8643150958"].columns.astype(
            "float"
        )
    ).astype("int")

    float_to_int_tol_dict = {}
    for old, new in zip(float_tol_columns, int_tol_columns):
        float_to_int_tol_dict[old] = str(new)

    df = df.rename(
        columns=float_to_int_tol_dict,
    )
    return df


def select_exactly_one_month(df, month_name):
    month_number = int(month_name.split("_")[1])
    df = df[df["timestamp"].dt.month == month_number].reset_index(drop=True)

    return df


def process_df(df):
    logging.info("Dropping PAMGuide false time column.")
    df = df.drop(columns=["1213"]).reset_index(drop=True)

    logging.info("Timestamping.")
    df = get_timestamps(df)

    logging.info("Cleaning data.")
    # Remove nan spl.
    pre_clean_length = len(df)
    df = remove_nans(inf_to_nans(df))
    logging.info(
        f"{len(df)/pre_clean_length*100:.2f}% of rows retained after clean."
    )

    logging.info("Sorting data by timestamps.")
    df.sort_values("timestamp", inplace=True, ignore_index=True)

    for column in df.columns:
        if df[column].dtype == "float64":
            df[column] = pd.to_numeric(df[column], downcast="float")

    # Remove nan times.
    pre_clean_length = len(df)
    df = df.drop(df[pd.isnull(df["timestamp"])].index).reset_index(drop=True)
    logging.info(
        f"{len(df)/pre_clean_length*100:.2f}% of cleaned data retained after"
        " removing unrecognised filenames."
    )

    logging.info("Renaming the TOL headers as integers.")
    df = tol_headers_to_ints(df)

    df = calc_broadband_spl(df, noramlise=False)

    return df


def process_monthly_data():
    month_paths = helpers.get_month_paths(config.raw_csvs_path)
    month_names = [
        helpers.month_name_from_month_path(month_path)
        for month_path in month_paths
    ]

    overall_max_broadband_spl = 0
    for month_name in month_names:
        logging.info(f"=== Processing {month_name} ===")
        raw_feather_path = helpers.feather_path_from_month_name(
            config.raw_feathers_path, month_name
        )
        df = pd.read_feather(raw_feather_path)
        df = process_df(df)
        df = select_exactly_one_month(df, month_name)

        max_broadband_spl = df["unnormalised_broadband_spl"].max()
        logging.info(
            f"Max unnormalised broadband SPL in {month_name} is"
            f" {max_broadband_spl:.2f}"
        )
        if max_broadband_spl > overall_max_broadband_spl:
            overall_max_broadband_spl = max_broadband_spl

        interim_feather_path = helpers.feather_path_from_month_name(
            config.interim_data_path, month_name
        )
        logging.info(f"Saving interim data to {interim_feather_path}.")
        df.to_feather(interim_feather_path)

    for month_name in month_names:
        interim_feather_path = helpers.feather_path_from_month_name(
            config.interim_data_path, month_name
        )
        df = pd.read_feather(interim_feather_path)

        logging.info(
            "Normalising broadband SPL over all months. Max SPL:"
            f" {overall_max_broadband_spl:.2f}."
        )
        df["broadband_spl"] = (
            df["unnormalised_broadband_spl"] - overall_max_broadband_spl
        )

        df = calc_background_spl(df)
        df = tag_loud_events(df)
        df = tag_short_transients(df)

        processed_feather_path = helpers.feather_path_from_month_name(
            config.processed_data_path, 
            month_name
        )

        df.to_feather(processed_feather_path)


if __name__ == "__main__":

    logging.info("Making final dataset from raw feather files.")
    process_monthly_data()
