import streamlit as st
import json
from app.data.database import get_history


def render_history():
    st.header("Historique des classifications")

    history = get_history(limit=50)

    if not history:
        st.info("Aucune classification pour le moment.")
        return

    feedback_icons = {
        "CORRECT": "👍",
        "WRONG": "👎",
        "UNCERTAIN": "🤔",
        None: "—"
    }

    for entry in history:
        key_factors = json.loads(entry["key_factors"]) if entry["key_factors"] else []
        icon = feedback_icons.get(entry["feedback_type"], "—")
        label = f"{entry['category_name']} — {entry['text'][:50]}..."

        with st.expander(f"{icon} {label}"):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(entry["text"])
                if key_factors:
                    st.caption(" · ".join(key_factors))
            with col2:
                st.metric("Confiance", f"{int(entry['confidence'] * 100)}%")
            with col3:
                st.markdown(f"**Feedback**")
                st.write(icon)
