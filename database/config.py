import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "driver": os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server"),
    "server": os.getenv("DB_SERVER"),
    "database": os.getenv("DB_DATABASE"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "trust_cert": "yes",
    "timeout": 5
}