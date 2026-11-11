from src.config import validate_config
from src.database import load_weather_to_postgres
from src.extract import CITIES, fetch_all_weather
from src.logger import get_logger
from src.storage import upload_raw_weather_records
from src.transform import transform_weather_records

logger = get_logger(__name__)


def main():

    try:
        logger.info("Starting weather data pipeline")

        # Step 1: Validate configuration
        logger.info("Validating application configuration")
        validate_config()

        # Step 2: Extract weather
        logger.info("Starting weather extraction")

        weather_records, weather_upload_records = (
            fetch_all_weather()
        )

        if len(weather_records) != len(CITIES):
            raise RuntimeError(
                f"Expected {len(CITIES)} weather records, "
                f"but received {len(weather_records)}"
            )

        logger.info(
            "Weather extraction completed. Records fetched: %s",
            len(weather_records)
        )

        # Step 3: Upload raw JSON to S3
        logger.info("Starting S3 storage")
        successful_uploads=upload_raw_weather_records(
            weather_upload_records
        )
        if successful_uploads !=len(weather_upload_records):
            raise RuntimeError(
                "Not all weather records were uploaded to S3"
            )

        # Step 4: Transform records
        logger.info("Starting data transformation")

        df = transform_weather_records(weather_records)

        logger.info(
            "Data transformation completed. Records: %s",
            len(df)
        )

        # Step 5: Load into PostgreSQL
        logger.info("Starting PostgreSQL loading")

        load_weather_to_postgres(df)

        logger.info("Weather pipeline completed successfully")

    except Exception:
        logger.exception("Weather pipeline failed")
        raise


if __name__ == "__main__":
    main()
