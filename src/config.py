from pathlib import Path
from dotenv import load_dotenv

# project configuration from .env (secret part)
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)  # loads into os.environ

# project configuration
DATA_DIR = "../data"
RESULTS_DIR = "../results"

# filename
pm25_file = "pm25_us.json"
chronic_file = "chronic_disease_us.json"
pm25_global_file = "pm25_global.csv"

# data sources configuration
aqs_epa_url = "https://aqs.epa.gov/data/api/annualData/byState"
chronic_url = "https://data.cdc.gov/api/views/hksd-2xuw/rows.json?accessType=DOWNLOAD"
global_url = "https://drive.google.com/file/d/1Biiamr8qiEv3IZi0o8E7O1ylMBfcuBJh/view?usp=share_link"

# Filter criteria for chronic disease dataset
TARGET_DATA_TYPE = "Age-adjusted Prevalence"
TARGET_STRATIFICATION = "Overall"
TARGET_STATES = ["California", "Colorado", "Illinois", "New York", "Texas"]
TARGET_YEAR_MIN = 2015
TARGET_YEAR_MAX = 2022

# Filter criteria for global PM2.5 dataset
TARGET_INDICATOR = "Concentrations of fine particulate matter (PM2.5)"

# for calculate correlation
TARGET_DISEASE = ['Alcohol', 'Arthritis', 'Asthma', 'Cardiovascular Disease',
         'Chronic Obstructive Pulmonary Disease', 'Cognitive Health and Caregiving',
         'Diabetes', 'Disability', 'Health Status', 'Immunization', 'Mental Health',
         'Nutrition, Physical Activity, and Weight Status',
         'Social Determinants of Health', 'Tobacco', 'Cancer', 'Oral Health', 'Sleep']
MIN_SAMPLE_SIZE = 10