import os
import pandas as pd
from config import DATA_DIR, RESULTS_DIR, aqs_epa_url, chronic_url, who_url
from load import retrieve_file_pm25, retrieve_file_chronic, retrieve_file_pm25_who
# from analyze import plot_statistics
from process import process_pm25, process_chronic, process_pm25_who

if __name__ == "__main__":
    print("---Running main for final project---\n")
    # Create a data directory
    os.makedirs(DATA_DIR, exist_ok=True)

    # --- U.S. EPA AQS API data ---
    pm25_data = retrieve_file_pm25(aqs_epa_url)
    pm25_5states_5years = process_pm25(pm25_data)
    if pm25_5states_5years is not None:
        df_pm25 = pd.DataFrame(pm25_5states_5years)
        print(f"\nU.S. PM2.5 Data Head:\n{df_pm25.head()}\n")

        # plot_statistics(df, 'PM2.5', result_dir=RESULTS_DIR)
    print("\n" + "=" * 50 + "\n")

    # --- U.S. Chronic disease data from web---
    chronic_data = retrieve_file_chronic(chronic_url)
    chronic_5state_5years = process_chronic(chronic_data)
    if chronic_5state_5years is not None:
        df_chronic = pd.DataFrame(chronic_5state_5years)
        print(f"\nU.S. Chronic Disease Data Head:\n{df_chronic.head()}")
        # plot_statistics(chronic, 'Chronic disease', result_dir=RESULTS_DIR)
    print("\n" + "=" * 50 + "\n")

    # --- Global PM2.5 data from Google drive ---
    pm25_who_data = retrieve_file_pm25_who(who_url, extract_dir=DATA_DIR)
    pm25_who_5years = process_pm25_who(pm25_who_data)
    if pm25_who_5years is not None:
        df_pm25_who = pd.DataFrame(pm25_who_5years)
        print(f"\nPM 2.5 Worldwide Data Head:\n{df_pm25_who.head()}\n")
        # plot_statistics(chronic, 'Chronic disease', result_dir=RESULTS_DIR)
    print("\n" + "=" * 50 + "\n")

    # print("\n--- Data collection and plotting complete. Check the 'results' directory. ---")