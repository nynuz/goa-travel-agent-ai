import pandas as pd

from goa_travel_agent.config.settings import settings
from goa_travel_agent.src.utils.logger import get_logger

log = get_logger(__name__)


# ---------------------------------------------------------------------------
# Hotels
# ---------------------------------------------------------------------------

def preprocess_hotels(df: pd.DataFrame) -> pd.DataFrame:
    """Filter Goa hotels, drop nulls on critical fields, create search_text."""
    # Keep only relevant columns that exist
    cols = [c for c in settings.HOTEL_COLUMNS if c in df.columns]
    df = df[cols].copy()

    # Filter state == Goa (case-insensitive)
    if "state" in df.columns:
        df = df[df["state"].astype(str).str.strip().str.lower() == "goa"]

    # Drop rows missing critical fields
    critical = ["property_name", "locality", "hotel_star_rating"]
    existing_critical = [c for c in critical if c in df.columns]
    df = df.dropna(subset=existing_critical)

    # Clamp ratings
    if "hotel_star_rating" in df.columns:
        df["hotel_star_rating"] = pd.to_numeric(df["hotel_star_rating"], errors="coerce").clip(1, 5)
    if "site_review_rating" in df.columns:
        df["site_review_rating"] = pd.to_numeric(df["site_review_rating"], errors="coerce").clip(0, 5)
    if "site_review_count" in df.columns:
        df["site_review_count"] = pd.to_numeric(df["site_review_count"], errors="coerce").fillna(0).astype(int)

    # Fill secondary nulls
    for col in ["hotel_facilities", "room_type", "address"]:
        if col in df.columns:
            df[col] = df[col].fillna("N/A")

    # Create combined search text
    parts = []
    for col in ["property_name", "hotel_facilities", "locality", "room_type"]:
        if col in df.columns:
            parts.append(df[col].fillna("").astype(str))
    if parts:
        df["search_text"] = pd.Series([" ".join(p) for p in zip(*parts)])
    else:
        df["search_text"] = ""
    df["search_text"] = df["search_text"].fillna("")

    df = df.reset_index(drop=True)
    log.info("Hotels after preprocessing: %d rows", len(df))
    return df


# ---------------------------------------------------------------------------
# Places
# ---------------------------------------------------------------------------

def _categorize_place(text: str) -> str:
    """Auto-categorize a place based on keyword matching."""
    text_lower = text.lower()
    matched = []
    for category, keywords in settings.PLACE_CATEGORIES.items():
        if any(kw in text_lower for kw in keywords):
            matched.append(category)
    return ", ".join(matched) if matched else "General"


def preprocess_places(df: pd.DataFrame) -> pd.DataFrame:
    """Filter Goa places, dedup keeping longest review, categorize, create full_text."""
    # Normalize city
    if "city" in df.columns:
        df["city"] = df["city"].astype(str).str.strip().str.lower()
    elif "City" in df.columns:
        df.rename(columns={"City": "city"}, inplace=True)
        df["city"] = df["city"].astype(str).str.strip().str.lower()

    # Filter Goa cities
    df = df[df["city"].isin(settings.GOA_CITIES)].copy()

    # Normalize other column names that may still be title-case from the raw CSV
    rename_map = {}
    for col in df.columns:
        lower = col.lower().replace(" ", "_")
        if lower != col:
            rename_map[col] = lower
    if rename_map:
        df.rename(columns=rename_map, inplace=True)

    # Dedup: keep row with longest review per place+city
    review_col = "review" if "review" in df.columns else None
    place_col = "place" if "place" in df.columns else None

    if review_col and place_col:
        df["_review_len"] = df[review_col].astype(str).str.len()
        df = df.sort_values("_review_len", ascending=False)
        df = df.drop_duplicates(subset=["city", place_col], keep="first")
        df = df.drop(columns=["_review_len"])

    # Auto-categorize
    text_for_cat = ""
    for col in ["place", "review", "city"]:
        if col in df.columns:
            text_for_cat = df[col].astype(str)
            break
    if isinstance(text_for_cat, pd.Series):
        combined_text = df.apply(
            lambda r: " ".join(str(r.get(c, "")) for c in ["place", "review", "city"]),
            axis=1,
        )
        df["category"] = combined_text.apply(_categorize_place)
    else:
        df["category"] = "General"

    # Create full_text
    parts = []
    for col in ["place", "review", "city"]:
        if col in df.columns:
            parts.append(df[col].fillna("").astype(str))
    if parts:
        df["full_text"] = (
            parts[0]
            + (" - " + parts[1] if len(parts) > 1 else "")
            + (" - Located in " + parts[2] if len(parts) > 2 else "")
        )
    else:
        df["full_text"] = ""
    df["full_text"] = df["full_text"].fillna("")

    df = df.reset_index(drop=True)
    log.info("Places after preprocessing: %d rows", len(df))
    return df


# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------

def save_processed(hotels_df: pd.DataFrame, places_df: pd.DataFrame) -> None:
    settings.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    hotels_df.to_csv(settings.HOTELS_CSV, index=False)
    places_df.to_csv(settings.PLACES_CSV, index=False)
    log.info("Saved processed CSVs to %s", settings.PROCESSED_DIR)
