import os
import pandas as pd
import json
from pathlib import Path
from config import DATA_DIR, RESULTS_DIR, aqs_epa_url, chronic_url, who_url
from load import retrieve_file_pm25, retrieve_file_chronic, retrieve_file_pm25_who
from analyze import calculate_correlation, plot_us_trends, plot_global_comparison, plot_disease_heatmap, plot_all_chronic_trends, plot_correlation_bar_chart, plot_correlation_scatters
from process import process_pm25, process_chronic, process_pm25_who, aggregate_us_pm25, aggregate_us_chronic, merge_us_data

# Filename for locally download for checking
directory_path = Path(DATA_DIR)
pm25_file = "pm25_5states_8years.json"
chronic_file = "chronic_5states_8years.json"
pm25_who_file = "pm25_who.csv"

print("Running tests for final project:\n")
print("=" * 70)

# ======================================================================================================================
# Getting U.S. PM 2.5 data and check if data file already existed in the directory, otherwise retrieve data from API
pm25_path = directory_path / pm25_file
if pm25_path.exists():
    print(f"The file '{pm25_file}' exists in '{directory_path}'.")
else:
    print(f"The file '{pm25_file}' does not exist in '{directory_path}'.")
    pm25_data = retrieve_file_pm25(aqs_epa_url)

    # Ensure the directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    # Save data to local
    with open(pm25_path, "w") as f:
        json.dump(pm25_data, f, ensure_ascii=False, indent=4)
    print(f"U.S. PM2.5 concentration data - written to {pm25_path}\n")

# Load the pm25_file into DataFrame
print(f"Loading {pm25_path} into DataFrame...")
with open(pm25_path, "r") as f:
    pm25_data = json.load(f)
print("U.S PM2.5 concentration data loaded successfully\n")

# Filtering data only the needed information: focusing on only 5 states over 5 years
pm25_5states_8years = process_pm25(pm25_data)
df_pm25_raw = pd.DataFrame(pm25_5states_8years)
print(f"\nU.S. PM2.5 Raw Processed Data Head:\n{df_pm25_raw.head()}")

# Aggregate: Group by state and year to get the final mean
df_pm25_agg = aggregate_us_pm25(pm25_5states_8years)
print(f"\nU.S. PM2.5 Aggregated Data Head (Final Form):\n{df_pm25_agg.head()}")

print("\n" + "=" * 50 + "\n")

# ======================================================================================================================
# Getting chronic disease data and check if data file already existed in the directory, otherwise retrieve data from API
chronic_path = directory_path / chronic_file
if chronic_path.exists():
    print(f"The file '{chronic_file}' exists in '{directory_path}'.")
else:
    print(f"The file '{chronic_file}' does not exist in '{directory_path}'.")
    chronic_data = retrieve_file_chronic(chronic_url)

    # Ensure the directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    # Save data to local
    with open(chronic_path, "w") as f:
        json.dump(chronic_data, f, ensure_ascii=False, indent=4)
    print(f"U.S. Chronic disease data - written to {chronic_path}\n")

# Load the chronic_file into DataFrame
print(f"Loading {chronic_path} into DataFrame...")
with open(chronic_path, "r") as f:
    chronic_data = json.load(f)
print("U.S. Chronic disease data loaded successfully\n")

# # Find all column names and their values
# columns_meta = chronic_data["meta"]["view"]["columns"]
# chronic_columns = [column['name'] for column in columns_meta]
# print(chronic_columns)
# df_chronic_columns = pd.DataFrame(columns=chronic_columns)

# Filtering data only the needed information: focusing on only 5 states over 5 years
chronic_5state_8years = process_chronic(chronic_data)
df_chronic_raw = pd.DataFrame(chronic_5state_8years)
print(f"\nU.S. Chronic Disease Raw Processed Data Head (Rates):\n{df_chronic_raw.head()}\n")

# Aggregate: Group by state, year, and disease to get the final rate
df_chronic_agg = aggregate_us_chronic(chronic_5state_8years)
print(f"\nChronic Disease Aggregated Data Head (State/Year/Disease):\n{df_chronic_agg.head()}")

print("\n" + "=" * 50 + "\n")

# ======================================================================================================================
# Data merging
if df_pm25_agg is not None and df_chronic_agg is not None:
    print("Testing Merging Function...")

    df_merged_test = merge_us_data(df_pm25_agg, df_chronic_agg)

    print(f"\nMerged U.S. Data Head (Multiple rows per State/Year):\n{df_merged_test.head()}")
    print(f"\nTotal merged rows: {len(df_merged_test)}")

    # Test for the correct final columns
    expected_cols = {'year', 'state', 'avg_pm25', 'disease', 'unit', 'avg_prevalence_rate'}
    if expected_cols.issubset(set(df_merged_test.columns)):
        print("SUCCESS: Final merged dataframe contains all expected columns.")
    else:
        print("FAIL: Merged dataframe missed some required columns.")

print("\n" + "=" * 50 + "\n")

# ======================================================================================================================
# Getting PM2.5 data from WHO
pm25_who_path = directory_path / pm25_who_file
if pm25_who_path.exists():
    print(f"The file '{pm25_who_file}' exists in '{directory_path}'.")
else:
    print(f"The file '{pm25_who_file}' does not exist in '{directory_path}'.")
    pm25_who_data = retrieve_file_pm25_who(who_url, extract_dir=DATA_DIR)

pm25_who_5years = process_pm25_who(pm25_who_data)
df_pm25_who = pd.DataFrame(pm25_who_5years)
print(f"\nGlobal PM2.5 Data Head:\n{df_pm25_who.head()}\n")
# df_pm25_who.info()

# Group by year and calculate the global mean PM2.5
df_global_mean = df_pm25_who.groupby("year")["value"].mean().reset_index()
df_global_mean = df_global_mean.rename(columns={"value": "GlobalPM25_Mean"})

print(f"Global PM2.5 Mean by Year:\n{df_global_mean}\n")

print("\n" + "=" * 50 + "\n")

# ======================================================================================================================
# Analysis section

if 'df_merged_test' in locals() and df_merged_test is not None:
    print("Testing Analysis and Visualization Functions...\n")

    # Test correlation analysis
    print(f"\n--- Testing correlation analysis ---")
    unique_diseases = df_merged_test["disease"].unique()
    print(f"Unique diseases available for correlation:\n{unique_diseases}\n")

    correlation_results = calculate_correlation(df_merged_test)
    if correlation_results is not None:
        print(f"SUCCESS: Correlation results generated for {len(correlation_results)} diseases.")
    else:
        print("FAIL: Correlation results could not be generated.\n")

    plot_correlation_bar_chart(correlation_results, RESULTS_DIR)
    plot_correlation_scatters(df_merged_test, correlation_results, RESULTS_DIR)

    # Test U.S. trend plots
    print(f"\n--- Testing U.S. trend plot ---")
    try:
        plot_us_trends(df_merged_test, RESULTS_DIR)
        print(f"SUCCESS: Trend plots generated successfully and saved to {RESULTS_DIR}.")
    except Exception as e:
        print(f"FAIL: Trend plots could not be generated. Error: {e}")

    # Test all chronic disease trend plots
    print(f"\n--- Testing all chronic disease trend plot ---")
    try:
        plot_all_chronic_trends(df_merged_test, RESULTS_DIR)
        print(f"SUCCESS: Trend plots generated successfully and saved to {RESULTS_DIR}.")
    except Exception as e:
        print(f"FAIL: Trend plots could not be generated. Error: {e}")

    # Test global comparison plots
    print(f"\n--- Testing global comparison trend plot ---")
    try:
        plot_global_comparison(df_merged_test, df_pm25_who, RESULTS_DIR)
        print(f"SUCCESS: Trend plots generated successfully and saved to {RESULTS_DIR}.")
    except Exception as e:
        print(f"FAIL: Trend plots could not be generated. Error: {e}")

    # Test heatmap plot
    print(f"\n--- Testing disease heatmap plot ---")
    try:
        plot_disease_heatmap(df_merged_test, RESULTS_DIR)
        print(f"SUCCESS: Heatmap plot generated successfully and saved to {RESULTS_DIR}.")
    except Exception as e:
        print(f"FAIL: Heatmap plot could not be generated. Error: {e}")

else:
    print("Skipping analysis test - Merged data was not created successfully.")

print("\n" + "=" * 50 + "\n")