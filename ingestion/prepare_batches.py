from pathlib import Path
import pandas as pd

REPO_ROOT=Path(__file__).resolve().parent.parent
SOURCE_DIR=REPO_ROOT / "data" / "raw_source"
BATCH_OUTPUT_DIR=REPO_ROOT / "data" / "batches"

BATCH_START_DATE = "2018-08-01"
BATCH_END_DATE = "2018-08-07"

TRANSACTIONAL_TABLES = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
}

MASTER_TABLES = {
    "customers": "olist_customers_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

def load_orders_in_range() -> pd.DataFrame:
    orders_path = SOURCE_DIR / TRANSACTIONAL_TABLES["orders"]
    orders = pd.read_csv(orders_path, parse_dates=["order_purchase_timestamp"])

    orders["batch_date"] = orders["order_purchase_timestamp"].dt.date.astype(str)

    mask = (orders["batch_date"] >= BATCH_START_DATE) & (orders["batch_date"] <= BATCH_END_DATE)
    orders_in_range = orders.loc[mask].copy()

    return orders_in_range

def build_daily_batches(orders_in_range: pd.DataFrame) -> None:
    other_transactional = {}
    for table_name, filename in TRANSACTIONAL_TABLES.items():
        if table_name == "orders":
            continue
        other_transactional[table_name] = pd.read_csv(SOURCE_DIR / filename)

    for batch_date, orders_group in orders_in_range.groupby("batch_date"):
        batch_dir = BATCH_OUTPUT_DIR / f"batch_date={batch_date}"
        batch_dir.mkdir(parents=True, exist_ok=True)

        orders_group.drop(columns=["batch_date"]).to_csv(batch_dir / "orders.csv", index=False)

        order_ids_today = set(orders_group["order_id"])

        for table_name, df in other_transactional.items():
            df_today = df[df["order_id"].isin(order_ids_today)]
            df_today.to_csv(batch_dir / f"{table_name}.csv", index=False)

def build_master_tables() -> None:
    master_dir = BATCH_OUTPUT_DIR / "master"
    master_dir.mkdir(parents=True, exist_ok=True)

    for table_name, filename in MASTER_TABLES.items():
        df = pd.read_csv(SOURCE_DIR / filename)
        df.to_csv(master_dir / f"{table_name}.csv", index=False)

def main() -> None:
    orders_in_range = load_orders_in_range()
    build_daily_batches(orders_in_range)
    build_master_tables()
    print("Batch processing complete.")

if __name__ == "__main__":
    main()