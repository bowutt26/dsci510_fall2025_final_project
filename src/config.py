from pathlib import Path
from dotenv import load_dotenv

# project configuration from .env (secret part)
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)  # loads into os.environ

# project configuration
DATA_DIR = "../data"
RESULTS_DIR = "../results"

# data sources configuration
aqs_epa_url = "https://aqs.epa.gov/data/api/annualData/byState"
chronic_url = "https://data.cdc.gov/api/views/hksd-2xuw/rows.json?accessType=DOWNLOAD"
who_url = "https://drive.google.com/file/d/1Biiamr8qiEv3IZi0o8E7O1ylMBfcuBJh/view?usp=share_link"


