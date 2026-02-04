import streamlit as st

from goa_travel_agent.ui.components.places_grid import render_places_grid


CATEGORIES = [
    ("Tutti", ""),
    ("🏖️ Beach", "Beach"),
    ("🎉 Nightlife", "Nightlife"),
    ("🛕 Culture", "Culture"),
    ("🏄 Adventure", "Adventure"),
    ("🧘 Wellness", "Wellness"),
    ("🍛 Food", "Food"),
]


def render(searcher) -> None:
    st.header("🗺️ Scopri Luoghi a Goa")

    # Category pill selector
    if "places_category" not in st.session_state:
        st.session_state.places_category = ""

    cat_labels = [label for label, _ in CATEGORIES]
    cat_values = [val for _, val in CATEGORIES]

    selected_label = st.radio(
        "Categoria",
        cat_labels,
        horizontal=True,
        label_visibility="collapsed",
        key="places_cat_radio",
    )
    selected_cat = cat_values[cat_labels.index(selected_label)]

    st.markdown("")

    query = st.text_input(
        "Cosa vuoi fare a Goa?",
        placeholder="es. romantic sunset point, water sports, local food market",
        key="places_query_main",
    )

    if st.button("🔍 Cerca", key="places_btn_main", use_container_width=True):
        if not query:
            st.warning("Inserisci una query di ricerca.")
            return

        with st.spinner("Ricerca in corso..."):
            results = searcher.search_places(
                query=query,
                category=selected_cat or None,
                top_k=6,
            )
            st.session_state["places_results"] = results

    if "places_results" in st.session_state:
        render_places_grid(st.session_state["places_results"])
