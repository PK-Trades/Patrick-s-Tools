import streamlit as st

st.set_page_config(
    page_title="Patrick's Tools",
    page_icon="👋",
    initial_sidebar_state="collapsed"
)

st.write("# Patrick's SEO Tools! 👋")

st.sidebar.success("Kies jouw tool hierboven.")

st.markdown(
    """
    Selecteer hieronder welke tool je wilt gebruiken.
    Of open de sidebar door op > linksboven te klikken.
    """
)

st.page_link("pages/patrick-content-pruning.py", label="##Content Pruning", icon="1️⃣")

st.page_link("pages/Patrick-merge-csv.py", label="##CSV Merge", icon="2️⃣")
