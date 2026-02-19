import streamlit as st
from app.data.database import init_db

st.set_page_config(
    page_title="Classifier Support Client",
    page_icon="💬",
    layout="wide"
)

init_db()

tab1, tab2, tab3 = st.tabs(["Classification", "Historique", "Admin"])

with tab1:
    from app.views.classify import render_classify
    render_classify()

with tab2:
    from app.views.history import render_history
    render_history()

with tab3:
    from app.views.admin import render_admin
    render_admin()
