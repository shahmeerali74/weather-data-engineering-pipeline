import psycopg

from src.config import DB_CONFIG
from src.logger import get_logger

logger=get_logger(__name__)

INSERT_QUERY = """
    INSERT INTO weather_records (
        city,
        latitude,
        longitude,
        temperature,
        temperature_unit,
        observation_time,
        ingestion_timestamp,
        weather_code,
        weather_description
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)

    ON CONFLICT (city, observation_time)
    DO UPDATE SET
        latitude = EXCLUDED.latitude,
        longitude = EXCLUDED.longitude,
        temperature = EXCLUDED.temperature,
        temperature_unit = EXCLUDED.temperature_unit,
        ingestion_timestamp = EXCLUDED.ingestion_timestamp,
        weather_code = EXCLUDED.weather_code,
        weather_description = EXCLUDED.weather_description;
"""


def load_weather_to_postgres(df):
    """Insert or update weather records in PostgreSQL."""

    if df.empty:
        raise ValueError("Cannot load an empty DataFrame")

    try:
        with (psycopg.connect(**DB_CONFIG) as connection,
             connection.cursor() as cursor):

                for record in df.itertuples(
                    index=False,
                    name=None
                ):
                    cursor.execute(INSERT_QUERY, record)

        logger.info(
            f"Successfully loaded {len(df)} weather records!"
        )

    except psycopg.Error:
        logger.exception("PostgreSQL insertion failed")
        raise
