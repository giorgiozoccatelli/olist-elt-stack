"""Shared settings and clients for the ingestion scripts.

Hosts default to localhost (scripts run from the Mac). Inside Docker, set
MINIO_ENDPOINT and POSTGRES_HOST / POSTGRES_PORT to the service names.
"""
import os
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from sqlalchemy import create_engine

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", f"http://localhost:{os.environ['MINIO_API_PORT']}")
MINIO_ACCESS_KEY = os.environ["MINIO_ROOT_USER"]
MINIO_SECRET_KEY = os.environ["MINIO_ROOT_PASSWORD"]
MINIO_BUCKET = os.environ["MINIO_BUCKET_RAW"]

POSTGRES_URL = (
    f"postgresql+psycopg2://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}"
    f"@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}"
)


def get_minio_client():
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
    )


def ensure_bucket(client) -> None:
    """Create the raw bucket if it does not exist yet."""
    try:
        client.head_bucket(Bucket=MINIO_BUCKET)
    except ClientError:
        client.create_bucket(Bucket=MINIO_BUCKET)


def get_engine():
    return create_engine(POSTGRES_URL)
