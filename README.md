# Rethinking PM2.5 Exposure: Chronic Disease Trends in the U.S. (2015 – 2019) <Project title>
Chronic disease such as cardiovascular disease, respiratory disorders, and
cancers are major causes of illness and death in the United States. Studying how
these diseases vary across different states and over time can help us to understand
population health patterns and support public health planning. Moreover, due to
growing global environmental concerns about PM 2.5, there is a known relationship
between air pollution and respiratory diseases. The aim of this study is to examine
temporal and geographic trends of chronic disease in the U.S. from 2015 to 2020
and discuss them in the context of global PM2.5 patterns.

# Data sources
1. EPA:
	- Air quality system (AQS) API
	- https://aqs.epa.gov/aqsweb/documents/data_api.html
	- API
	- Field: Environment
	- Format: json
	- Data size: 14,423

2. Data.gov:
	- U.S. Chronic Disease Indicators
	- https://catalog.data.gov/dataset/u-s-chronic-disease-indicators
	- Download file from web
	- Field: Health
	- Format: json
	- Data size: 8,782

3. WHO:
	- Air pollution: concentrations of fine particular matter (PM2.5), SDG 11.6.2
	- https://www.who.int/data/gho/data/indicators/indicator-details/GHO/concentrations-of-fine-particulate-matter-%28pm2-5%29
	- Download file from Google drive
	- Field: Environment
	- Format: csv
    	- Data size: 4,725

# Results 
**from the Data Selection and Preparation part**

1. U.S. PM2.5 concentration data (EPA AQS API)
    - Select five representative states (California, Colorado, Illinois, New York, Texas) to reduce data size while maintaining geographic diversity.
    - Filter records collected from 2015 to 2019.
    - Extract only arithmetic mean PM2.5 concentrations at the county level.
2. U.S. chronic disease data
    - Select the same five states to match the environmental dataset.
    - Filter records collected from 2015 to 2019.
    - Keep only essential variables: disease name, value, value unit, state, year, and geolocation.
3. Worldwide PM2.5 concentration data
    - Filter for 2015–2019 to match the U.S. dataset.
    - Keep only indicator, country, period (year), and value.

# Installation
**for the Data Selection and Preparation part**
- Get an API key for retrieving data from the EPA by using https://aqs.epa.gov/data/api/signup?email=myemail@example.com. You will receive the key in your email.
- create .env file in /src
- Set the registered email in the first line of the .env file using this template (aqs_epa_email=myemail@example.com)
- Set the obtained key in the second line of the .env file using this template (aqs_epa_key=yourkey)

- Special python packages
    - pandas
	- requests
    - dotenv

# Running analysis
**Planned analysis**
1. Clean and preprocess the chronic disease dataset for 2015 to 2019, and extract relevant variables such as disease type, year and state.
    - Tools: pandas - for filtering, cleaning, and handling missing data
2. Aggregate data by year and state to calculate disease prevalence rates.
    - Tools: pandas groupby/aggregation
3. Retrieve state-level PM2.5 concentration data from the EPA Air quality system (AQS) API.
    - Tools: requests - for API calls, json + pandas for parsing and structuring data
4. Merge environmental data with disease dataset using state and year as key variables.
    - Tools: pandas.merge
5. Analyze descriptive statistics and create visualizations (trend lines and heatmaps) to explore spatial and temporal patterns.
    - Tools: pandas.describe, matplotlib, seaborn
6. Using correlation analysis to evaluate relationships between chronic disease rates and PM2.5 levels.
    - Tools: scipy.stats - for Pearson/Spearman correlation, or pandas.corr
7. Summarize and interpret the results
    - Tools: matplotlib / seaborn


From `src/` directory run:

`python main.py `

Results will appear in `results/` folder. All obtained will be stored in `data/`