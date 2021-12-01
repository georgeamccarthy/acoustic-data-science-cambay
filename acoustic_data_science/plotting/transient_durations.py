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



def report_transient_stats(transient_durations):
    with open(durations_stats_txt_path, "a") as f:
        print(3)
        print(f"min (s) {transient_durations.min()}", file=f)
        print(f"max (s) {transient_durations.max() / 60}", file=f)
        print(f"max (mins) {transient_durations.max()/ 60:.2f}", file=f)
        print(f"sd {transient_durations.std()}", file=f)

        print(
            "Number of transients with durations > 0.5"
            f" {len(transient_durations[transient_durations > 0.5])}",
            file=f
        )
        print(
            "Number of transients with durations = 0.5"
            f" {len(transient_durations[transient_durations == 0.5])}",
            file=f
        )
        print('', file=f)


def report_monthly_transient_stats(monthly_transient_durations):
    logging.info("Reporting monthly transient stats.")
    months = helpers.get_months(config.processed_data_path)
    
    with open(durations_stats_txt_path, "w") as f:
        print("Transit Duration Stats", file=f)
        print(1)

    with open(durations_stats_txt_path, "a") as f:
        for transient_durations, month in zip(monthly_transient_durations, months):
            print(f"=== {helpers.get_month_name_from_path(month)} ===", file=f)
            print(2)
            report_transient_stats(transient_durations)


def get_longest_duration(monthly_transient_durations):
    longest_duration = np.max(
        np.concatenate(monthly_transient_durations)
    )  # seconds
    return longest_duration


def get_max_bin_size(
    monthly_transient_durations, bins, min_duration=None, max_duration=None
):
    max_bin_size = 0

    months = helpers.get_months(config.processed_data_path)

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

    months = helpers.get_months(config.processed_data_path)

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


if __name__ == "__main__":
    monthly_transient_durations = get_monthly_transit_durations()

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

    report_monthly_transient_stats(monthly_transient_durations)
