import pandas as pd
import datetime
import numpy as np
import os
import matplotlib.pyplot as plt
import logging

from acoustic_data_science import config, helpers

durations_stats_txt_path = os.path.join(
    config.project_dir,
    "figures/transient_durations",
    "durations_stats.txt",
)


def report_transient_stats(transient_durations, f):
    print(f"min (s) {transient_durations.min()}", file=f)
    print(f"max (s) {transient_durations.max() / 60}", file=f)
    print(f"max (mins) {transient_durations.max()/ 60:.2f}", file=f)
    print(f"sd {transient_durations.std()}", file=f)

    print(
        "Number of transients with durations > 0.5"
        f" {len(transient_durations[transient_durations > 0.5])}",
        file=f,
    )
    print(
        "Number of transients with durations = 0.5"
        f" {len(transient_durations[transient_durations == 0.5])}",
        file=f,
    )
    print("", file=f)


def report_monthly_transient_stats(monthly_transient_durations):
    logging.info("Reporting monthly transient stats.")
    month_names = helpers.get_month_names(config.processed_data_path)

    with open(durations_stats_txt_path, "w") as f:
        print("Transit Duration Stats\n", file=f)

        for transient_durations, month_name in zip(
            monthly_transient_durations, month_names
        ):
            print(f"=== {month_name} ===", file=f)
            report_transient_stats(transient_durations, f)


def get_longest_duration(monthly_transient_durations):
    longest_duration = np.max(
        np.concatenate(monthly_transient_durations)
    )  # seconds
    return longest_duration


def get_max_bin_size(
    monthly_transient_durations, bins, min_duration=None, max_duration=None
):
    max_bin_size = 0

    months = helpers.get_month_names(config.processed_data_path)

    for transient_durations, month in zip(monthly_transient_durations, months):
        if min_duration is not None:
            transient_durations = transient_durations[
                transient_durations >= min_duration
            ]

        if max_duration is not None:
            transient_durations = transient_durations[
                transient_durations <= max_duration
            ]

        bin_size = max(np.histogram(transient_durations, bins=bins)[0])
        if bin_size > max_bin_size:
            max_bin_size = bin_size

    return max_bin_size


def plot_duration_histograms(
    monthly_transient_durations,
    bins,
    min_duration=None,
    max_duration=None,
    title="",
    xunits="seconds",
):
    logging.info("Plotting histogram of monthly transit durations.")
    fig = plt.figure(figsize=(15, 15))
    fig.suptitle(f"{title} {bins} bins.")

    months = helpers.get_month_names(config.processed_data_path)

    i = 0
    for transient_durations, month in zip(monthly_transient_durations, months):
        i += 1

        if min_duration is not None:
            transient_durations = transient_durations[
                transient_durations >= min_duration
            ]

        if max_duration is not None:
            transient_durations = transient_durations[
                transient_durations <= max_duration
            ]

        if xunits == "minutes":
            transient_durations = transient_durations / 60

        ax = fig.add_subplot(4, 3, i)
        ax.set_title(month)
        ax.hist(transient_durations, bins=bins)
        ax.set_ylim(
            0,
            get_max_bin_size(
                monthly_transient_durations,
                bins=bins,
                min_duration=min_duration,
                max_duration=max_duration,
            ),
        )

        ax.set_ylabel("Count")
        ax.set_xlabel(f"Duration ({xunits})")

    plt.tight_layout()
    fig_file_name = helpers.snake_case(title)
    plt.savefig(
        os.path.join(
            config.project_dir,
            "figures/transient_durations",
            fig_file_name + config.figure_ending,
        )
    )

def plot_monthly_transient_durations_by_length(whole_year_transients_df):
    short_transients_df = whole_year_transients_df[whole_year_transients_df["duration"] <= 0.5].groupby("month").size()
    med_short_transients_df = whole_year_transients_df[(0.5 < whole_year_transients_df["duration"]) & (whole_year_transients_df["duration"] <= 5)].groupby("month").size()
    med_transients_df = whole_year_transients_df[(5 < whole_year_transients_df["duration"]) & (whole_year_transients_df["duration"] <= 3*60)].groupby("month").size()
    long_transients_df = whole_year_transients_df[(3*60 < whole_year_transients_df["duration"]) & (whole_year_transients_df["duration"] <= 20*60)].groupby("month").size()

    plt.figure(figsize=(16,8))

    x = short_transients_df.index
    y = short_transients_df.values
    plt.bar(x, y, label=r"$0 \less \rm{duration} \leq 0.5$ sec")

    x = med_short_transients_df.index
    y = med_short_transients_df.values
    plt.bar(x, y, label=r"$0.5 \less \rm{duration} \leq 5$ sec")

    x = med_transients_df.index
    y = med_transients_df.values
    plt.bar(x, y, label=r"$5 \less \rm{duration} \leq 3 \rm{min}$")

    x = long_transients_df.index
    y = long_transients_df.values
    plt.bar(x, y, label=r"$3 \rm{min} \less \rm{duration} \leq 20 \rm{min}$")

    plt.legend()

    plt.savefig(
        os.path.join(
            config.figures_path,
            "transient_durations/monthly_transient_durations_by_length" + config.figure_ending,
        )
    )


def plot_monthly_long_transient_durations_and_ice_concentration(whole_year_transients_df):
    short_transients_df = whole_year_transients_df[whole_year_transients_df["duration"] <= 0.5].groupby("month").size()
    med_short_transients_df = whole_year_transients_df[(0.5 < whole_year_transients_df["duration"]) & (whole_year_transients_df["duration"] <= 5)].groupby("month").size()
    med_transients_df = whole_year_transients_df[(5 < whole_year_transients_df["duration"]) & (whole_year_transients_df["duration"] <= 3*60)].groupby("month").size()
    long_transients_df = whole_year_transients_df[(3*60 < whole_year_transients_df["duration"]) & (whole_year_transients_df["duration"] <= 20*60)].groupby("month").size()

    fig, ax = plt.subplots(1,1,figsize=(16,8))

    ax.bar(whole_year_transients_df["month"].unique(), 0)

    x = long_transients_df.index
    y = long_transients_df.values
    ax.bar(x, y, label=r"$3 \rm{min} \less \rm{duration} \leq 20 \rm{min}$")
    ax.set_ylabel("Number of long transients per month")

    ax2 = ax.twinx()
    ax.set_ylabel("Number of long transients per month")
    monthly_ice_concentration = pd.read_csv(config.processed_data_path + "/monthly_ice_concentration.csv")
    x = monthly_ice_concentration["month"].astype("str")
    y = monthly_ice_concentration["total_concentration"]
    ax2.set_ylabel("Ice concentration (/10)")
    ax2.scatter(x, y, label="Ice concentration")
    ax2.plot(x, y)

    ax.legend(loc="upper left")
    ax2.legend(loc="upper right")
    plt.savefig(
        os.path.join(
            config.figures_path,
            "transient_durations/monthly_long_transient_durations_and_ice_concentration" + config.figure_ending,
        )
    )


def plot_monthly_long_transient_durations_and_temperature(whole_year_transients_df):
    short_transients_df = whole_year_transients_df[whole_year_transients_df["duration"] <= 0.5].groupby("month").size()
    med_short_transients_df = whole_year_transients_df[(0.5 < whole_year_transients_df["duration"]) & (whole_year_transients_df["duration"] <= 5)].groupby("month").size()
    med_transients_df = whole_year_transients_df[(5 < whole_year_transients_df["duration"]) & (whole_year_transients_df["duration"] <= 3*60)].groupby("month").size()
    long_transients_df = whole_year_transients_df[(3*60 < whole_year_transients_df["duration"]) & (whole_year_transients_df["duration"] <= 20*60)].groupby("month").size()

    fig, ax = plt.subplots(1,1,figsize=(16,8))
    ax.set_ylabel("Number of long transients per month")

    x = short_transients_df.index
    y = short_transients_df.values
    ax.bar(x, y, label=r"$0 \less \rm{duration} \leq 0.5$ sec")

    x = med_short_transients_df.index
    y = med_short_transients_df.values
    ax.bar(x, y, label=r"$0.5 \less \rm{duration} \leq 5$ sec")

    x = med_transients_df.index
    y = med_transients_df.values
    ax.bar(x, y, label=r"$5 \less \rm{duration} \leq 3 \rm{min}$")

    x = long_transients_df.index
    y = long_transients_df.values
    ax.bar(x, y, label=r"$3 \rm{min} \less \rm{duration} \leq 20 \rm{min}$")

    ax2 = ax.twinx()
    monthly_ice_concentration = pd.read_csv(config.processed_data_path + "/monthly_ice_concentration.csv")
    x = monthly_ice_concentration["month"].astype("str")
    y = monthly_ice_concentration["mean_temperature"]
    ax2.set_ylabel("Temperature (deg C)")
    ax2.scatter(x, y, label="Temperature (deg C)", color="black")
    ax2.plot(x, y, color="black")

    ax.legend(loc="upper left")
    ax2.legend(loc="upper right")

    plt.legend()
    plt.savefig(
        os.path.join(
            config.figures_path,
            "transient_durations/monthly_long_transient_durations_and_temperature" + config.figure_ending,
        )
    )


if __name__ == "__main__":
    monthly_transient_durations = helpers.load_monthly_transient_durations()

    plot_duration_histograms(
        monthly_transient_durations,
        bins=20,
        title="All transients.",
        xunits="minutes",
    )
    plot_duration_histograms(
        monthly_transient_durations,
        bins=20,
        min_duration=3 * 60,
        title="Only transients longer than 3 minutes.",
        xunits="minutes",
    )
    plot_duration_histograms(
        monthly_transient_durations,
        bins=20,
        max_duration=3 * 60,
        title="Only transients shorter than 3 minutes.",
    )
    plot_duration_histograms(
        monthly_transient_durations,
        bins=15,
        max_duration=15,
        title="Only transients shorter than 15 seconds.",
    )

    whole_year_transients_df = pd.read_feather(config.processed_data_path + '/transient_timestamps_and_durations/whole_year.feather')
    plot_monthly_transient_durations_by_length(whole_year_transients_df)
    plot_monthly_long_transient_durations_and_ice_concentration(whole_year_transients_df)
    plot_monthly_long_transient_durations_and_temperature(whole_year_transients_df)

    report_monthly_transient_stats(monthly_transient_durations)
