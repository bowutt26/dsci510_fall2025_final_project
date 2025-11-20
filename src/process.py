import pandas as pd

# Process PM2.5 concentration data and categorized into 5 states for 5 years
def process_pm25(pm25_data):
    bdate = [20150101, 20160101, 20170101, 20180101, 20190101]
    states = ["06", "08", "17", "36", "48"]
    state_names = {"06": "California", "08": "Colorado", "17": "Illinois", "36": "New York", "48": "Texas"}
    pm25_5states_5years = {}

    print(f"Processing U.S. PM2.5 data...")

    pm25_data = {int(key): value for key, value in pm25_data.items()} # Converts keys back to int
    for index_year, year in enumerate(bdate):
        annual_means_5states = {}
        data_len = 0
        for index_state, state in enumerate(states):
            pm25_year = pm25_data[bdate[index_year]]
            pm25_state = pm25_year[state_names[states[index_state]]]
            results = pm25_state["Data"]
            annual_means = [result["arithmetic_mean"] for result in results]  # Select only the arithmetic mean value from each county
            annual_means_5states[state_names[states[index_state]]] = annual_means
            data_len += len(annual_means)
        pm25_5states_5years[bdate[index_year]] = annual_means_5states  # Collecting data over 5 years
        print(f"    Data length: Year {bdate[index_year]} - PM2.5 concentration = {data_len}")
    print("U.S. PM2.5 concentration data processed successfully\n")
    return pm25_5states_5years

# Process chronic disease data and categorized into 5 states for 5 years
def process_chronic(chronic_data):
    valid_units = {"%", "cases per 1,000", "cases per 100,000", "cases per 1,000,000", "per 100,000"}
    targeted_states = {"California", "Colorado", "Illinois", "New York", "Texas"}
    chronic_5state_5years = []

    print("Processing U.S. chronic disease data...")

    # Define indices based on the data structure
    YEAR_INDEX = 8
    LOCATION_INDEX = 11
    TOPIC_INDEX = 13
    UNIT_INDEX = 16
    VALUE_INDEX = 18

    data_rows = chronic_data.get("data", [])[1:]
    for row in data_rows:
        # Ensure the row is long enough to prevent IndexError
        if len(row) < VALUE_INDEX + 1:
            continue

        # Check raw value for None before attempting any conversion
        raw_value = row[VALUE_INDEX]
        if raw_value is None:
            continue

        # Attempt to extract and clean all necessary fields
        try:
            year = int(row[YEAR_INDEX])
            unit = str(row[UNIT_INDEX]).strip()
            state = str(row[LOCATION_INDEX]).strip()
            disease = str(row[TOPIC_INDEX]).strip()
            value = float(raw_value)  # Convert to float to ensure it's not None

        except (IndexError, ValueError):
            # Catches errors if the index is incorrect
            # or if a value cannot be converted
            continue

        # Check if the record uses a valid standardized unit
        if unit not in valid_units:
            continue

        # Filter by year range (2015 - 2019)
        if not (2015 <= year <= 2019):
            continue

        # Filter by targeted states
        if state not in targeted_states:
            continue

        # Append Cleaned Record ---
        chronic_5state_5years.append({
            "year": year,
            "state": state,
            "disease": disease,
            "unit": unit,
            "value": value
        })
    print(f"    Cleaned data length: U.S. chronic disease (5 states, 5 years) = {len(chronic_5state_5years)}")
    print("Chronic disease data processed successfully.\n")
    return chronic_5state_5years

# Process PM2.5 concentration worldwide data and categorized for 5 years
def process_pm25_who(pm25_who_data):
    """
    Process global PM2.5 dataset:
    - Keep only 'Concentrations of fine particulate matter (PM2.5)' indicators
    - Filter years 2015–2019
    - Keep only 3 columns: country, year, value
    """
    print("Processing Global PM2.5 data...")

    # Filter Indicator
    pm25_who_data = pm25_who_data[pm25_who_data["Indicator"] == "Concentrations of fine particulate matter (PM2.5)"]

    # Filter years 2015–2019
    pm25_who_5years = pm25_who_data[(pm25_who_data["Period"] >= 2015) & (pm25_who_data["Period"] <= 2019)]

    # Keep only 3 columns and rename
    pm25_who_5years = pm25_who_5years[["Location", "Period", "FactValueNumeric"]].copy()
    pm25_who_5years = pm25_who_5years.rename(
        columns={"Location": "country", "Period": "year", "FactValueNumeric": "value"}
    )

    # Ensure numeric types
    pm25_who_5years["year"] = pd.to_numeric(pm25_who_5years["year"], errors="coerce")
    pm25_who_5years["value"] = pd.to_numeric(pm25_who_5years["value"], errors="coerce")
    pm25_who_5years = pm25_who_5years.dropna(subset=["year", "value"])

    print(f"    Data length: Global PM2.5 (5 years) = {len(pm25_who_5years)}")
    print("Global PM2.5 data processed successfully\n")
    return pm25_who_5years

def aggregate_us_pm25(pm25_dict):
    # Aggregates the county-level PM2.5 means (from process_pm25 output) to a single State-Year average.
    aggregated_data = []

    # pm25_dict keys are date strings (e.g., 20150101) after conversion in process_pm25
    for date_key, state_data in pm25_dict.items():
        # Convert the date_key (e.g., 20150101) to a simple year integer (e.g., 2015)
        year = int(str(date_key)[:4])

        # state_data keys are state names, values are lists of county means
        for state, county_means in state_data.items():
            if county_means:
                # Calculate the mean of all county means within that state and year
                state_avg_pm25 = pd.Series(county_means, dtype=float).mean()
                aggregated_data.append({
                    "year": year,
                    "state": state,
                    "avg_pm25": state_avg_pm25
                })

    df_pm25_agg = pd.DataFrame(aggregated_data)
    print(f"U.S. PM2.5 aggregated to {len(df_pm25_agg)} State-Year rows.")
    return df_pm25_agg

def aggregate_us_chronic(chronic_list):
    # Aggregates the cleaned chronic disease records (from process_chronic output) to a single State-Year average value.
    df_chronic = pd.DataFrame(chronic_list)

    # Calculate the mean 'value' for each combination of 'state' and 'year'
    df_chronic_agg = df_chronic.groupby(["state", "year", "disease", "unit"])["value"].mean().reset_index()

    # Rename the aggregated column for clarity
    df_chronic_agg = df_chronic_agg.rename(
        columns={"value": "avg_prevalence_rate"}
    )

    # Drop records where the disease or unit is NaN after grouping (shouldn't happen with clean data)
    df_chronic_agg = df_chronic_agg.dropna(subset=['disease'])

    print(f"U.S. Chronic Disease aggregated to {len(df_chronic_agg)} State-Year-Disease rate rows.")
    return df_chronic_agg

def merge_us_data(df_pm25_agg, df_chronic_agg):
    # Merges the aggregated U.S. PM2.5 and chronic disease data on 'state' and 'year'
    df_merged = pd.merge(
        df_pm25_agg,
        df_chronic_agg,
        on=["state", "year"],
        how="inner"  # Use inner to only keep state-year pairs present in both datasets
    )
    print(f"U.S. Data Merged. Resulting DataFrame has {len(df_merged)} rows (multiple per state-year).")
    return df_merged