import streamlit as st
from app.data.database import get_history, count_unused_wrong_feedbacks


def build_stats(history: list) -> dict:
    total = len(history)
    if total == 0:
        return {"total": 0, "feedback_rate": 0, "wrong_rate": 0, "avg_confidence": 0}

    with_feedback = sum(1 for h in history if h["feedback_type"] is not None)
    wrong = sum(1 for h in history if h["feedback_type"] == "WRONG")
    avg_conf = sum(h["confidence"] for h in history) / total

    return {
        "total": total,
        "feedback_rate": round(with_feedback / total * 100),
        "wrong_rate": round(wrong / total * 100),
        "avg_confidence": round(avg_conf * 100)
    }


def render_admin():
    st.header("Administration")

    tab1, tab2, tab3 = st.tabs(["Métriques", "Optimisation", "Évaluation"])

    history = get_history(limit=500)
    stats = build_stats(history)

    # ── Métriques ──
    with tab1:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Classifications totales", stats["total"])
        col2.metric("Taux de feedback", f"{stats['feedback_rate']}%")
        col3.metric("Taux de correction", f"{stats['wrong_rate']}%")
        col4.metric("Confiance moyenne", f"{stats['avg_confidence']}%")

        if history:
            st.subheader("Dernières classifications")
            for entry in history[:10]:
                fb = entry["feedback_type"] or "—"
                st.write(
                    f"`{entry['category_name']}` "
                    f"({int(entry['confidence']*100)}%) "
                    f"· feedback: {fb} "
                    f"· {entry['text'][:60]}..."
                )

    # ── Optimisation ──
    with tab2:
        pending = count_unused_wrong_feedbacks()
        st.metric("Feedbacks disponibles pour optimisation", pending)

        if pending >= 10:
            st.success("Seuil atteint — optimisation recommandée")
        else:
            st.info(f"Il faut {10 - pending} corrections supplémentaires pour optimiser")

        if st.button("Optimiser les exemples", type="primary", disabled=pending < 2):
            with st.spinner("Optimisation en cours..."):
                from app.feedback.optimizer import run_optimizer
                result = run_optimizer()
            if result:
                st.success(f"examples.json mis à jour (v{result['version']})")
                st.json(result["changelog"][-1])
            else:
                st.warning("Pas assez de feedbacks pour optimiser")

    # ── Évaluation ──
    with tab3:
        n = st.slider("Cas de test par catégorie", 5, 20, 10)
        st.caption(f"Soit {n * 6} cas de test au total")

        if st.button("Lancer l'évaluation", type="primary"):
             with st.spinner(f"Génération et évaluation de {n*6} cas... (peut prendre 1-2 min)"):
                 from app.evaluation.evaluator import run_evaluation
                 report = run_evaluation(n_per_category=n)

             col1, col2, col3 = st.columns(3)
             col1.metric("Accuracy globale", f"{report['strict_accuracy']*100:.1f}%")
             col2.metric("Cas difficiles", f"{report['hard_accuracy']*100:.1f}%")
             col3.metric("Cas testés", report["total_cases"])

             st.subheader("Détail par catégorie")
             for cat_id, metrics in report["by_category"].items():
                 col1, col2 = st.columns([3, 1])
                 with col1:
                    st.write(f"**{cat_id}**")
                    st.progress(metrics["accuracy"])
                 with col2:
                    acc = metrics["accuracy"] * 100
                    color = "🟢" if acc >= 80 else "🟡" if acc >= 65 else "🔴"
                    st.write(f"{color} {acc:.0f}%")

             if report["failed_cases"]:
                 st.subheader(f"{len(report['failed_cases'])} cas ratés")
                 for i, case in enumerate(report["failed_cases"]):
                     with st.expander(
                         f"❌ Attendu : {case['expected']} | "
                         f"Prédit : {case['predicted']} | "
                         f"{case['text'][:50]}..."
                     ):
                         st.markdown(f"**Message complet :**")
                         st.write(case["text"])
                         col1, col2 = st.columns(2)
                         with col1:
                             st.markdown(f"**Attendu :** `{case['expected']}`")
                             st.markdown(f"**Prédit :** `{case['predicted']}`")
                             st.markdown(f"**Difficulté :** `{case['difficulty']}`")
                         with col2:
                             st.markdown(f"**Confiance :** `{int(case['confidence']*100)}%`")
                             st.markdown(f"**Sévérité :** `{case['severity']}`")
                         st.markdown(f"**Jugement :** {case['judge_reasoning']}")
 
