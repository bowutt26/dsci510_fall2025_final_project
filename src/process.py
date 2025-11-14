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
        print(f"    Data length: Year {bdate[index_year]} - PM 2.5 concentration = {data_len}")
    print("U.S. PM2.5 concentration data processed successfully")
    return pm25_5states_5years

# Process chronic disease data and categorized into 5 states for 5 years
def process_chronic(chronic_data):
    targeted_state = {"California", "Colorado", "Illinois", "New York", "Texas"}
    chronic_5years = []

    print(f"Processing U.S. chronic disease data...")

    results = chronic_data["data"]
    for result in results:
        if result[8] >= "2015" and result[9] <= "2019":  # Select only data from 2015 to 2019
            data = {
                "year_start": result[8],
                "year_end": result[9],
                "state": result[11],
                "disease": result[13],
                "unit": result[16],
                "value": result[18],
                "geolocation": result[30],
            }
            chronic_5years.append(data)
        else:
            continue
    print(f"    Data length: U.S. chronic disease (5 years) = {len(chronic_5years)}")

    # Filter only 5 states
    chronic_by_state_5years = [result for result in chronic_5years if result["state"] in targeted_state]
    print(f"    Data length: U.S. chronic disease (5 states, 5 years) = {len(chronic_by_state_5years)}")
    print("U.S. Chronic disease data processed successfully")
    return chronic_by_state_5years

# Process PM2.5 concentration worldwide data and categorized for 5 years
def process_pm25_who(pm25_who_data):
    targeted_header = ["Indicator", "Location", "Period", "FactValueNumeric"]

    print(f"Processing PM 2.5 worldwide data...")

    pm25_who_data = pm25_who_data[[col for col in targeted_header if col in pm25_who_data.columns]]
    pm25_who_5years = pm25_who_data[(pm25_who_data["Period"] >= 2015) & (pm25_who_data["Period"] <= 2019)]
    print(f"    Data length: PM 2.5 worldwide (5 years) = {len(pm25_who_5years)}")
    print("PM 2.5 worldwide data processed successfully")
    return pm25_who_5years