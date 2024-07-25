import streamlit as st

[client]
showSidebarNavigation = false

st.set_page_config(
    page_title="Patrick's Tools",
    page_icon="👋",
)

st.write("# Welcome to Your Combined App! 👋")

st.sidebar.success("Select a page above.")

st.markdown(
    """
    Selecteer in de sidebar welke tool je wilt gebruiken.
    """
)

st.page_link("pages/patrick-content-pruning.py", label="Content Pruning Tool", icon="1️⃣")

st.page_link("pages/Patrick-merge-csv.py", label="CSV Merge", icon="2️⃣")
