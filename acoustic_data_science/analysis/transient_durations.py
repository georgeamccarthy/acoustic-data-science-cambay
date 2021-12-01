import pandas as pd
import numpy as np
import logging

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
    months = helpers.get_months(config.processed_data_path)
    monthly_transient_durations = []

    for feather_path in helpers.get_feather_paths(config.processed_data_path):
        df = pd.read_feather(feather_path)
        df = df[df["loud"]]
        monthly_transient_durations.append(get_transient_durations(df))

    monthly_transient_durations = np.array(monthly_transient_durations)

    return monthly_transient_durations

if __name__ == '__main__':
    monthly_transient_durations = get_monthly_transit_durations()
    np.save(config.monthly_transient_durations_path, monthly_transient_durations)