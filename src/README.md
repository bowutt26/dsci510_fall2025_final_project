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
	- Download file from web
	- Field: Environment
	- Format: csv

# Results 
_describe your findings_

# Installation
- Get an API key for retrieving data from the EPA by using https://aqs.epa.gov/data/api/signup?email=myemail@example.com. You will receive the key in your email.
- Set the registered email in the first line of the .env file using this template (aqs_epa_email=myemail@example.com)
- Set the obtained key in the second line of the .env file using this template (aqs_epa_key=yourkey)

- Special python packages
	- pathlib
	- load
	- requests
	- json

# Running analysis 
_update these instructions_


From `src/` directory run:

`python main.py `

Results will appear in `results/` folder. All obtained will be stored in `data/`