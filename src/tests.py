import os
import pandas as pd
import json
from pathlib import Path
from config import DATA_DIR, RESULTS_DIR, aqs_epa_url, chronic_url, who_url
from load import retrieve_file_pm25, retrieve_file_chronic, retrieve_file_pm25_who
from process import process_pm25, process_chronic, process_pm25_who

# Filename for locally download for checking
directory_path = Path(DATA_DIR)
pm25_file = "pm25_5states_5years.json"
chronic_file = "chronic_5states_5years.json"
pm25_who_file = "pm25_who.csv"

print("Running tests for final project:\n")

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
pm25_5states_5years = process_pm25(pm25_data)
if pm25_5states_5years is not None:
    df_pm25 = pd.DataFrame(pm25_5states_5years)
    print(f"\nU.S. PM2.5 Data Head:\n{df_pm25.head()}\n")
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

# Filtering data only the needed information: focusing on only 5 states over 5 years
chronic_5state_5years = process_chronic(chronic_data)
if chronic_5state_5years is not None:
    df_chronic = pd.DataFrame(chronic_5state_5years)
    print(f"\nU.S. Chronic Disease Data Head:\n{df_chronic.head()}")
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
if pm25_who_5years is not None:
    df_pm25_who = pd.DataFrame(pm25_who_5years)
    print(f"\nWorldwide PM 2.5 Data Head:\n{df_pm25_who.head()}\n")
print("\n" + "=" * 50 + "\n")