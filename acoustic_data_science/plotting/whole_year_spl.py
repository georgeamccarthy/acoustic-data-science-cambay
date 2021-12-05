import matplotlib.pyplot as plt
import pandas as pd
import os
from acoustic_data_science import config, helpers
import logging

def plot_avg_spl(averaging_window = 2 * 60 * 60 * 24 * 2):
    logging.info("Plotting broadband SPL over the year.")

    df = pd.read_feather(path=config.whole_year_path)

    rolling_mean = df['broadband_spl'].rolling(averaging_window).mean()
    rolling_mean_not_null = rolling_mean.notnull()
    rolling_mean = rolling_mean[rolling_mean_not_null]

    plt.figure(figsize=(16,12))

    step = 1000

    t = df['timestamp'][rolling_mean_not_null]
    y = rolling_mean
    plt.plot(t[::step], y[::step], 'b-', label='Broadband SPL')

    plt.legend()
    plt.savefig(helpers.get_figure_path('whole_year_spl'))

if __name__ == '__main__':
    plot_avg_spl()