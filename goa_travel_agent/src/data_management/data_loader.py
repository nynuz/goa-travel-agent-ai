from pathlib import Path

import pandas as pd

from goa_travel_agent.src.utils.logger import get_logger

log = get_logger(__name__)


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df


def load_hotels_csv(raw_dir: Path) -> pd.DataFrame:
    """Load the raw hotel CSV and normalize column names."""
    candidates = list(raw_dir.glob("*.csv"))
    if not candidates:
        raise FileNotFoundError(f"No CSV found in {raw_dir}")
    csv_path = candidates[0]
    log.info("Loading hotels CSV: %s", csv_path.name)
    df = pd.read_csv(csv_path)
    return _normalize_columns(df)


def load_places_csv(raw_dir: Path) -> pd.DataFrame:
    """Load the raw places/reviews CSV and normalize column names."""
    candidates = list(raw_dir.glob("*.csv"))
    if not candidates:
        raise FileNotFoundError(f"No CSV found in {raw_dir}")
    csv_path = candidates[0]
    log.info("Loading places CSV: %s", csv_path.name)
    df = pd.read_csv(csv_path)
    return _normalize_columns(df)
