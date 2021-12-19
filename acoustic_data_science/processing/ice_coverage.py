import pandas as pd
from acoustic_data_science import config
import numpy as np


def process_ice_coverage_csv():
    df = pd.read_csv(
        config.external_data_path
        + "/cambridge_bay_sea_ice_properties_from_ice_charts.csv",
        usecols=[
            "Date",
            "Total Concentration",
            "Stage of Development",
            "Form of Ice",
            "Mean Temperature",
        ],
    )
    df = df.rename(
        columns={
            "Total Concentration": "total_concentration",
            "Stage of Development": "stage_of_development",
            "Form of Ice": "form_of_ice",
            "Mean Temperature": "mean_temperature",
        }
    )

    df = df.replace("<1", 0.5)
    df.loc[:, "total_concentration":"mean_temperature"] = df.loc[
        :, "total_concentration":"mean_temperature"
    ].astype("float")

    df["timestamp"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")
    df = df.sort_values("timestamp", ignore_index=True)

    bad_rows = df[14:23]["stage_of_development"]
    df[14:23]["stage_of_development"] = bad_rows.replace(1, 11)

    return df

def get_monthly_ice_concentration():
    ice_concentration = pd.read_csv(config.processed_data_path + '/cambridge_bay_sea_ice_properties_from_ice_charts.csv')[["timestamp", "total_concentration", "mean_temperature"]]
    ice_concentration = ice_concentration.replace(np.nan, 0)

    ice_concentration["timestamp"] = ice_concentration["timestamp"].apply(pd.to_datetime)
    ice_concentration["month"] = ice_concentration['timestamp'].apply(lambda x: '{year}{month:02}'.format(year=x.year, month=x.month)).values
    #ice_concentration_monthly = ice_concentration.groupby("month").mean()
    #ice_concentration_monthly = ice_concentration_monthly.sort_values(["month"])

    #ice_concentration_monthly[201808 <= ice_concentration_monthly["month"]]
    ice_concentration_monthly = ice_concentration.drop(columns=["timestamp"]).groupby("month", as_index=False).mean()
    ice_concentration_monthly["total_concentration"] = ice_concentration_monthly["total_concentration"].round()
    #ice_concentration_monthly[201808 < int(ice_concentration_monthly["month"])]

    new_row = {'month':'201808', 'total_concentration':0}
    ice_concentration_monthly = ice_concentration_monthly.append(new_row, ignore_index=True)
    ice_concentration_monthly = ice_concentration_monthly.sort_values(["month"]).reset_index(drop=True)

    ice_concentration_monthly = ice_concentration_monthly[ice_concentration_monthly["month"].astype("int") <= 201905]
    ice_concentration_monthly["month"] = ice_concentration_monthly["month"].astype("str")
    return ice_concentration_monthly

if __name__ == "__main__":
    ice_coverage_df = process_ice_coverage_csv()
    ice_coverage_df.to_csv(
        config.processed_data_path
        + "/cambridge_bay_sea_ice_properties_from_ice_charts.csv"
    )
    monthly_ice_concentration_df = get_monthly_ice_concentration()
    monthly_ice_concentration_df.to_csv(config.processed_data_path + '/monthly_ice_concentration.csv', index=False)
