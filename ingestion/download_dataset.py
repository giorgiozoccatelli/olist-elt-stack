from pathlib import Path
from kaggle.api.kaggle_api_extended import KaggleApi

DATASET_REF = "olistbr/brazilian-ecommerce"
DOWNLOAD_DIR = Path(__file__).resolve().parent.parent / "data" / "raw_source"

def download_olist_dataset() -> None:
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    api = KaggleApi()
    api.authenticate()

    api.dataset_download_files(DATASET_REF, path=str(DOWNLOAD_DIR), unzip=True)
    print("Download complete.")

if __name__ == "__main__":
    download_olist_dataset()