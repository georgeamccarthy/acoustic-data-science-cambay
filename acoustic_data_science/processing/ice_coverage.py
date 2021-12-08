import pandas as pd
from acoustic_data_science import config


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


if __name__ == "__main__":
    ice_coverage_df = process_ice_coverage_csv()
    ice_coverage_df.to_csv(
        config.processed_data_path
        + "/cambridge_bay_sea_ice_properties_from_ice_charts.csv"
    )
