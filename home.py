import streamlit as st

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
st.link_button("Content Pruning Tool", "https://patrick-seo-tools.streamlit.app/patrick-content-pruning")
)
