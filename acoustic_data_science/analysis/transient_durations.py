import pandas as pd
import numpy as np
import logging
import os

from acoustic_data_science import config, helpers


def get_transient_durations(df):
    # Mask df to only get loud rows.
    df["index_group"] = df.index - np.arange(df.shape[0])
    index_groups = df["index_group"].unique()

    transient_durations = []
    for index_group in index_groups:
        transient_times = df[df["index_group"] == index_group][
            "timestamp"
        ].values
        transient_durations.append(
            (transient_times[-1] - transient_times[0]).astype("float") / 1e9
            + 0.5
        )

    # Cull any detected transient with length longer than 5 mins. Arbitrary for now.
    # transient_durations[i] = transient_durations[transient_durations < 5*60]
    transient_durations = np.array(transient_durations)
    return transient_durations


def get_monthly_transit_durations():
    logging.info("Getting monthly transit durations.")
    months = helpers.get_month_names(config.processed_data_path)
    monthly_transient_durations = []

    for feather_path in helpers.get_feather_paths(config.processed_data_path):
        df = pd.read_feather(feather_path)
        df = df[df["loud"]]
        monthly_transient_durations.append(get_transient_durations(df))

    monthly_transient_durations = np.array(monthly_transient_durations)

    return monthly_transient_durations


def get_transient_timestamps_and_durations(df, average_tols=False):
    # Just get the loud events.
    df = df[df["loud"]]

    # Each transient has a number called transient_group.
    # Half-seconds in the same transient have the same transient_group.
    df.loc[:, "transient_group"] = df.index - np.arange(df.shape[0])
    # Recover the original index lost by grouping.
    # =========================================================================
    df.loc[:, "duration"] = np.full(len(df), 0.5).tolist()
    transient_groups_summed = df.groupby(['transient_group']).sum()
    durations = transient_groups_summed["duration"]

    # Starting index of transients gets lost when grouping.
    # Recover by taking cumulative sum of the durations and divide by the duration length (0.5 s) to get the number of skipped rows.
    durations_index = (durations.index + durations.cumsum(axis=0)/0.5 - np.ones(len(durations))).astype('int').values
    # =========================================================================

    transients_df = df[df.index.isin(durations_index)]
    transients_df.loc[:, "duration"] = durations.values
    transients_df.drop(columns=['transient_group'], inplace=True)

    transients_df = transients_df.reset_index(drop=True)

    if average_tols:
        transients_df.loc[:, "25":"25119"] = transients_df.loc[:, "25":"25119"]#.div(transients_df["duration"]/0.5, axis=0)
    
    return transients_df



if __name__ == "__main__":
    monthly_transient_durations = get_monthly_transit_durations()
    np.save(
        config.monthly_transient_durations_path, monthly_transient_durations
    )

    # Create monthly transient duration and timestamp files
    monthly_feather_paths = helpers.get_feather_paths(config.processed_data_path + '/monthly_data')
    month_names = helpers.get_month_names(config.processed_data_path + '/monthly_data')
    for monthly_feather_path, month_name in zip(monthly_feather_paths, month_names):
        df = pd.read_feather(monthly_feather_path).drop(columns=['unnormalised_broadband_spl', "short_transient"])
        transients_df = get_transient_timestamps_and_durations(df, average_tols=True)
        transients_df.to_feather(os.path.join(config.processed_data_path,f'transient_timestamps_and_durations/{month_name}.feather'))

    # Create year long transient durations and timestamps file 
    whole_year_df = pd.read_feather(config.processed_data_path + '/whole_year/whole_year.feather')
    whole_year_df["loud"] = whole_year_df["broadband_spl"] > whole_year_df["background_spl"] + 10
    whole_year_transients_df = get_transient_timestamps_and_durations(whole_year_df)
    whole_year_transients_df = whole_year_transients_df.drop(columns=["loud"])
    whole_year_transients_df["month"] = whole_year_transients_df['timestamp'].apply(lambda x: '{year}{month:02}'.format(year=x.year, month=x.month)).values
    whole_year_transients_df.to_feather(config.processed_data_path + '/transient_timestamps_and_durations/whole_year.feather')
    whole_year_transients_df