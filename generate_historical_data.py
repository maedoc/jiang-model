"""
Generate placeholder historical data CSV files for calibration.
"""

import numpy as np
import pandas as pd
from historical_calibration import HistoricalCalibrator
from ode_model_extended import load_parameters


def main():
    params = load_parameters("real_params.json")

    # Generate 1973 data
    calibrator_1973 = HistoricalCalibrator(params, "1973")
    df_1973 = calibrator_1973._generate_synthetic_data()
    df_1973.to_csv("historical_1973.csv", index=False)
    print(f"Generated historical_1973.csv with {len(df_1973)} rows")

    # Generate 2008 data
    calibrator_2008 = HistoricalCalibrator(params, "2008")
    df_2008 = calibrator_2008._generate_synthetic_data()
    df_2008.to_csv("historical_2008.csv", index=False)
    print(f"Generated historical_2008.csv with {len(df_2008)} rows")

    # Print summary
    print("\nVariables included:", df_1973["variable"].unique())
    print("Regions:", df_1973["region"].unique())
    print("Time span: 0-730 days (2 years)")


if __name__ == "__main__":
    main()
