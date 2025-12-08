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
	- Data size: 309,214 (after processed: 290 rows x 6 columns)

3. WHO:
	- Air pollution: concentrations of fine particular matter (PM2.5), SDG 11.6.2
	- https://www.who.int/data/gho/data/indicators/indicator-details/GHO/concentrations-of-fine-particulate-matter-%28pm2-5%29
	- Download file from Google drive
    - Data period: 2015-2019
	- Format: csv
    - Data size: 4,725

# Results
I. Initial Findings (Spearman Correlation)

- Significant Negative Link: Only Asthma (ρ=−0.51) and the Immunization (ρ=−0.48) show a statistically significant relationship with PM2.5.
- This negative link contradicted the biological hypothesis and suggested a major source of Ecological Confounding.

II. Mixed-Effects Model (MEM) Findings

- Asthma Reversal (Biological Hypothesis Confirmed): the relationship with Asthma reversed and became highly significant and positive (Coef.=+0.238). 
- PM2.5 is an independent risk factor for Asthma. The strong negative correlation was indeed an artifact of Ecological Confounding.
- The MEM found no significant independent PM2.5 effect for COPD or Diabetes, confirming that pollution is not the primary driver for these outcomes in this specific dataset.

III. Ecological Factors

- Policy Insight: For most chronic diseases in this dataset, PM2.5 is a proxy for larger determinants (Socioeconomic Status, healthcare access), which are far stronger drivers of prevalence than the air pollutant itself.

# Installation
**for the Data Selection and Preparation part**
- Get an API key for retrieving data from the EPA by using https://aqs.epa.gov/data/api/signup?email=myemail@example.com. You will receive the key in your email.
- create .env file in /src
- Set the registered email in the first line of the .env file using this template (aqs_epa_email=myemail@example.com)
- Set the obtained key in the second line of the .env file using this template (aqs_epa_key=yourkey)
- Special python packages
    - statsmodels
    - seaborn
    - scipy
    - matplotlib
    - numpy
    - pandas
	- requests
    - python-dotenv

# Running analysis
1. Data preprocessing
- Only five states are included as the study sample: California, Colorado, Illinois, New York, Texas.
- Tools: requests - for API calls, json + pandas for parsing and structuring data
- Tools: pandas - for filtering, cleaning, and handling missing data
    - U.S. PM2.5
      - Extract annual state-level PM2.5 data (2015-2022) from the EPA API.
      - Extract only 5 target states.
      - Keep all arithmetic mean values from every monitors
    - U.S. Chronic Disease
      - Filter columns where:
        - DataValueType: Age-adjusted Prevalence
        - StratificationCategory1: Overall
        - States: California, Colorado, Illinois, New York, Texas
        - Topic in the list of 17 diseases.
    - Global PM2.5
      - Keep only three columns: country, year, value.
2. Data aggregation & merging
   **Tools: pandas groupby/merge**
   - U.S. PM2.5 aggregated (2015–2022): one mean PM2.5 value per state per year.
   - Chronic disease prevalence (2019–2022): one prevalence value per disease, per state, per year.
   - Global PM2.5 aggregated (2015–2019): one mean PM2.5 value per year.
   - Merged dataset: U.S. PM2.5 and disease data merged on (state, year).
3. Trend analysis
   **Tools: pandas, matplotlib, seaborn**
   - U.S. PM2.5 trend (2015–2022): For 5 states individually.
   - U.S. vs Global PM2.5 trend (2015–2019): Uses overlapping years.
   - Heatmap of disease prevalence (2019–2022): Visualizes state- and year-level patterns.
   - Chronic disease trend plots (2019–2022): For all 17 diseases.
   - Chronic disease grouped bar charts (2019–2022): For all 17 diseases.
4. Correlation analysis (Spearman correlation)
   **Tools: scipy.stats - for Spearman correlation**
   - Reasons for choosing:
     - Many disease distributions are non-linear or non-normal.
     - Robust to monotonic but non-linear relationships.
   - For each of the 17 diseases:
     - Compute ρ (rho) and p-value.
     - Store results in structured dictionary.
     - Generate a correlation summary bar chart.
     - Generate scatter plots for selected diseases.
5. Mixed-Effects Models analysis
   **Tools: statsmodels.formula.api - for Mixed-Effects Models**
   - Reasons for choosing:
     - robust to the small sample size.
     - provide greater statistical power and reliability.
   - For each of the 17 diseases:
     - Compute the coefficients and variances
     - Generate a Mixed Effects Forest plot.
5. Visualization outputs
   **Tools: matplotlib / seaborn**
   - All figures are saved automatically in the ../results/ directory.
6. Summarize and interpret the results

From `src/` directory run:

`python main.py `

Results will appear in `results/` folder. All obtained will be stored in `data/`