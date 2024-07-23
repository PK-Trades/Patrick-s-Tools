import streamlit as st
import pandas as pd
import plotly.express as px

st.title('Minimal Trade Journal with Plot')

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write(df)

    # Create a simple line plot
    fig = px.line(df, x=df.index, y='Net P/L', title='Net P/L Over Time')
    st.plotly_chart(fig)
