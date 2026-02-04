import streamlit as st


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1>Pianifica il Tuo Viaggio da Sogno a Goa</h1>
            <p>Assistente AI con 15 anni di esperienza locale</p>
            <p class="hero-subtitle">Ricerca ibrida intelligente, 3 agenti AI specializzati, itinerari ottimizzati</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stats(num_hotels: int, num_places: int) -> None:
    cols = st.columns(3)
    items = [
        (f"{num_hotels}+", "Hotel Verificati"),
        (f"{num_places}+", "Attrazioni Curate"),
        ("3", "Agenti AI Esperti"),
    ]
    for col, (value, label) in zip(cols, items):
        with col:
            st.markdown(
                f'<div class="metric-card fade-in">'
                f'<div class="metric-value">{value}</div>'
                f'<div class="metric-label">{label}</div></div>',
                unsafe_allow_html=True,
            )


def render_how_it_works() -> None:
    st.markdown("### Come Funziona")
    cols = st.columns(3)
    steps = [
        ("🔍", "Ricerca Intelligente", "Ricerca ibrida densa + sparsa con reranking per trovare esattamente quello che cerchi"),
        ("🤖", "Agenti AI Esperti", "3 agenti specializzati: Marco (hotel), Priya (luoghi), Raj (itinerari)"),
        ("📅", "Itinerario Ottimizzato", "Pianificazione automatica con ottimizzazione geografica e budget"),
    ]
    for i, (col, (icon, title, desc)) in enumerate(zip(cols, steps)):
        with col:
            st.markdown(
                f'<div class="how-card fade-in fade-in-delay-{i + 1}">'
                f'<span class="how-icon">{icon}</span>'
                f'<h4>{title}</h4>'
                f'<p>{desc}</p></div>',
                unsafe_allow_html=True,
            )


def _navigate_to(nav_target: str) -> None:
    """Set nav state and rerun to switch page."""
    st.session_state._pending_nav = nav_target
    st.rerun()


def render_quick_start() -> None:
    st.markdown("### Inizia Subito")
    cols = st.columns(3)
    cards = [
        ("🏨", "Cerca Hotel", "Trova l'hotel perfetto con ricerca AI", "🏨 Hotel"),
        ("🗺️", "Esplora Luoghi", "Scopri le attrazioni di Goa", "🗺️ Luoghi"),
        ("📅", "Crea Itinerario", "Pianifica il viaggio ideale", "📅 Itinerario"),
    ]
    for i, (col, (icon, title, desc, nav_target)) in enumerate(zip(cols, cards)):
        with col:
            st.markdown(
                f'<div class="feature-card fade-in fade-in-delay-{i + 1}">'
                f'<span class="feature-icon">{icon}</span>'
                f'<h3>{title}</h3>'
                f'<p>{desc}</p></div>',
                unsafe_allow_html=True,
            )
            st.markdown("")  # spacing between card and button
            if st.button(f"Vai a {title}", key=f"home_cta_{nav_target}", use_container_width=True):
                _navigate_to(nav_target)
