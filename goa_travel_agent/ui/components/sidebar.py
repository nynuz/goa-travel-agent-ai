import streamlit as st


def render_sidebar() -> dict:
    """Render the global sidebar filters. Returns filter values."""
    st.sidebar.markdown(
        '<div style="text-align:center; padding: 0.5rem 0 1rem;">'
        '<span style="font-size:1.8rem;">🌴</span><br>'
        '<span style="color:#E8E8E8; font-weight:700; font-size:1.1rem;">Goa Travel Agent</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")

    # --- Budget ---
    st.sidebar.markdown("##### 💰 Budget")
    budget = st.sidebar.slider(
        "Budget Giornaliero (Rs.)", 1000, 20000, (3000, 10000), step=500
    )

    st.sidebar.markdown("---")

    # --- Trip details ---
    st.sidebar.markdown("##### 🧳 Dettagli Viaggio")
    trip_type = st.sidebar.selectbox(
        "Tipo Viaggio", ["Solo", "Coppia", "Famiglia", "Amici"], index=1
    )
    hotel_stars = st.sidebar.slider("Stelle Hotel (min)", 1, 5, 3)
    min_rating = st.sidebar.selectbox(
        "⭐ Rating minimo", [0.0, 3.0, 3.5, 4.0, 4.5], index=0
    )

    st.sidebar.markdown("---")

    # --- Interests ---
    st.sidebar.markdown("##### 🎯 Interessi")
    interests = []
    if st.sidebar.checkbox("🏖️ Relax in Spiaggia", value=True):
        interests.append("Beach")
    if st.sidebar.checkbox("🎉 Nightlife & Party"):
        interests.append("Nightlife")
    if st.sidebar.checkbox("🛕 Cultura & Storia"):
        interests.append("Culture")
    if st.sidebar.checkbox("🏄 Avventura & Sport"):
        interests.append("Adventure")
    if st.sidebar.checkbox("🍛 Food & Gastronomia"):
        interests.append("Food")
    if st.sidebar.checkbox("🧘 Wellness & Spa"):
        interests.append("Wellness")

    st.sidebar.markdown("---")

    # Reset button
    if st.sidebar.button("🔄 Reset Filtri", use_container_width=True):
        st.rerun()

    return {
        "budget_min": budget[0],
        "budget_max": budget[1],
        "trip_type": trip_type,
        "hotel_stars": hotel_stars,
        "min_rating": min_rating,
        "interests": interests,
    }
