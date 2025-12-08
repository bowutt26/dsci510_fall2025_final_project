import os
from config import DATA_DIR, RESULTS_DIR, aqs_epa_url, chronic_url, global_url
from load import retrieve_file_pm25, retrieve_file_chronic, retrieve_file_pm25_global
from analyze import calculate_correlation, mixed_effects_model, plot_us_trends, plot_global_comparison, plot_disease_heatmap, plot_all_chronic_trends, plot_correlation_bar_chart, plot_correlation_scatters, plot_grouped_bar_charts, plot_mixed_effects_forest
from process import process_pm25_us, process_chronic, process_pm25_global, aggregate_us_pm25, aggregate_us_chronic, aggregate_global_pm25, merge_us_data

if __name__ == "__main__":
    print("---Running main for final project---\n")
    # Create a data directory
    os.makedirs(DATA_DIR, exist_ok=True)
    # =======================================================
    # --- RETRIEVING DATA ---

    # --- U.S. EPA AQS API data ---
    pm25_us_data = retrieve_file_pm25(aqs_epa_url)
    df_pm25_us_processed = process_pm25_us(pm25_us_data)

    # Aggregate U.S. PM2.5 and get the clean DataFrame
    if df_pm25_us_processed is not None:
        df_pm25_us_agg = aggregate_us_pm25(df_pm25_us_processed)
        print(f"\nU.S. PM2.5 Aggregated Data Head:\n{df_pm25_us_agg.head()}\n")
    print("\n" + "=" * 50 + "\n")
    # =======================================================
    # --- U.S. chronic disease data from web---
    chronic_data = retrieve_file_chronic(chronic_url)
    df_chronic_processed = process_chronic(chronic_data)

    # Aggregate chronic disease and get the clean DataFrame
    if df_chronic_processed is not None:
        df_chronic_agg = aggregate_us_chronic(df_chronic_processed)
        print(f"\nU.S. Chronic Disease Aggregated Data Head:\n{df_chronic_agg.head()}")
    print("\n" + "=" * 50 + "\n")
    # =======================================================
    # --- Global PM2.5 data from Google drive ---
    pm25_global_data = retrieve_file_pm25_global(global_url, extract_dir=DATA_DIR)
    df_pm_global_processed = process_pm25_global(pm25_global_data)

    # Aggregate global PM2.5 and get the clean DataFrame
    if df_pm_global_processed is not None:
        df_global_agg = aggregate_global_pm25(df_pm_global_processed)
        print(f"\nGlobal PM 2.5 Aggregated Data Head:\n{df_global_agg.head()}")
    print("\n" + "=" * 50 + "\n")
    # =======================================================
    # --- MERGING DATA ---

    # --- Merge the two U.S. datasets for analysis ---
    if df_pm25_us_agg is not None and df_chronic_agg is not None:
        df_merged_us = merge_us_data(df_pm25_us_agg, df_chronic_agg)
        print(f"\nMerged Avg. U.S. Data Head:\n{df_merged_us.head()}")
    print("\n" + "=" * 50 + "\n")

    print("\n--- Data aggregation and merging complete. Proceed to analysis. ---")
    # =======================================================
    # --- ANALYSIS AND VISUALIZATION ---

    # Correlation analysis
    if df_merged_us is not None:
        correlation_results = calculate_correlation(df_merged_us)

        print("\n--- Summary Correlation Results ---")
        for disease, res in correlation_results.items():
            if res['status'] == 'Success':
                print(f"  {disease}: rho={res['rho']:.4f}, p={res['p_value']:.4f}")
            else:
                print(f"  {disease}: {res['status']}")
        plot_correlation_bar_chart(correlation_results, RESULTS_DIR)
        plot_correlation_scatters(df_merged_us, correlation_results, RESULTS_DIR)

    # Mixed-Effects Models analysis
    if df_merged_us is not None:
        mixed_effects_results = mixed_effects_model(df_merged_us)
        plot_mixed_effects_forest(mixed_effects_results, RESULTS_DIR)

    # U.S. and Disease trend plots
    if df_merged_us is not None:
        plot_us_trends(df_merged_us, RESULTS_DIR)
        plot_all_chronic_trends(df_merged_us, RESULTS_DIR)
        plot_grouped_bar_charts(df_merged_us, RESULTS_DIR)
        plot_disease_heatmap(df_merged_us, RESULTS_DIR)

    # Global comparison plot
    if df_pm25_us_agg is not None and df_global_agg is not None:
        plot_global_comparison(df_pm25_us_agg, df_global_agg, RESULTS_DIR)

    print("\n" + "=" * 50 + "\n")
    print("\n--- Data collection and plotting complete. Check the 'results' directory. ---")