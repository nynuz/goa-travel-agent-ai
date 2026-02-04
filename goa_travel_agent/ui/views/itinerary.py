import streamlit as st


def _render_step_indicator(current_step: int) -> None:
    """Render a 3-step progress indicator (1-indexed)."""
    steps = [
        (1, "Configura"),
        (2, "Genera"),
        (3, "Risultato"),
    ]
    html_parts = []
    for i, (num, label) in enumerate(steps):
        if num < current_step:
            cls = "step step-done"
            line_cls = "step-line step-line-done"
        elif num == current_step:
            cls = "step step-active"
            line_cls = "step-line"
        else:
            cls = "step"
            line_cls = "step-line"

        html_parts.append(
            f'<div class="{cls}">'
            f'<div class="step-circle">{num}</div>'
            f'<span class="step-label">{label}</span>'
            f'</div>'
        )
        if i < len(steps) - 1:
            html_parts.append(f'<div class="{line_cls}"></div>')

    st.markdown(
        f'<div class="step-indicator">{"".join(html_parts)}</div>',
        unsafe_allow_html=True,
    )


def render(agents: dict) -> None:
    st.header("📅 Crea Itinerario")

    has_result = "itinerary_result" in st.session_state
    current_step = 3 if has_result else 1
    _render_step_indicator(current_step)

    # --- Configuration form ---
    with st.expander("🧳 Dettagli Viaggio", expanded=not has_result):
        col1, col2 = st.columns(2)
        with col1:
            num_days = st.number_input("Durata viaggio (giorni)", min_value=1, max_value=14, value=4, key="itin_days")
            trip_type = st.selectbox("Tipo gruppo", ["Solo", "Coppia", "Famiglia", "Amici"], key="itin_trip")
        with col2:
            hotel_stars = st.selectbox("Stelle hotel", [3, 4, 5], index=1, key="itin_stars")
            style = st.selectbox("Stile viaggio", ["budget", "moderate", "luxury"], index=1, key="itin_style")

    with st.expander("🎯 Preferenze", expanded=not has_result):
        interests = st.multiselect(
            "Interessi principali",
            ["Beach", "Nightlife", "Culture", "Adventure", "Food", "Wellness"],
            default=["Beach", "Culture"],
            key="itin_interests",
        )
        pace = st.slider("Ritmo", 1, 5, 3, help="1 = Molto rilassato, 5 = Molto intenso", key="itin_pace")
        locality_pref = st.text_input("Zona preferita (opzionale)", placeholder="es. Candolim, Baga", key="itin_zone")

    # --- Generate button ---
    if st.button("🗓️ Genera Itinerario", use_container_width=True):
        planner = agents.get("planner")
        if planner is None:
            st.error("Agente planner non disponibile. Verifica le API keys.")
            return

        prompt_parts = [
            f"Pianifica un viaggio a Goa di {num_days} giorni.",
            f"Tipo viaggiatore: {trip_type}.",
            f"Hotel preferito: {hotel_stars} stelle, stile {style}.",
            f"Interessi: {', '.join(interests)}.",
            f"Ritmo: {'rilassato' if pace <= 2 else 'moderato' if pace <= 3 else 'intenso'}.",
        ]
        if locality_pref:
            prompt_parts.append(f"Zona preferita: {locality_pref}.")

        prompt = " ".join(prompt_parts)
        st.session_state["itinerary_prompt"] = prompt

        with st.spinner("Raj sta creando il tuo itinerario..."):
            try:
                result = planner.run(prompt)
                response_text = result.text if result else "Nessuna risposta dall'agente."
            except Exception as e:
                response_text = f"Errore nella generazione: {e}"

        st.session_state["itinerary_result"] = response_text
        st.rerun()

    # --- Result display ---
    if has_result:
        st.markdown("---")
        st.subheader("Il Tuo Itinerario")
        st.markdown(
            f'<div class="itinerary-result">{st.session_state["itinerary_result"]}</div>',
            unsafe_allow_html=True,
        )

        col_a, col_b = st.columns(2)
        with col_a:
            st.download_button(
                "📥 Scarica Itinerario",
                data=st.session_state["itinerary_result"],
                file_name="itinerario_goa.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with col_b:
            if st.button("🔄 Modifica e Rigenera", use_container_width=True):
                del st.session_state["itinerary_result"]
                st.rerun()
