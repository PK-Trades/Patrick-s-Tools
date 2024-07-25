import streamlit as st
import pandas as pd
import io

def convert_csv(input_file):
    # Read the input CSV file with semicolon delimiter
    df = pd.read_csv(input_file, sep=';')
    
    # Convert the DataFrame to a comma-delimited CSV
    output = io.StringIO()
    df.to_csv(output, index=False, sep=',')
    return output.getvalue()

st.title("CSV Delimiter Converter")

st.markdown("Deze tool maakt van een ; gescheiden CSV een , gescheiden CSV")

uploaded_file = st.file_uploader("Upload a semicolon-delimited CSV file", type="csv")

if uploaded_file is not None:
    # Convert the uploaded file
    converted_csv = convert_csv(uploaded_file)
    
    # Provide a download button for the converted CSV
    st.download_button(
        label="Download Converted CSV",
        data=converted_csv,
        file_name="converted_comma_delimited.csv",
        mime="text/csv"
    )
