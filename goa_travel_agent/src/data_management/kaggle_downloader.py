import os
import time
import zipfile
from pathlib import Path

from goa_travel_agent.config.settings import settings
from goa_travel_agent.src.utils.logger import get_logger

log = get_logger(__name__)

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


def _ensure_kaggle_env() -> None:
    """Set KAGGLE_USERNAME / KAGGLE_KEY from .env if present."""
    username = os.getenv("KAGGLE_USERNAME", "")
    key = os.getenv("KAGGLE_KEY", "")
    if username and key:
        os.environ["KAGGLE_USERNAME"] = username
        os.environ["KAGGLE_KEY"] = key
        log.info("Kaggle credentials loaded from environment variables.")
    else:
        raise RuntimeError(
            "Kaggle credentials not found. "
            "Set KAGGLE_USERNAME and KAGGLE_KEY in your .env file."
        )


def download_dataset(dataset_slug: str, dest_dir: Path) -> Path:
    """Download and extract a Kaggle dataset with retry logic.

    Returns the directory containing the extracted files.
    """
    _ensure_kaggle_env()
    from kaggle.api.kaggle_api_extended import KaggleApi

    dest_dir.mkdir(parents=True, exist_ok=True)
    dataset_name = dataset_slug.split("/")[-1]
    extract_dir = dest_dir / dataset_name

    if extract_dir.exists() and any(extract_dir.iterdir()):
        log.info("Dataset '%s' already downloaded at %s", dataset_slug, extract_dir)
        return extract_dir

    api = KaggleApi()
    api.authenticate()

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            log.info("Downloading '%s' (attempt %d/%d)...", dataset_slug, attempt, MAX_RETRIES)
            api.dataset_download_files(dataset_slug, path=str(dest_dir), unzip=False)

            zip_path = dest_dir / f"{dataset_name}.zip"
            if zip_path.exists():
                extract_dir.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(zip_path, "r") as zf:
                    zf.extractall(extract_dir)
                zip_path.unlink()
                log.info("Extracted to %s", extract_dir)
            return extract_dir

        except Exception as exc:
            log.warning("Attempt %d failed: %s", attempt, exc)
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)
            else:
                raise RuntimeError(
                    f"Failed to download '{dataset_slug}' after {MAX_RETRIES} attempts"
                ) from exc

    return extract_dir  # unreachable but keeps type-checkers happy


def download_all() -> tuple[Path, Path]:
    """Download both hotel and places datasets. Returns (hotels_dir, places_dir)."""
    hotels_dir = download_dataset(settings.HOTELS_DATASET, settings.RAW_DIR)
    places_dir = download_dataset(settings.PLACES_DATASET, settings.RAW_DIR)
    return hotels_dir, places_dir
