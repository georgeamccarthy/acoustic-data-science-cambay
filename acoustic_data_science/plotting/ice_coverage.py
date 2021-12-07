# This cell is from the template notebook. It contains ipython magic and 
# various useful imports which are commonly used in this app.

%load_ext autoreload
%autoreload 2

import pandas as pd
import datetime
import numpy as np
import os
from acoustic_data_science import config, helpers
import matplotlib.pyplot as plt
import logging

colours = ["blue", "orange", "green", "red"]


def plot_ice_coverage_property(df, ice_property):
    plt.figure(figsize=(16,8))
    mask = df[ice_property].notnull()
    x = df['timestamp'][mask]
    y = df[ice_property][mask]
    plt.ylabel(ice_property)
    plt.xlabel("Date (YYYY-MM)")
    plt.plot(x, y)
    plt.scatter(x, y)
    plt.show()


def plot_multiple_ice_coverage_properties_as_one_plot(df, ice_properties):
    plt.figure(figsize=(16,10))
    for i, ice_property in enumerate(ice_properties):
        mask = df[ice_property].notnull()
        x = df['timestamp'][mask]
        y = df[ice_property][mask]
        # Min-max normalization
        # https://stackoverflow.com/questions/26414913/normalize-columns-of-pandas-data-frame
        if ice_property == "mean_temperature":
            y_norm = (y-y.min())/(y.max()-y.min())*10
            ice_property = f"normalized_mean_temperature ({y.min():.0f} - {y.max():.0f})->(0 - 10)"
        else:
            y_norm = y
        plt.plot(x, y_norm, c=colours[i])
        plt.scatter(x, y_norm, label=ice_property, c=colours[i])

    plt.xlabel("Date (YYYY-MM)")
    plt.ylabel("Noramalized quantity (0-1)")
    plt.legend(loc="lower left")
    figure_path = helpers.get_figure_path('multiple_ice_coverage_properties_as_one_plot', 'ice_coverage')
    plt.savefig(figure_path)
    plt.show()


def plot_multiple_ice_coverage_properties_as_grid(df, ice_properties):
    fig = plt.figure(figsize=(20,15))
    for i, ice_property in enumerate(ice_properties):
        mask = df[ice_property].notnull()
        x = df['timestamp'][mask]
        y = df[ice_property][mask]
        # Min-max normalization
        # https://stackoverflow.com/questions/26414913/normalize-columns-of-pandas-data-frame
        ax = fig.add_subplot(2,2,i+1)
        ax.plot(x, y, c=colours[i])
        ax.scatter(x, y, label=ice_property, c=colours[i])
        ax.set_title(ice_property)

        if ice_property == "mean_temperature":
            plt.ylabel("Mean temperature (degrees C)")
        else:
            plt.ylim(0,11.5)
            plt.ylabel(ice_property)

        plt.xlabel("Date (YYYY-MM)")
        
    plt.legend(loc="upper left")
    plt.tight_layout()
    figure_path = helpers.get_figure_path('multiple_ice_coverage_properties_as_grid', 'ice_coverage')
    plt.savefig(figure_path)
    plt.sho

if __name__ == '__main__':
    ice_properties = ["total_concentration", "stage_of_development", "form_of_ice", "mean_temperature"]

    df = pd.read_csv(config.processed_data_path + '/cambridge_bay_sea_ice_properties_from_ice_charts.csv')

    plot_multiple_ice_coverage_properties_as_one_plot(df, ice_properties)
    plot_multiple_ice_coverage_properties_as_grid(df, ice_properties)