Real-World Weather Data Engineering Pipeline
An end-to-end data engineering project that extracts real-time weather data from the Open-Meteo API, stores raw data in AWS S3, transforms and validates records using Python and Pandas, and loads structured data into PostgreSQL using Apache Airflow orchestration.
Project Architecture
Open-Meteo API
      |
      v
Weather Data Extraction
      |
      v
Raw JSON Records
      |
      v
AWS S3 Storage
      |
      v
Data Transformation & Validation
(Python + Pandas)
      |
      v
PostgreSQL Database
Apache Airflow orchestrates the workflow, while Docker Compose manages the application infrastructure.
Technology Stack
- Programming: Python
- Orchestration: Apache Airflow
- Cloud Storage: AWS S3
- Database: PostgreSQL
- Data Processing: Pandas
- Containerization: Docker and Docker Compose
- API: Open-Meteo Weather API
- AWS SDK: Boto3
Airflow Workflow
The weather_workflow DAG contains five tasks:
1. validate_configuration – Validates application configuration.
2. extract_weather – Extracts weather data for Lahore, Karachi, and Islamabad.
3. upload_to_s3 – Uploads raw weather records to AWS S3.
4. transform_weather – Cleans and transforms the extracted records using Pandas.
5. load_to_postgres – Loads transformed records into PostgreSQL.
The workflow uses Airflow's TaskFlow API, with two retries and a two-minute retry delay.
Project Structure
weather-data-engineering-pipeline/
│
├── dags/
│   └── weather_workflow.py
│
├── src/
│   ├── config.py
│   ├── database.py
│   ├── extract.py
│   ├── logger.py
│   ├── storage.py
│   └── transform.py
│
├── tests/
│   └── test_extract.py
│
├── config/
├── Dockerfile
├── Dockerfile.airflow
├── docker-compose.yml
├── airflow-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── main.py
Prerequisites
Before running the project, install:
- Docker
- Docker Compose
- Python 3
- AWS CLI
- An AWS account with access to an S3
