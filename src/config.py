import os

from dotenv import load_dotenv

# Load environment variables from the project's .env file
load_dotenv()

# AWS configuration
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# PostgreSQL configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "weather_analytics"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}


def validate_config():
    """Check that required configuration is available."""

    if not S3_BUCKET_NAME:
        raise ValueError("S3_BUCKET_NAME is missing from .env")

    if not DB_CONFIG["password"]:
        raise ValueError("DB_PASSWORD is missing from .env")
