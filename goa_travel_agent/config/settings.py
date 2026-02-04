import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# -- Paths --
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CACHE_DIR = DATA_DIR / "cache"

# -- API keys --
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

# -- Kaggle datasets --
HOTELS_DATASET = "PromptCloudHQ/hotels-on-goibibo"
PLACES_DATASET = "ritvik1909/indian-places-to-visit-reviews-data"

# -- Qdrant collections --
HOTELS_COLLECTION = "goa_hotels"
PLACES_COLLECTION = "goa_places"

# -- Embeddings --
DENSE_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DENSE_DIM = 384
CROSS_ENCODER_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
TFIDF_PATH = CACHE_DIR / "tfidf_model.joblib"

# -- Processed CSV names --
HOTELS_CSV = PROCESSED_DIR / "goa_hotels.csv"
PLACES_CSV = PROCESSED_DIR / "goa_places.csv"

# -- Goa cities for places filtering --
GOA_CITIES = [
    "agonda", "alto-porvorim", "amboli", "anjuna", "arambol", "assagao",
    "baga", "bardez", "benaulim", "calangute", "canacona", "candolim",
    "chapora", "colva", "divar island", "dona paula", "margao",
    "marmagao", "mapusa", "mobor", "morjim", "nuvem", "old goa",
    "palolem", "panjim", "porvorim", "quepem", "saligao", "sangolda",
    "sanguem", "sanquelim", "vasco da gama", "varca", "vagator",
    "velsao", "verna",
]

# -- Hotel columns to keep --
HOTEL_COLUMNS = [
    "property_id",
    "property_name",
    "hotel_facilities",
    "address",
    "locality",
    "city",
    "state",
    "hotel_star_rating",
    "site_review_rating",
    "site_review_count",
    "room_type",
]

# -- Place categories keyword map --
PLACE_CATEGORIES: dict[str, list[str]] = {
    "Beach": ["beach", "shore", "sand", "coast", "seaside", "sea"],
    "Nightlife": ["club", "bar", "party", "nightlife", "pub", "disco"],
    "Culture": ["church", "temple", "museum", "fort", "heritage", "cathedral", "basilica", "chapel", "ruins"],
    "Adventure": ["water sport", "diving", "parasailing", "trekking", "kayak", "surf", "jet ski", "rafting"],
    "Wellness": ["spa", "yoga", "meditation", "ayurved", "retreat"],
    "Food": ["restaurant", "cafe", "market", "shack", "bakery", "food"],
}


class _Settings:
    """Convenience accessor for all settings."""

    PROJECT_ROOT = PROJECT_ROOT
    DATA_DIR = DATA_DIR
    RAW_DIR = RAW_DIR
    PROCESSED_DIR = PROCESSED_DIR
    CACHE_DIR = CACHE_DIR

    OPENAI_API_KEY = OPENAI_API_KEY
    QDRANT_URL = QDRANT_URL
    QDRANT_API_KEY = QDRANT_API_KEY
    TAVILY_API_KEY = TAVILY_API_KEY

    HOTELS_DATASET = HOTELS_DATASET
    PLACES_DATASET = PLACES_DATASET
    HOTELS_COLLECTION = HOTELS_COLLECTION
    PLACES_COLLECTION = PLACES_COLLECTION

    DENSE_MODEL_NAME = DENSE_MODEL_NAME
    DENSE_DIM = DENSE_DIM
    CROSS_ENCODER_NAME = CROSS_ENCODER_NAME
    TFIDF_PATH = TFIDF_PATH

    HOTELS_CSV = HOTELS_CSV
    PLACES_CSV = PLACES_CSV
    GOA_CITIES = GOA_CITIES
    HOTEL_COLUMNS = HOTEL_COLUMNS
    PLACE_CATEGORIES = PLACE_CATEGORIES


settings = _Settings()
