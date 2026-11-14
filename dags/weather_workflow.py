from datetime import datetime, timedelta

from airflow.sdk import dag, task

from src.config import validate_config
from src.extract import CITIES, fetch_all_weather
from src.storage import upload_raw_weather_records
from src.transform import transform_weather_records
from src.database import load_weather_to_postgres
@dag(
    dag_id="weather_workflow",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    default_args={
        "retries":2,
        "retry_delay":timedelta(minutes=2),
    },
    tags=["weather", "data-engineering"],
)
def weather_workflow():

    @task
    def validate_configuration():
        print("Validating weather pipeline configuration...")

        validate_config()

        print("Configuration validation successful!")
        return True

    @task
    def extract_weather(validation_passed):
        if not validation_passed:
            raise RuntimeError("Configuration validation failed")

        print("Starting weather extraction...")

        weather_records, weather_upload_records = fetch_all_weather()

        if len(weather_records) != len(CITIES):
            raise RuntimeError(
                f"Expected {len(CITIES)} weather records, "
                f"but received {len(weather_records)}"
            )

        print(f"Successfully extracted {len(weather_records)} cities")

        return {
            "weather_records": weather_records,
            "weather_upload_records": weather_upload_records,
        }


    @task
    def upload_to_s3(extracted_data):

        print("Starting raw weather data upload to S3...")

        weather_upload_records = extracted_data["weather_upload_records"]

        successful_uploads = upload_raw_weather_records(
            weather_upload_records
        )

        if successful_uploads != len(weather_upload_records):
            raise RuntimeError(
                "Not all weather records were uploaded to S3"
            )

        print(
            f"Successfully uploaded {successful_uploads} records to S3"
        )

        return successful_uploads

    @task
    def transform_weather(extracted_data):

        print("Starting weather data transformation...")

        weather_records = extracted_data["weather_records"]

        df = transform_weather_records(weather_records)

        if df.empty:
            raise RuntimeError("Transformation returned an empty DataFrame")

        print(f"Successfully transformed {len(df)} records")

        return df.astype({
          "observation_time": "str",
          "ingestion_timestamp": "str",
        }).to_dict(orient="records")
    
    @task
    def load_to_postgres(transformed_records):
        import pandas as pd

        print("Starting PostgreSQL loading...")

        df = pd.DataFrame(transformed_records)
        if df.empty:
            raise RuntimeError(
                "No transformed records available for PostgreSQL loading"
            )
        expected_columns = [
            "city",
            "latitude",
            "longitude",
            "temperature",
            "temperature_unit",
            "observation_time",
            "ingestion_timestamp",
            "weather_code",
            "weather_description",
        ]

        df = df[expected_columns]

        print("DataFrame columns:", df.columns.tolist())
        print("First record:", df.iloc[0].to_dict())


        df["observation_time"] = pd.to_datetime(
            df["observation_time"]
        )

        df["ingestion_timestamp"] = pd.to_datetime(
            df["ingestion_timestamp"],
            utc=True
        )

        load_weather_to_postgres(df)

        print(
            f"Successfully loaded {len(df)} records into PostgreSQL"
        )
    validation_result = validate_configuration()
    extracted_data = extract_weather(validation_result)
    upload_to_s3(extracted_data)
    transformed_data = transform_weather(extracted_data)
    load_to_postgres(transformed_data)
weather_workflow()



