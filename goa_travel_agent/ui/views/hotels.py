import streamlit as st

from goa_travel_agent.ui.components.hotel_cards import render_hotel_results
from goa_travel_agent.ui.components.sidebar import render_sidebar


def render(searcher) -> None:
    st.header("🏨 Cerca Hotel a Goa")

    filters = render_sidebar()

    query = st.text_input(
        "Descrivi il tuo hotel ideale...",
        placeholder="es. luxury resort con piscina vicino alla spiaggia di Candolim",
    )

    locality = st.text_input("📍 Localita (opzionale)", "", placeholder="es. Candolim, Baga, Panjim")

    if st.button("🔍 Cerca Hotel", use_container_width=True):
        if not query:
            st.warning("Inserisci una descrizione per la ricerca.")
            return

        with st.spinner("Ricerca in corso..."):
            results = searcher.search_hotels(
                query=query,
                min_stars=float(filters["hotel_stars"]),
                min_rating=float(filters["min_rating"]),
                locality=locality or None,
                top_k=5,
            )
            st.session_state["hotel_results"] = results

    if "hotel_results" in st.session_state:
        render_hotel_results(st.session_state["hotel_results"])
