import streamlit as st

AGENTS = {
    "Marco": ("🏨", "Hotel Expert", "Esperto di hotel e alloggi a Goa"),
    "Priya": ("🗺️", "Discovery", "Specialista in attrazioni e luoghi"),
    "Raj": ("📅", "Planner", "Pianificatore di itinerari e budget"),
}

AGENT_COLORS = {
    "Marco": "marco",
    "Priya": "priya",
    "Raj": "raj",
}

AGENT_QUICK_ACTIONS = {
    "Marco": [
        ("🏖️", "Hotel vicino alla spiaggia di Baga"),
        ("💎", "Resort lusso con piscina e spa"),
        ("💰", "Hotel economico a Panjim"),
        ("👨‍👩‍👧‍👦", "Hotel famiglia con camere grandi"),
    ],
    "Priya": [
        ("🌅", "Migliori tramonti a Goa"),
        ("🛕", "Chiese e templi storici"),
        ("🍛", "Mercati locali e street food"),
        ("🏄", "Attivita e sport acquatici"),
    ],
    "Raj": [
        ("💑", "Weekend romantico a Goa"),
        ("📅", "Itinerario 5 giorni con budget medio"),
        ("🎉", "3 giorni tra spiagge e nightlife"),
        ("👨‍👩‍👧‍👦", "Vacanza famiglia 7 giorni relax"),
    ],
}


def init_chat_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_agent" not in st.session_state:
        st.session_state.current_agent = "Raj"


def render_agent_selector() -> str:
    cols = st.columns(3)
    current = st.session_state.current_agent

    for col, (name, (icon, title, desc)) in zip(cols, AGENTS.items()):
        with col:
            active_cls = f"agent-card-active agent-card-{AGENT_COLORS[name]}" if name == current else ""
            st.markdown(
                f'<div class="agent-card {active_cls}">'
                f'<span class="agent-avatar">{icon}</span>'
                f'<div class="agent-name">{name}</div>'
                f'<div class="agent-desc">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown("")  # spacing between card and button
            if st.button(f"Seleziona {name}", key=f"agent_{name}", use_container_width=True):
                st.session_state.current_agent = name
                st.rerun()

    return st.session_state.current_agent


def render_quick_actions(agent_name: str) -> str | None:
    """Render per-agent quick action buttons. Returns selected action or None."""
    actions = AGENT_QUICK_ACTIONS.get(agent_name, [])
    if not actions:
        return None

    cols = st.columns(len(actions))
    for col, (icon, action) in zip(cols, actions):
        with col:
            if st.button(f"{icon} {action}", key=f"qa_{agent_name}_{action}", use_container_width=True):
                return action
    return None


def render_messages() -> None:
    agent_icons = {name: icon for name, (icon, _, _) in AGENTS.items()}

    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        agent = msg.get("agent", "")

        if role == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(content)
        else:
            avatar = agent_icons.get(agent, "🤖")
            with st.chat_message("assistant", avatar=avatar):
                if agent:
                    st.markdown(f"**{agent}**")
                st.markdown(content)


def render_typing_indicator() -> None:
    st.markdown(
        '<div class="typing-indicator">'
        '<span></span><span></span><span></span>'
        '</div>',
        unsafe_allow_html=True,
    )


def add_message(role: str, content: str, agent: str = "") -> None:
    st.session_state.messages.append(
        {"role": role, "content": content, "agent": agent}
    )
