import streamlit as st


BADGE_MAP = {
    "Beach": "badge-beach",
    "Nightlife": "badge-nightlife",
    "Culture": "badge-culture",
    "Adventure": "badge-adventure",
    "Wellness": "badge-wellness",
    "Food": "badge-food",
}


def _category_badges(category: str) -> str:
    badges = []
    for cat in category.split(", "):
        css_class = BADGE_MAP.get(cat.strip(), "")
        if css_class:
            badges.append(f'<span class="category-badge {css_class}">{cat.strip()}</span>')
    return " ".join(badges) if badges else f'<span class="category-badge">{category}</span>'


def _rating_dots(rating: float, max_dots: int = 5) -> str:
    """Generate HTML for visual rating dots."""
    filled = int(round(rating))
    dots = []
    for i in range(max_dots):
        cls = "rating-dot rating-dot-filled" if i < filled else "rating-dot"
        dots.append(f'<span class="{cls}"></span>')
    return f'<div class="rating-visual">{"".join(dots)}</div>'


def render_place_card(place: dict, show_full_review: bool = False) -> None:
    name = place.get("place", "N/A")
    city = place.get("city", "")
    category = place.get("category", "General")
    review = str(place.get("review", ""))
    rating = float(place.get("rating", 0) or 0)

    short_review = review[:150] + "..." if len(review) > 150 else review

    st.markdown(
        f"""
        <div class="place-card">
            <h4>{name}</h4>
            <p>📍 {city.title()}</p>
            {_category_badges(category)}
            {_rating_dots(rating) if rating > 0 else ''}
            <p class="review-text" style="margin-top:0.5rem;">{short_review}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if len(review) > 150:
        with st.expander("Mostra di piu"):
            st.markdown(f'<p class="review-text">{review}</p>', unsafe_allow_html=True)


def render_places_grid(results: list[dict]) -> None:
    if not results:
        st.markdown(
            '<div class="empty-state">'
            '<span class="empty-icon">🗺️</span>'
            '<h3>Nessun luogo trovato</h3>'
            '<p>Prova con una query diversa o una categoria differente</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown(f"**Trovati {len(results)} luoghi**")
    cols = st.columns(2)
    for i, place in enumerate(results):
        with cols[i % 2]:
            render_place_card(place)
