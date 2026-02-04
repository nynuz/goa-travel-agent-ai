"""Goa Travel Agent — main entry point.

Usage:
    uv run python main.py          # CLI interactive mode
    uv run python main.py --ui     # Launch Streamlit web app
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))


def _run_data_pipeline() -> tuple:
    """STEP 1: Download & preprocess datasets (skipped if CSVs already exist)."""
    import pandas as pd

    from goa_travel_agent.config.settings import settings
    from goa_travel_agent.src.utils.logger import get_logger

    log = get_logger("pipeline")

    if settings.HOTELS_CSV.exists() and settings.PLACES_CSV.exists():
        log.info("Processed CSVs already exist, loading...")
        hotels_df = pd.read_csv(settings.HOTELS_CSV)
        places_df = pd.read_csv(settings.PLACES_CSV)
        log.info("Hotels: %d rows  |  Places: %d rows", len(hotels_df), len(places_df))
        return hotels_df, places_df

    # Download
    from goa_travel_agent.src.data_management.kaggle_downloader import download_all

    log.info("Downloading datasets from Kaggle...")
    hotels_dir, places_dir = download_all()

    # Load raw CSVs
    from goa_travel_agent.src.data_management.data_loader import load_hotels_csv, load_places_csv

    raw_hotels = load_hotels_csv(hotels_dir)
    raw_places = load_places_csv(places_dir)

    # Preprocess
    from goa_travel_agent.src.data_management.preprocessor import (
        preprocess_hotels,
        preprocess_places,
        save_processed,
    )

    hotels_df = preprocess_hotels(raw_hotels)
    places_df = preprocess_places(raw_places)
    save_processed(hotels_df, places_df)

    log.info("Hotels: %d rows  |  Places: %d rows", len(hotels_df), len(places_df))
    print(f"\n--- Hotels sample ---\n{hotels_df.head(3).to_string()}")
    print(f"\n--- Places sample ---\n{places_df.head(3).to_string()}")

    return hotels_df, places_df


def _run_embeddings(hotels_df, places_df):
    """STEP 2: Fit TF-IDF + encode embeddings + upload to Qdrant (skipped if already done)."""
    from goa_travel_agent.config.settings import settings
    from goa_travel_agent.src.embeddings.hybrid_embedder import HybridEmbedder
    from goa_travel_agent.src.vector_db.qdrant_manager import QdrantManager
    from goa_travel_agent.src.utils.logger import get_logger

    log = get_logger("embeddings")
    embedder = HybridEmbedder()

    # Fit TF-IDF once on full corpus (CRITICAL FIX)
    if not embedder.is_tfidf_fitted():
        corpus = hotels_df["search_text"].tolist() + places_df["full_text"].tolist()
        embedder.fit_tfidf(corpus)
    else:
        embedder.load_tfidf()
        log.info("TF-IDF model already fitted, loaded from cache.")

    # Upload to Qdrant (skip if already populated)
    if not settings.QDRANT_URL:
        log.warning("QDRANT_URL not set. Skipping Qdrant upload.")
        return embedder

    manager = QdrantManager()

    if manager.collection_exists_and_populated(settings.HOTELS_COLLECTION):
        log.info("Hotels collection already populated (%d points).", manager.collection_count(settings.HOTELS_COLLECTION))
    else:
        log.info("Setting up hotels collection...")
        manager.setup_hotels_collection(hotels_df, embedder)

    if manager.collection_exists_and_populated(settings.PLACES_COLLECTION):
        log.info("Places collection already populated (%d points).", manager.collection_count(settings.PLACES_COLLECTION))
    else:
        log.info("Setting up places collection...")
        manager.setup_places_collection(places_df, embedder)

    return embedder


def _run_search_demo(embedder):
    """STEP 3: Run example hybrid searches."""
    from goa_travel_agent.config.settings import settings
    from goa_travel_agent.src.vector_db.searcher import HybridSearcher
    from goa_travel_agent.src.utils.logger import get_logger

    log = get_logger("search")

    if not settings.QDRANT_URL:
        log.warning("Qdrant not configured. Skipping search demo.")
        return None

    searcher = HybridSearcher(embedder=embedder)

    print("\n=== Hotel Search: 'luxury resort with pool near beach' ===")
    hotel_results = searcher.search_hotels("luxury resort with pool near beach", min_stars=4, top_k=3)
    for r in hotel_results:
        print(f"  {r.get('property_name')} | {r.get('hotel_star_rating')}★ | {r.get('locality')} | score={r.get('rerank_score', 0):.3f}")

    print("\n=== Places Search: 'romantic sunset point' ===")
    place_results = searcher.search_places("romantic sunset point", top_k=3)
    for r in place_results:
        print(f"  {r.get('place', r.get('full_text', '')[:60])} | {r.get('city')} | score={r.get('rerank_score', 0):.3f}")

    return searcher


def _run_cli(searcher):
    """STEP 4+5: Interactive CLI with agent selection."""
    from goa_travel_agent.config.settings import settings
    from goa_travel_agent.src.tools import hotel_search as hs_mod
    from goa_travel_agent.src.tools import places_search as ps_mod
    from goa_travel_agent.src.utils.logger import get_logger

    log = get_logger("cli")

    if not settings.OPENAI_API_KEY:
        log.warning("OPENAI_API_KEY not set. Skipping agent CLI.")
        return

    # Wire searcher into tools
    if searcher:
        hs_mod.set_searcher(searcher)
        ps_mod.set_searcher(searcher)

    from goa_travel_agent.src.agents.hotel_agent import create_hotel_agent
    from goa_travel_agent.src.agents.discovery_agent import create_discovery_agent
    from goa_travel_agent.src.agents.planner_agent import create_planner_agent
    from goa_travel_agent.src.tools.budget_calculator import estimate_budget
    from goa_travel_agent.src.tools.itinerary_optimizer import optimize_itinerary

    # Create agents with stateless=False to maintain conversation history
    hotel_agent = create_hotel_agent(stateless=False)
    discovery_agent = create_discovery_agent(stateless=False)
    planner_agent = create_planner_agent(
        hotel_agent=hotel_agent,
        discovery_agent=discovery_agent,
        extra_tools=[estimate_budget, optimize_itinerary],
        stateless=False,
    )

    agents = {
        "1": ("Marco (Hotel Expert)", hotel_agent),
        "2": ("Priya (Discovery)", discovery_agent),
        "3": ("Raj (Planner)", planner_agent),
    }

    print("\n" + "=" * 60)
    print("  GOA TRAVEL AGENT — Interactive CLI")
    print("=" * 60)

    while True:
        print("\nSeleziona agente:")
        for k, (name, _) in agents.items():
            print(f"  [{k}] {name}")
        print("  [q] Esci")

        choice = input("\n> ").strip()
        if choice.lower() == "q":
            print("Arrivederci!")
            break
        if choice not in agents:
            print("Scelta non valida.")
            continue

        agent_name, agent = agents[choice]
        print(f"\nStai parlando con {agent_name}. Scrivi 'back' per cambiare agente.\n")

        while True:
            user_input = input(f"[Tu → {agent_name.split()[0]}] ").strip()
            if not user_input or user_input.lower() == "back":
                break

            try:
                result = agent.run(user_input)
                response = result.text if result else "Nessuna risposta."
            except Exception as e:
                response = f"Errore: {e}"

            print(f"\n[{agent_name.split()[0]}]: {response}\n")


def main() -> None:
    args = sys.argv[1:]

    if "--ui" in args:
        # Launch Streamlit
        import subprocess

        app_path = Path(__file__).resolve().parent / "goa_travel_agent" / "ui" / "app.py"
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)], check=False)
        return

    # CLI pipeline
    print("=" * 60)
    print("  GOA TRAVEL AGENT — Pipeline")
    print("=" * 60)

    # Step 1
    print("\n[STEP 1] Data Pipeline")
    hotels_df, places_df = _run_data_pipeline()

    # Step 2
    print("\n[STEP 2] Embeddings + Qdrant")
    embedder = _run_embeddings(hotels_df, places_df)

    # Step 3
    print("\n[STEP 3] Search Demo")
    searcher = _run_search_demo(embedder)

    # Step 4-5: Interactive CLI
    print("\n[STEP 4-5] Interactive Agent CLI")
    _run_cli(searcher)


if __name__ == "__main__":
    main()
