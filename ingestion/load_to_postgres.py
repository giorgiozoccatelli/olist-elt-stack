import io
import pandas as pd
from sqlalchemy import inspect, text
from config import MINIO_BUCKET, get_engine, get_minio_client

TRANSACTIONAL_TABLES = ["orders", "order_items", "order_payments", "order_reviews"]
MASTER_TABLES = ["customers", "products", "sellers", "geolocation", "category_translation"]

def read_csv_from_minio(client, object_key: str) -> pd.DataFrame:
    response = client.get_object(Bucket=MINIO_BUCKET, Key=object_key)
    file_bytes = response["Body"].read()
    return pd.read_csv(io.BytesIO(file_bytes))

def write_table(df: pd.DataFrame, table_name: str, engine, first_chunk: bool) -> None:
    """Write a dataframe to raw.<table_name>.

    The first chunk empties the table with TRUNCATE (not DROP, which would fail
    because dbt views depend on it), so the load can be re-run safely.
    """
    if first_chunk and inspect(engine).has_table(table_name, schema="raw"):
        with engine.begin() as conn:
            conn.execute(text(f"TRUNCATE TABLE raw.{table_name}"))
    df.to_sql(table_name, engine, schema="raw", if_exists="append", index=False)

def load_master_tables(client, engine) -> None:
    for table_name in MASTER_TABLES:
        object_key = f"master/{table_name}.csv"
        df = read_csv_from_minio(client, object_key)

        write_table(df, table_name, engine, first_chunk=True)

def list_batch_dates(client) -> list[str]:
    response = client.list_objects_v2(Bucket=MINIO_BUCKET, Prefix="batch_date=", Delimiter="/")
    prefixes = response.get("CommonPrefixes", [])
    return sorted(p["Prefix"].rstrip("/") for p in prefixes)

def load_transactional_tables(client, engine) -> None:
    batch_dates = list_batch_dates(client)

    for table_name in TRANSACTIONAL_TABLES:
        for i, batch_date in enumerate(batch_dates):
            object_key = f"{batch_date}/{table_name}.csv"
            df = read_csv_from_minio(client, object_key)

            write_table(df, table_name, engine, first_chunk=(i == 0))


def main() -> None:
    client = get_minio_client()
    engine = get_engine()

    load_master_tables(client, engine)
    load_transactional_tables(client, engine)

    print("Loading in Postgres complete.")


if __name__ == "__main__":
    main()
