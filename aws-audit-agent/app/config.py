import os
from dotenv import load_dotenv
load_dotenv()

APP_NAME = os.getenv("APP_NAME", "AWS Account Audit Agent")
DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/audits.db")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
SECURITY_HUB_ADMIN_TOKEN = os.getenv("SECURITY_HUB_ADMIN_TOKEN", "")
