import pandas as pd

from src.logger import get_logger

logger=get_logger(__name__)

def transform_weather_records(weather_records):

    required_columns = [
    "city",
    "latitude",
    "longitude",
    "temperature",
    "temperature_unit",
    "observation_time",
    "ingestion_timestamp",
    "weather_code",
    "weather_description"
    ]


    """Convert extracted weather records into a clean DataFrame."""

    if not weather_records:
        raise ValueError("No weather records available for transformation")

    df = pd.DataFrame(weather_records)
    
    missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Convert timestamps into datetime values
    df["observation_time"] = pd.to_datetime(
        df["observation_time"]
    )

    df["ingestion_timestamp"] = pd.to_datetime(
        df["ingestion_timestamp"]
    )

    # Basic data quality report
    logger.info("\nDataFrame information: %s",df.info())
    

    logger.info("\nStatistical summary: %s", df.describe())
    logger.warning("\nMissing values: %s",df.isnull().sum())

    print(
        "\nDuplicate city-observation records: %s", df.duplicated(
            subset=["city", "observation_time"]
        ).sum(),
    )

    return df
