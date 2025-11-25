# Rethinking PM2.5 Exposure: Chronic Disease Trends in the U.S. (2015 – 2022) <Project title>
Chronic disease such as cardiovascular disease, respiratory disorders, and
cancers are major causes of illness and death in the United States. Studying how
these diseases vary across different states and over time can help us to understand
population health patterns and support public health planning. Moreover, due to
growing global environmental concerns about PM 2.5, there is a known relationship
between air pollution and respiratory diseases. 

This project aims to analyze U.S. chronic disease prevalence alongside national PM2.5 trends 
and to compare U.S. air quality patterns with global PM2.5 levels. Together, these trends 
help contextualize how air pollution may relate to population health in the United States.

# Data sources
1. EPA:
	- Air quality system (AQS) API
	- https://aqs.epa.gov/aqsweb/documents/data_api.html
	- API
    - Data period: 2015-2022
	- Format: json
	- Data size: 25,270 (after processed: 40 rows x 3 columns)

2. CDC: 
	- U.S. Chronic Disease Indicators
	- https://catalog.data.gov/dataset/u-s-chronic-disease-indicators
	- Download file from web
    - Data period: 2019-2022 (only age-adjusted prevalence values retained)
	- Format: json
	- Data size: 309,215 (after processed: 281 rows x 5 columns)

3. WHO:
	- Air pollution: concentrations of fine particular matter (PM2.5), SDG 11.6.2
	- https://www.who.int/data/gho/data/indicators/indicator-details/GHO/concentrations-of-fine-particulate-matter-%28pm2-5%29
	- Download file from Google drive
    - Data period: 2015-2019
	- Format: csv
    - Data size: 4,725

# Results
I. Statistical Findings
- Significant Negative Link: Only Asthma (ρ=−0.51) and the Immunization control metric (ρ=−0.48) show a statistically significant relationship with PM2.5.
- Biological Hypothesis Rejected: We found no significant correlation for COPD or Diabetes (P>0.05).
II. Ecological Factors
- The negative correlation means that cleaner states have higher Asthma rates. This is driven by Ecological Confounding. 
- The identical pattern in Immunization confirms a powerful third factor—likely Socioeconomic Status or strong public health policy—that influences both air quality and disease rates. 
- For Asthma, factors like population migration (Avoidance Eﬀect) and local policy are stronger determinants than direct environmental exposure in this dataset.

# Installation
**for the Data Selection and Preparation part**
- Get an API key for retrieving data from the EPA by using https://aqs.epa.gov/data/api/signup?email=myemail@example.com. You will receive the key in your email.
- create .env file in /src
- Set the registered email in the first line of the .env file using this template (aqs_epa_email=myemail@example.com)
- Set the obtained key in the second line of the .env file using this template (aqs_epa_key=yourkey)

- Special python packages
    - scipy
    - matplotlib
    - numpy
    - pandas
	- requests
    - python-dotenv

# Running analysis
1. Data preprocessing 
   **Only five states are included as the study sample: California, Colorado, Illinois, New York, Texas.**
   **Tools: requests - for API calls, json + pandas for parsing and structuring data**
   **Tools: pandas - for filtering, cleaning, and handling missing data**
    - U.S. PM2.5
      - Extract annual state-level PM2.5 data from the EPA API.
      - Filter for the 5 target states.
      - Compute the mean PM2.5 per state per year.
    - U.S. Chronic Disease
      - Filter rows where:
        - DataValueType = "Age-adjusted Prevalence"
        - StratificationCategory1 = "Overall"
        - Topic in the list of 17 diseases.
    - Global PM2.5 
      - Keep only three columns: country, year, value.
2. Data aggregation
   **Tools: pandas groupby/merge**
   - U.S. PM2.5 aggregated (2015–2022): one mean PM2.5 value per state per year.
   - Chronic disease prevalence (2019–2022): one prevalence value per disease, per state, per year.
   - Merged dataset: PM2.5 and disease data merged on (state, year).
3. Trend analysis
   **Tools: pandas, matplotlib, seaborn**
   - U.S. PM2.5 trend (2015–2022): For 5 states individually.
   - U.S. vs Global PM2.5 trend (2015–2019): Uses overlapping years.
   - Chronic disease trend plots (2019–2022): For all 17 diseases, with support for generating individual plots.
   - Heatmap of disease prevalence (2019–2022): Visualizes state- and year-level patterns.
4. Correlation analysis (Spearman correlation)
   **Tools: scipy.stats - for Spearman correlation**
   - Reasons for choosing:
     - Data across 5 states × 4 years is small.
     - Many disease distributions are non-linear or non-normal. 
     - Robust to monotonic but non-linear relationships.
   - For each of the 17 diseases:
     - Compute ρ (rho) and p-value.
     - Store results in structured dictionary.
     - Generate a correlation summary bar chart.
     - Generate scatter plots for selected diseases.
5. Visualization outputs
   **Tools: matplotlib / seaborn**
   - All figures are saved automatically in the ../results/ directory.
6. Summarize and interpret the results


From `src/` directory run:

`python main.py `

Results will appear in `results/` folder. All obtained will be stored in `data/`