"""Streamlit entry point for the Goa Travel Agent."""

from pathlib import Path

import streamlit as st

# -- Page config (must be first Streamlit call) --
st.set_page_config(
    page_title="Goa Travel Agent AI",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -- Load custom CSS --
_css_path = Path(__file__).parent / "styles" / "custom.css"
if _css_path.exists():
    st.markdown(f"<style>{_css_path.read_text()}</style>", unsafe_allow_html=True)


def _ensure_data_pipeline():
    """Run data download + preprocessing + embeddings + Qdrant upload if needed."""
    import pandas as pd

    from goa_travel_agent.config.settings import settings
    from goa_travel_agent.src.utils.logger import get_logger

    log = get_logger("ui.init")

    # --- Step 1: Data pipeline ---
    if settings.HOTELS_CSV.exists() and settings.PLACES_CSV.exists():
        log.info("Processed CSVs found, loading...")
        hotels_df = pd.read_csv(settings.HOTELS_CSV)
        places_df = pd.read_csv(settings.PLACES_CSV)
    else:
        log.info("Processed CSVs not found, running data pipeline...")
        from goa_travel_agent.src.data_management.kaggle_downloader import download_all
        from goa_travel_agent.src.data_management.data_loader import load_hotels_csv, load_places_csv
        from goa_travel_agent.src.data_management.preprocessor import (
            preprocess_hotels,
            preprocess_places,
            save_processed,
        )

        hotels_dir, places_dir = download_all()
        raw_hotels = load_hotels_csv(hotels_dir)
        raw_places = load_places_csv(places_dir)
        hotels_df = preprocess_hotels(raw_hotels)
        places_df = preprocess_places(raw_places)
        save_processed(hotels_df, places_df)

    # --- Step 2: Embeddings + Qdrant ---
    from goa_travel_agent.src.embeddings.hybrid_embedder import HybridEmbedder
    from goa_travel_agent.src.vector_db.qdrant_manager import QdrantManager

    embedder = HybridEmbedder()
    if not embedder.is_tfidf_fitted():
        log.info("Fitting TF-IDF on full corpus...")
        corpus = hotels_df["search_text"].tolist() + places_df["full_text"].tolist()
        embedder.fit_tfidf(corpus)
    else:
        embedder.load_tfidf()

    if settings.QDRANT_URL:
        manager = QdrantManager()
        if not manager.collection_exists_and_populated(settings.HOTELS_COLLECTION):
            log.info("Uploading hotels to Qdrant...")
            manager.setup_hotels_collection(hotels_df, embedder)
        if not manager.collection_exists_and_populated(settings.PLACES_COLLECTION):
            log.info("Uploading places to Qdrant...")
            manager.setup_places_collection(places_df, embedder)

    return embedder, len(hotels_df), len(places_df)


@st.cache_resource
def _init_backend():
    """Initialize embedder, searcher, and agents (cached across reruns)."""
    from goa_travel_agent.config.settings import settings
    from goa_travel_agent.src.vector_db.searcher import HybridSearcher
    from goa_travel_agent.src.tools import hotel_search as hs_mod
    from goa_travel_agent.src.tools import places_search as ps_mod

    embedder, num_hotels, num_places = _ensure_data_pipeline()

    searcher = HybridSearcher(embedder=embedder)

    # Wire searcher into tool modules
    hs_mod.set_searcher(searcher)
    ps_mod.set_searcher(searcher)

    # Load agents
    agents = {}
    if settings.OPENAI_API_KEY:
        from goa_travel_agent.src.agents.hotel_agent import create_hotel_agent
        from goa_travel_agent.src.agents.discovery_agent import create_discovery_agent
        from goa_travel_agent.src.agents.planner_agent import create_planner_agent
        from goa_travel_agent.src.tools.budget_calculator import estimate_budget
        from goa_travel_agent.src.tools.itinerary_optimizer import optimize_itinerary

        # Create agents with stateless=False to maintain conversation history
        # NOTE: These agents are cached globally, but conversation state
        # is managed per-session in Streamlit session_state
        hotel_agent = create_hotel_agent(stateless=False)
        discovery_agent = create_discovery_agent(stateless=False)
        planner_agent = create_planner_agent(
            hotel_agent=hotel_agent,
            discovery_agent=discovery_agent,
            extra_tools=[estimate_budget, optimize_itinerary],
            stateless=False,
        )
        agents = {
            "marco": hotel_agent,
            "priya": discovery_agent,
            "raj": planner_agent,
            "planner": planner_agent,
        }

    return searcher, agents, num_hotels, num_places


PAGE_OPTIONS = [
    "🏠 Home",
    "🏨 Hotel",
    "🗺️ Luoghi",
    "📅 Itinerario",
    "💬 Chat AI",
]


def _render_home(num_hotels: int, num_places: int) -> None:
    from goa_travel_agent.ui.components.header import render_hero, render_stats, render_how_it_works, render_quick_start

    render_hero()
    render_stats(num_hotels, num_places)

    st.markdown("")
    render_how_it_works()

    st.markdown("")
    render_quick_start()


def main() -> None:
    searcher, agents, num_hotels, num_places = _init_backend()

    # -- Handle pending navigation from CTA buttons (before widget creation) --
    if "_pending_nav" in st.session_state:
        target = st.session_state.pop("_pending_nav")
        st.session_state.nav_page = target
        st.session_state.nav_radio = target  # set widget key BEFORE it's instantiated
    elif "nav_page" not in st.session_state:
        st.session_state.nav_page = "🏠 Home"

    page = st.radio(
        "Navigazione",
        PAGE_OPTIONS,
        index=PAGE_OPTIONS.index(st.session_state.nav_page),
        horizontal=True,
        label_visibility="collapsed",
        key="nav_radio",
    )
    st.session_state.nav_page = page

    st.markdown("")

    if page == "🏠 Home":
        _render_home(num_hotels, num_places)

    elif page == "🏨 Hotel":
        from goa_travel_agent.ui.views.hotels import render
        render(searcher)

    elif page == "🗺️ Luoghi":
        from goa_travel_agent.ui.views.places import render
        render(searcher)

    elif page == "📅 Itinerario":
        from goa_travel_agent.ui.views.itinerary import render
        render(agents)

    elif page == "💬 Chat AI":
        from goa_travel_agent.ui.views.chat import render
        render(agents)


if __name__ == "__main__":
    main()
