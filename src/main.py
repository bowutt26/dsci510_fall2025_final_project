import os
import pandas as pd
from config import DATA_DIR, RESULTS_DIR, aqs_epa_url, chronic_url, who_url
from load import retrieve_file_pm25, retrieve_file_chronic, retrieve_file_pm25_who
from analyze import calculate_correlation, plot_us_trends, plot_global_comparison, plot_disease_heatmap, plot_all_chronic_trends, plot_correlation_bar_chart, plot_correlation_scatters
from process import process_pm25, process_chronic, process_pm25_who, aggregate_us_pm25, aggregate_us_chronic, merge_us_data

if __name__ == "__main__":
    print("---Running main for final project---\n")
    # Create a data directory
    os.makedirs(DATA_DIR, exist_ok=True)
    # =======================================================
    # --- RETRIEVING DATA ---

    # --- U.S. EPA AQS API data ---
    pm25_data = retrieve_file_pm25(aqs_epa_url)
    pm25_5states_8years = process_pm25(pm25_data)

    # Aggregate PM2.5 and get the clean DataFrame
    if pm25_5states_8years is not None:
        df_pm25_agg = aggregate_us_pm25(pm25_5states_8years)
        print(f"\nU.S. PM2.5 Aggregated Data Head:\n{df_pm25_agg.head()}\n")
    print("\n" + "=" * 50 + "\n")
    # =======================================================
    # --- U.S. chronic disease data from web---
    chronic_data = retrieve_file_chronic(chronic_url)
    chronic_5state_8years = process_chronic(chronic_data)

    # Aggregate chronic disease and get the clean DataFrame
    if chronic_5state_8years is not None:
        df_chronic_agg = aggregate_us_chronic(chronic_5state_8years)
        print(f"\nU.S. Chronic Disease Aggregated Data Head:\n{df_chronic_agg.head()}")
    print("\n" + "=" * 50 + "\n")

    # --- Merge the two U.S. datasets for analysis ---
    if 'df_pm25_agg' in locals() and 'df_chronic_agg' in locals():
        df_merged_us = merge_us_data(df_pm25_agg, df_chronic_agg)
        print(f"\nMerged U.S. Data Head:\n{df_merged_us.head()}")
    print("\n" + "=" * 50 + "\n")
    # =======================================================
    # --- Global PM2.5 data from Google drive ---
    pm25_who_data = retrieve_file_pm25_who(who_url, extract_dir=DATA_DIR)
    pm25_who_5years = process_pm25_who(pm25_who_data)
    if pm25_who_5years is not None:
        df_pm25_who = pd.DataFrame(pm25_who_5years)
        print(f"\nGlobal PM 2.5 Data Head:\n{df_pm25_who.head()}\n")
    print("\n" + "=" * 50 + "\n")

    print("\n--- Data aggregation and merging complete. Proceed to analysis. ---")
    # =======================================================
    # --- ANALYSIS AND VISUALIZATION ---

    # Correlation analysis
    if 'df_merged_us' in locals():
        correlation_results = calculate_correlation(df_merged_us)

        print("\n--- Summary Correlation Results ---")
        for disease, res in correlation_results.items():
            if res['status'] == 'Success':
                print(f"  {disease}: rho={res['rho']:.4f}, p={res['p_value']:.4f}")
            else:
                print(f"  {disease}: {res['status']}")
        plot_correlation_bar_chart(correlation_results, RESULTS_DIR)
        plot_correlation_scatters(df_merged_us, correlation_results, RESULTS_DIR)

    # U.S. trend plots
    if 'df_merged_us' in locals():
        plot_us_trends(df_merged_us, RESULTS_DIR)

    # All chronic diseases trend plots
    if 'df_merged_us' in locals():
        plot_all_chronic_trends(df_merged_us, RESULTS_DIR)

    # Global comparison plot
    if 'df_merged_us' in locals() and 'df_pm25_who' in locals():
        plot_global_comparison(df_merged_us, df_pm25_who, RESULTS_DIR)

    # Chronic disease heatmap
    if 'df_merged_us' in locals():
        plot_disease_heatmap(df_merged_us, RESULTS_DIR)

    # if 'df_merged_us' in locals():
    #     descriptive_stats(df_merged_us)

    print("\n--- Data collection and plotting complete. Check the 'results' directory. ---")