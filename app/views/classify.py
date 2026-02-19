import streamlit as st
from app.core.classifier import classify
from app.data.database import save_classification, save_feedback


def confidence_badge(score: float) -> tuple:
    if score >= 0.85:
        return "🟢", "Haute confiance"
    elif score >= 0.65:
        return "🟡", "Confiance modérée"
    else:
        return "🔴", "Incertain"


def render_classify():
    st.header("Classifier un message client")

    text = st.text_area(
        "Message à analyser",
        placeholder="Collez ou tapez le message client ici...",
        height=120
    )

    if st.button("Classifier", type="primary", disabled=not text):
        with st.spinner("Analyse en cours..."):
            result = classify(text)
            classif_id = save_classification(result)
            st.session_state.classif_id = classif_id
            st.session_state.result = result
            st.session_state.show_correction = False

    if "result" in st.session_state and st.session_state.result:
        result = st.session_state.result
        classif_id = st.session_state.classif_id

        st.divider()

        # Catégorie + badge confiance
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {result.category_name.upper()}")
            st.progress(result.confidence)
        with col2:
            emoji, label = confidence_badge(result.confidence)
            st.markdown(f"## {emoji}")
            st.caption(f"{int(result.confidence * 100)}% — {label}")

        # Avertissement confiance faible
        if result.needs_review:
            st.warning("Confiance faible — vérification recommandée")

        # Facteurs clés
        if result.key_factors:
            st.markdown("**Facteurs déterminants :**")
            cols = st.columns(len(result.key_factors))
            for col, factor in zip(cols, result.key_factors):
                col.markdown(
                    f"<span style='background:#e8f4f8; color:#1a1a1a; padding:4px 10px;"
                    f"border-radius:12px; font-size:0.85em'>🔍 {factor}</span>",
                    unsafe_allow_html=True
                )

        st.divider()

        # Comparaison message / définition
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Votre message**")
            st.info(f'"{text}"')
        with col2:
            st.markdown("**Pourquoi cette catégorie**")
            st.info(result.category_name)

        # Raisonnement dépliable
        with st.expander("🧠 Voir le raisonnement complet"):
            st.write(result.reasoning)
            if result.alternative_category:
                st.info(
                    f"Le système a hésité avec : **{result.alternative_category_name}**"
                )
                if st.button(f"↩️ C'est plutôt : {result.alternative_category_name}"):
                    save_feedback(classif_id, "WRONG", result.alternative_category)
                    st.success("Correction enregistrée !")

        st.divider()
        st.markdown("**Cette classification est-elle correcte ?**")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("👍 Correct"):
                save_feedback(classif_id, "CORRECT", None)
                st.success("Merci !")
        with col2:
            if st.button("👎 Incorrect"):
                st.session_state.show_correction = True
        with col3:
            if st.button("🤔 Ambigu"):
                save_feedback(classif_id, "UNCERTAIN", None)
                st.info("Signalé.")

        if st.session_state.get("show_correction"):
            import yaml
            categories = yaml.safe_load(open("config/categories.yaml"))["categories"]
            correct_label = st.selectbox(
                "Quelle est la bonne catégorie ?",
                options=[(c["id"], c["name"]) for c in categories],
                format_func=lambda x: x[1]
            )
            if st.button("Confirmer la correction"):
                save_feedback(classif_id, "WRONG", correct_label[0])
                st.success("Correction enregistrée !")
                st.session_state.show_correction = False
