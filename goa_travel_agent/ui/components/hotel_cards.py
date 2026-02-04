import streamlit as st


def _score_bar(score: float | None) -> str:
    """Return HTML for a visual score bar (0-1 range)."""
    if score is None:
        return ""
    pct = min(max(score * 100, 0), 100)
    return (
        f'<div class="score-bar-track">'
        f'<div class="score-bar-fill" style="width:{pct:.0f}%"></div>'
        f'</div>'
        f'<p><small>Relevance: {score:.3f}</small></p>'
    )


def render_hotel_card(hotel: dict) -> None:
    """Render a single hotel card with two-column layout."""
    name = hotel.get("property_name", "N/A")
    stars = hotel.get("hotel_star_rating", 0)
    rating = hotel.get("site_review_rating", 0)
    reviews = hotel.get("site_review_count", 0)
    locality = hotel.get("locality", "")
    facilities = hotel.get("hotel_facilities", "N/A")
    room = hotel.get("room_type", "")
    score = hotel.get("rerank_score")

    star_str = "★" * int(float(stars)) + "☆" * (5 - int(float(stars)))
    facilities_str = str(facilities)

    col_info, col_details = st.columns([3, 2])

    with col_info:
        st.markdown(
            f"""
            <div class="hotel-card">
                <h3>{name} <span class="star-rating">{star_str}</span></h3>
                <p>📍 {locality}, Goa</p>
                <p>⭐ {rating}/5 ({reviews} recensioni)</p>
                <p>🛏️ {room}</p>
                {_score_bar(score)}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_details:
        st.markdown(
            f"""
            <div class="hotel-card">
                <h4>Servizi</h4>
                <p>🏊 {facilities_str[:200]}{'...' if len(facilities_str) > 200 else ''}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_hotel_results(results: list[dict], sort_by: str = "relevance") -> None:
    """Render a list of hotel results with sorting."""
    if not results:
        st.markdown(
            '<div class="empty-state">'
            '<span class="empty-icon">🏨</span>'
            '<h3>Nessun hotel trovato</h3>'
            '<p>Prova con criteri diversi o una descrizione piu ampia</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown(f"**Trovati {len(results)} hotel**")

    # Sorting
    sort_option = st.selectbox(
        "Ordina per",
        ["Relevance", "Rating", "Stelle"],
        index=["Relevance", "Rating", "Stelle"].index(
            sort_by.capitalize() if sort_by.capitalize() in ["Relevance", "Rating", "Stelle"] else "Relevance"
        ),
        key="hotel_sort",
    )
    if sort_option == "Rating":
        results = sorted(results, key=lambda x: float(x.get("site_review_rating", 0)), reverse=True)
    elif sort_option == "Stelle":
        results = sorted(results, key=lambda x: float(x.get("hotel_star_rating", 0)), reverse=True)

    for hotel in results:
        render_hotel_card(hotel)
