import os
import requests
import re
import ssl
import pandas as pd
import json
import csv

def retrieve_file_pm25(aqs_epa_url):
    aqs_epa_email = os.getenv("aqs_epa_email")
    aqs_epa_key = os.getenv("aqs_epa_key")
    bdate = [20150101, 20160101, 20170101, 20180101, 20190101]
    edate = [20151231, 20161231, 20171231, 20181231, 20191231]
    states = ["06", "08", "17", "36", "48"]
    state_names = {"06": "California", "08": "Colorado", "17": "Illinois", "36": "New York", "48": "Texas"}
    pm25_conc_5years = {}

    print(f"Loading data from {aqs_epa_url}...")

    # API limits data retrieval to a maximum of one year per request
    for index_year, year in enumerate(bdate):
        pm25_conc_data = {}
        for index_state, state in enumerate(states):
            # Retrieve data by using API
            params = {
                "email": aqs_epa_email,
                "key": aqs_epa_key,
                # from metadata
                #       parameters class - "code": "PM2.5 MASS/QA", "value_represented": "PM2.5 Mass and QA Parameters"
                #       parameter in class - "code": "88101", "value_represented": "PM2.5 - Local Conditions"
                "param": 88101,
                "bdate": bdate[index_year],
                "edate": edate[index_year],
                "state": states[index_state]
            }
            r = requests.get(aqs_epa_url, params=params)
            pm25_concentration = r.json()

            if "Data" not in pm25_concentration:
                print(f"Warning: No data for {state_names[state]} in {year}")
                continue

            pm25_conc_data[state_names[states[index_state]]] = pm25_concentration
        pm25_conc_5years[bdate[index_year]] = pm25_conc_data
    print("U.S. PM2.5 concentration data loaded successfully\n")
    return pm25_conc_5years

def retrieve_file_chronic(chronic_url):
    print(f"Loading data from {chronic_url}...")

    # Retrieve data via Web
    r = requests.get(chronic_url)
    chronic_data = r.json()
    print("U.S. Chronic disease data loaded successfully\n")
    return chronic_data

def retrieve_file_pm25_who(who_url, extract_dir):
    try:
        # Ensure extraction directory exists
        os.makedirs(extract_dir, exist_ok=True)
        print(f"Loading data from {who_url}...")

        # Retrieve data via Google drive
        ssl._create_default_https_context = ssl._create_unverified_context  # Disable SSL verification

        file_id = re.split("/", who_url)[5]
        gg_url = f"https://drive.google.com/uc?export=download&id={file_id}"

        # Download the file
        r = requests.get(gg_url)
        if r.status_code != 200:
            raise Exception(f"Failed to download file from Google Drive: {r.status_code}")

        # Save file locally to /data folder
        pm25_who_path = os.path.join(extract_dir, "who_pm25.csv")
        with open(pm25_who_path, "wb") as f:
            f.write(r.content)
        print(f"Global PM2.5 concentration data saved to {pm25_who_path}")

        # Load the extracted CSV into a DataFrame
        if os.path.exists(pm25_who_path):
            print(f"Loading {pm25_who_path} into DataFrame...")
            pm25_who_data = pd.read_csv(pm25_who_path)
            print("Global PM2.5 concentration data loaded successfully\n")
        return pm25_who_data

    except Exception as e:
        print(f"Error loading data from Google drive: {e}")
        return None

