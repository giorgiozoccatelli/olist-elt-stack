import io
import os
from pathlib import Path
import boto3
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")

MINIO_ENDPOINT = f"http://localhost:{os.environ['MINIO_API_PORT']}"
MINIO_ACCESS_KEY = os.environ["MINIO_ROOT_USER"]
MINIO_SECRET_KEY = os.environ["MINIO_ROOT_PASSWORD"]
MINIO_BUCKET = os.environ["MINIO_BUCKET_RAW"]

POSTGRES_URL = (
    f"postgresql+psycopg2://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}"
    f"@localhost:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}"
)

TRANSACTIONAL_TABLES = ["orders", "order_items", "order_payments", "order_reviews"]
MASTER_TABLES = ["customers", "products", "sellers", "geolocation", "category_translation"]

def get_minio_client():
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
    )

def read_csv_from_minio(client, object_key: str) -> pd.DataFrame:
    response = client.get_object(Bucket=MINIO_BUCKET, Key=object_key)
    file_bytes = response["Body"].read()
    return pd.read_csv(io.BytesIO(file_bytes))

def load_master_tables(client, engine) -> None:
    for table_name in MASTER_TABLES:
        object_key = f"master/{table_name}.csv"
        df = read_csv_from_minio(client, object_key)

        df.to_sql(table_name, engine, schema="raw", if_exists="replace", index=False)

def list_batch_dates(client) -> list[str]:
    response = client.list_objects_v2(Bucket=MINIO_BUCKET, Prefix="batch_date=", Delimiter="/")
    prefixes = response.get("CommonPrefixes", [])
    return sorted(p["Prefix"].rstrip("/") for p in prefixes)

def load_transactional_tables(client) -> None:
    engine = create_engine(POSTGRES_URL)
    batch_dates = list_batch_dates(client)

    for table_name in TRANSACTIONAL_TABLES:
        for i, batch_date in enumerate(batch_dates):
            object_key = f"{batch_date}/{table_name}.csv"
            df = read_csv_from_minio(client, object_key)

            write_mode = "replace" if i == 0 else "append"
            df.to_sql(table_name, engine, schema="raw", if_exists=write_mode, index=False)


def main() -> None:
    client = get_minio_client()
    engine = create_engine(POSTGRES_URL)

    load_master_tables(client, engine)
    load_transactional_tables(client)

    print("Loading in Postgres complete.")


if __name__ == "__main__":
    main()