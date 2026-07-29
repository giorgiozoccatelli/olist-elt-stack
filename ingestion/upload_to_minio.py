import os
from pathlib import Path
import boto3
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
BATCH_OUTPUT_DIR = REPO_ROOT / "data" / "batches"

load_dotenv(REPO_ROOT / ".env")

MINIO_ENDPOINT = f"http://localhost:{os.environ['MINIO_API_PORT']}"
MINIO_ACCESS_KEY = os.environ["MINIO_ROOT_USER"]
MINIO_SECRET_KEY = os.environ["MINIO_ROOT_PASSWORD"]
MINIO_BUCKET = os.environ["MINIO_BUCKET_RAW"]

def get_minio_client():
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
    )

def upload_batches_to_minio() -> None:
    client = get_minio_client()
    file_paths = sorted(BATCH_OUTPUT_DIR.rglob("*.csv"))

    for file_path in file_paths:
        object_key = str(file_path.relative_to(BATCH_OUTPUT_DIR))

        client.upload_file(
            Filename=str(file_path),
            Bucket=MINIO_BUCKET,
            Key=object_key,
        )
    print("Upload complete.")

def main() -> None:
    upload_batches_to_minio()

if __name__ == "__main__":
    main()
