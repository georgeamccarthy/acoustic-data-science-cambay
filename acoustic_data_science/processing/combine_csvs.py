import glob
import pandas as pd
import os
import acoustic_data_science.config as config
import logging


def combine_csvs(month):
    """
    Takes path to month folder which should contain all CSVs to be combined as
    top level files e.g. ../data/raw/reorganised_tols/
    Returns dataframe with CSVs contatenated and filenames column.
    """
    logging.info("Getting list of csv files in month directory.")
    files = glob.iglob(os.path.join(month, "*.csv"))
    logging.info(
        "Making DataFrame generator for each CSV. Name of file saved in"
        " filename column."
    )
    df_from_each_file = (
        pd.read_csv(f).assign(filename=os.path.basename(f).split("/")[-1])
        for f in files
    )
    # Time ordering of rows preserved within each DF but DFs are in wrong order at this point.
    # Save in interim path as YYYY_MM.feather.
    logging.info("Concatenate each DataFrame.")
    return pd.concat(df_from_each_file, ignore_index=True)
    # .to_feather(os.path.join(config.interim_data_path,month.split('/')[-1]+'.feather'))


def combine_monthly_csvs():
    """
    Combines monthly CSVs and saves them as feather files.
    """
    logging.info("Combining CSVs to feather file.")

    month_paths = []
    for month in os.listdir(config.raw_csvs_path):
        logging.info(f"=== Processing {month.split('/')[-1]} ===")
        csv_folder_path = f"{config.raw_csvs_path}/{month}"
        if os.path.isdir(csv_folder_path):
            month_paths.append(csv_folder_path)

    for month in month_paths:
        combine_csvs(month).to_feather(
            os.path.join(
                config.raw_feathers_path, month.split("/")[-1] + ".feather"
            )
        )


if __name__ == "__main__":
    combine_monthly_csvs()
