import pandas as pd
import numpy as np

def process_pm25_us(pm25_us_data):
    """
    Processes U.S. PM2.5 data:
    - extracting and storing the list of monitor-level arithmetic means for each state/year combination.
    """
    # Define the inputs
    bdate_codes = [20150101, 20160101, 20170101, 20180101, 20190101, 20200101, 20210101, 20220101]
    state_names = {"06": "California", "08": "Colorado", "17": "Illinois", "36": "New York", "48": "Texas"}
    pm25_all_data = []

    print(f"Processing U.S. PM2.5 data...")

    pm25_data = {int(key): value for key, value in pm25_us_data.items()} # Converts keys back to int

    for year_code in bdate_codes:
        current_year = year_code // 10000
        total_data_len = 0

        pm25_year_data = pm25_data.get(year_code, {})

        for state_code, state_name in state_names.items():
            pm25_state_data = pm25_year_data.get(state_name, {})
            results = pm25_state_data.get("Data", [])

            # Extract list of means from all monitors in the state/year
            monitor_means_list = [result["arithmetic_mean"] for result in results if "arithmetic_mean" in result]

            # Store the data for this State/Year combination
            pm25_all_data.append({
                "year": current_year,
                "state": state_name,
                "monitor_means_list": monitor_means_list,  # Storing the list of raw means
                "data_point_count": len(monitor_means_list)  # Storing the size for verification
            })
            total_data_len += len(monitor_means_list)

        print(f"    Total data points extracted: Year {current_year} = {total_data_len}")

    # Convert the list of dicts to a pandas DataFrame for easy merging
    df_pm25_us_processed = pd.DataFrame(pm25_all_data)

    print("U.S. PM2.5 concentration data processed successfully\n")
    return df_pm25_us_processed

def process_chronic(chronic_data):
    """
    Processes U.S. chronic disease data:
    - Cleaning, filtering, and transforming raw chronic disease data for analysis.
    - Filters to Age-adjusted Prevalence for 5 target states and expands multi-year ranges.
    """
    from config import TARGET_DATA_TYPE, TARGET_STRATIFICATION, TARGET_STATES, TARGET_YEAR_MIN, TARGET_YEAR_MAX

    print("Processing U.S. chronic disease data...")

    column_definitions = chronic_data["meta"]["view"]["columns"]
    column_names = [col["fieldName"] for col in column_definitions]

    # Extract the data rows, skipping the first (index 0) internal metadata row
    data_rows = chronic_data["data"][1:]
    df_chronic = pd.DataFrame(data_rows, columns=column_names)

    target_cols = [
        'locationdesc',  # State
        'topic',  # Disease
        'datavaluetype',  # Age-adjusted Prevalence
        'datavalue',  # Value
        'yearstart',
        'yearend',
        'datavalueunit',  # %
        'stratification1' # Overall
    ]

    df_cleaned = df_chronic[target_cols].copy()
    df_cleaned.rename(columns={
        'locationdesc': 'state',
        'topic': 'disease',
        'datavalue': 'value',
        'yearstart': 'year_start',
        'yearend': 'year_end',
        'datavaluetype': 'data_type',
        'datavalueunit': 'unit',
        'stratification1': 'stratification'
    }, inplace=True)

    # Convert 'value' to numeric immediately (handles missing/invalid strings)
    df_cleaned["value"] = pd.to_numeric(df_cleaned["value"], errors="coerce")

    # Convert year columns to numeric for filtering
    df_cleaned['year_start'] = pd.to_numeric(df_cleaned['year_start'], errors='coerce')
    df_cleaned['year_end'] = pd.to_numeric(df_cleaned['year_end'], errors='coerce')

    # Initial filtering (before explode)
    df_cleaned = df_cleaned[
        (df_cleaned['data_type'] == TARGET_DATA_TYPE) &
        (df_cleaned['unit'] == "%") &
        (df_cleaned['stratification'] == TARGET_STRATIFICATION) &
        (df_cleaned['state'].isin(TARGET_STATES)) &
        (df_cleaned['value'].notna())  # Filter missing values
        ]
    print(f"Filter ==> Pre-Explode Cleaned Rows: {len(df_cleaned)}")

    # Expand multi-year ranges
    df_cleaned['year'] = df_cleaned.apply(lambda row: list(range(int(row['year_start']), int(row['year_end']) + 1)), axis=1)
    df_cleaned = df_cleaned.explode('year')
    df_cleaned['year'] = df_cleaned['year'].astype(int)

    # Final year filter
    df_cleaned = df_cleaned[(df_cleaned['year'] >= TARGET_YEAR_MIN) & (df_cleaned['year'] <= TARGET_YEAR_MAX)]
    print(f"Filter ==> Final Rows After Explode and Year Filter: {len(df_cleaned)}")

    print("Chronic disease data processed successfully.\n")
    return df_cleaned

# Process PM2.5 concentration worldwide data and categorized for 5 years
def process_pm25_global(pm25_global_data):
    """
    Process global PM2.5 data:
    - Cleans and filters raw global PM2.5 data (WHO source).
    - Filter 'Concentrations of fine particulate matter (PM2.5)' indicators and years 2015–2019
    """
    from config import TARGET_INDICATOR

    print("Processing Global PM2.5 data...")

    df_pm_global_processed = pm25_global_data.copy()

    # Ensure 'Period' and 'FactValueNumeric' columns are numeric types
    df_pm_global_processed["Period"] = pd.to_numeric(df_pm_global_processed["Period"], errors="coerce")
    df_pm_global_processed["FactValueNumeric"] = pd.to_numeric(df_pm_global_processed["FactValueNumeric"], errors="coerce")

    # Filter Indicator
    df_pm_global_processed = df_pm_global_processed[df_pm_global_processed["Indicator"] == TARGET_INDICATOR]

    # Filter years 2015–2019
    df_pm_global_processed = df_pm_global_processed[(df_pm_global_processed["Period"] >= 2015) & (df_pm_global_processed["Period"] <= 2019)]

    # Keep only 3 columns and rename
    df_pm_global_processed = df_pm_global_processed[["Location", "Period", "FactValueNumeric"]].copy()
    df_pm_global_processed = df_pm_global_processed.rename(
        columns={"Location": "country", "Period": "year", "FactValueNumeric": "value"}
    )

    # Drop rows where year or value failed conversion/filtering
    df_pm_global_processed = df_pm_global_processed.dropna(subset=["year", "value"])

    print(f"    Data length: Global PM2.5 (5 years) = {len(df_pm_global_processed)}")
    print("Global PM2.5 data processed successfully\n")
    return df_pm_global_processed

def aggregate_us_pm25(df_pm25_us_processed):
    """
    Aggregates the monitor-level PM2.5 means (from process_pm25_raw_means output)
    to a single State-Year average.
    """
    print(f"\nAggregating {len(df_pm25_us_processed)} State-Year raw mean lists...")

    # Calculate the mean of the list of monitor means for each State-Year row.
    df_pm25_us_agg = df_pm25_us_processed.copy()

    # Use .apply(np.mean) to calculate the average of the list stored in each cell
    df_pm25_us_agg['avg_pm25'] = df_pm25_us_agg['monitor_means_list'].apply(lambda x: np.mean(x) if x else np.nan)

    # Drop the list column now that the mean is calculated
    df_pm25_us_agg = df_pm25_us_agg.drop(columns=['monitor_means_list', 'data_point_count'])

    # Clean up the output to only include rows where aggregation was successful
    df_pm25_us_agg = df_pm25_us_agg.dropna(subset=['avg_pm25']).reset_index(drop=True)

    print(f"Aggregated U.S. PM2.5 size: {df_pm25_us_agg.shape}")
    print(f"U.S. PM2.5 data aggregation successful.\n")
    return df_pm25_us_agg

def aggregate_us_chronic(df_chronic_processed):
    """
    Aggregates chronic disease data after cleaning.
    Group by: state, year, disease
    Compute: average prevalence, number of observations
    """
    print("Aggregating chronic disease data...")

    df_chronic_agg = (
        df_chronic_processed.groupby(["state", "year", "disease", "unit"], as_index=False)
        .agg(avg_prevalence=("value", "mean"),
             n_obs=("value", "count"))
    )

    print(f"Aggregated chronic size: {df_chronic_agg.shape}")
    print("Chronic disease data aggregation successful.\n")
    return df_chronic_agg

def aggregate_global_pm25(df_pm25_processed):
    """
    Aggregates the clean, country-level PM2.5 data to calculate the
    Worldwide Arithmetic Mean PM2.5 concentration for each year.
    """
    print("Aggregating Global PM2.5 data to Worldwide Average...")

    df_global_agg = (
        df_pm25_processed.groupby("year")["value"]
        .mean()
        .reset_index()
        .rename(columns={"value": "Global_PM25"})
    )

    print(f"Aggregated chronic size: {df_global_agg.shape}")
    print("Global PM2.5 aggregation successful.\n")
    return df_global_agg

def merge_us_data(df_pm25_us_agg, df_chronic_agg):
    """
    Merge annual PM2.5 averages with aggregated chronic disease data.
    Uses 'outer' merge to preserve the full time range of the PM2.5 data
    (needed for plotting global comparison).
    Key: (state, year)
    """
    print("Merging PM2.5 and chronic data...")

    df_merged_us = df_chronic_agg.merge(
        df_pm25_us_agg,
        on=["state", "year"],
        how="outer" # using outer merge to keep the full time range (2015-2022)
    )

    print(f"Merged dataset size: {df_merged_us.shape}")
    return df_merged_us

def merge_us_data_individual(df_pm25_us_agg, df_chronic_processed):
    """
    Merge annual PM2.5 averages with the individual, processed
    chronic disease observations (before final disease-level aggregation) for scatter plots.
    Key: (state, year)
    """
    # Change the generic 'value' column to a descriptive name
    df_chronic_processed.rename(columns={"value": "prevalence_rate"}, inplace=True)
    print("Merging PM2.5 and individual chronic prevalence values from processed chronic data...")

    df_merged_us_individual = df_chronic_processed.merge(
        df_pm25_us_agg,
        on=["state", "year"],
        how="inner" # using inner merge to ensure every resulting row has a corresponding
    )

    # Drop any row where the primary plot variables are NaN.
    df_merged_us_individual = df_merged_us_individual.dropna(subset=['prevalence_rate', 'avg_pm25'])

    print(f"Merged dataset size: {df_merged_us_individual.shape}")
    return df_merged_us_individual