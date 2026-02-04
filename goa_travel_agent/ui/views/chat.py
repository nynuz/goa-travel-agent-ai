import streamlit as st

from goa_travel_agent.ui.components.chat_interface import (
    add_message,
    init_chat_state,
    render_agent_selector,
    render_messages,
    render_quick_actions,
)


def render(agents: dict) -> None:
    # Title row with clear button
    title_col, btn_col = st.columns([6, 1])
    with title_col:
        st.header("💬 Chat con AI")
    with btn_col:
        st.markdown("")
        if st.session_state.get("messages"):
            if st.button("🗑️ Cancella", key="clear_chat"):
                st.session_state.messages = []
                # Reset agent memories by clearing cache
                st.cache_resource.clear()
                st.rerun()

    init_chat_state()

    current_agent_name = render_agent_selector()
    st.caption(f"Stai parlando con **{current_agent_name}**")

    # Per-agent quick actions
    st.markdown("")
    quick_action = render_quick_actions(current_agent_name)
    if quick_action:
        st.session_state["_pending_msg"] = quick_action

    st.markdown("---")

    render_messages()

    # Chat input
    user_input = st.chat_input("Scrivi un messaggio...")

    # Check pending from quick actions
    if "_pending_msg" in st.session_state:
        user_input = st.session_state.pop("_pending_msg")

    if user_input:
        add_message("user", user_input)

        agent = agents.get(current_agent_name.lower())
        if agent is None:
            agent = agents.get("planner")  # fallback

        if agent is None:
            add_message("assistant", "Agente non disponibile. Verifica le API keys.", current_agent_name)
            st.rerun()
            return

        # Check if agent switched: provide conversation context
        last_agent = None
        if len(st.session_state.messages) >= 2:
            # Get previous assistant message to detect agent switch
            for msg in reversed(st.session_state.messages[:-1]):  # Exclude current user msg
                if msg["role"] == "assistant":
                    last_agent = msg.get("agent", "")
                    break

        # If agent switched, prepend context summary
        agent_input = user_input
        if last_agent and last_agent != current_agent_name:
            # Build context from recent conversation
            context_messages = []
            for msg in st.session_state.messages[-6:-1]:  # Last 5 messages before current
                role = "Utente" if msg["role"] == "user" else msg.get("agent", "Assistente")
                context_messages.append(f"{role}: {msg['content'][:150]}...")

            if context_messages:
                context_summary = "\n".join(context_messages)
                agent_input = f"""[CONTESTO CONVERSAZIONE PRECEDENTE]
{context_summary}

[DOMANDA ATTUALE DELL'UTENTE]
{user_input}

Nota: L'utente ha cambiato agente da {last_agent} a te. Usa il contesto precedente per comprendere la situazione e fornire una risposta pertinente."""

        with st.spinner(f"{current_agent_name} sta scrivendo..."):
            try:
                result = agent.run(agent_input)
                response = result.text if result else "Nessuna risposta."
            except Exception as e:
                response = f"Errore: {e}"

        add_message("assistant", response, current_agent_name)
        st.rerun()
