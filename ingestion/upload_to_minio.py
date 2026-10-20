from config import MINIO_BUCKET, REPO_ROOT, ensure_bucket, get_minio_client

BATCH_OUTPUT_DIR = REPO_ROOT / "data" / "batches"

def upload_batches_to_minio() -> None:
    client = get_minio_client()
    ensure_bucket(client)
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
