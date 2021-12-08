import pandas as pd
import os
from acoustic_data_science import config, helpers

feather_paths = helpers.get_feather_paths(config.processed_data_path + '/monthly_data')

df_generator = (
    pd.read_feather(
        feather_path, columns=["timestamp", "broadband_spl", "background_spl"]
    )
    for feather_path in feather_paths
)
pd.concat(df_generator, ignore_index=True).to_feather(
    path=os.path.join(
        config.processed_data_path, "whole_year", "whole_year.feather"
    )
)
