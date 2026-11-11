import json
from datetime import UTC, datetime

import boto3
from botocore.exceptions import ClientError

from src.config import AWS_REGION, S3_BUCKET_NAME
from src.logger import get_logger

logger=get_logger(__name__)

s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION
)


def upload_raw_weather_records(weather_upload_records):
    """Upload original API responses to S3."""

    ingestion_time = datetime.now(UTC)

    run_timestamp = ingestion_time.strftime(
        "%Y%m%dT%H%M%SZ"
    )

    ingestion_date = ingestion_time.strftime("%Y-%m-%d")
    ingestion_hour = ingestion_time.strftime("%H")

    successful_uploads = 0

    for record in weather_upload_records:

        city_name = record["city"].lower()

        raw_json = json.dumps(
            record["data"],
            indent=4,
            ensure_ascii=False
        )

        s3_key = (
            "weather-pipeline/raw/"
            f"ingestion_date={ingestion_date}/"
            f"ingestion_hour={ingestion_hour}/"
            f"{city_name}_{run_timestamp}.json"
        )

        try:
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_key,
                Body=raw_json.encode("utf-8"),
                ContentType="application/json"
            )

            verification = s3_client.head_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_key
            )

            logger.info(f"{city_name} uploaded successfully!")
            logger.info("Verified: %s", s3_key)
            logger.info(
                "File size %s bytes:",
                verification["ContentLength"]
            )
            logger.info(
                "Content type: %s",
                verification["ContentType"]
            )

            successful_uploads += 1

        except ClientError as error:

            error_code = error.response["Error"]["Code"]

            logger.exception(
                    "S3 operation failed for %s. Error code: %s",
                    city_name,
                    error_code
                )

    logger.info(
        "S3 uploads completed:%s/%s ",
        successful_uploads,
        len(weather_upload_records)
    )

    return successful_uploads
