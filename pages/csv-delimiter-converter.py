import streamlit as st
import pandas as pd
import io

def detect_encoding(file):
    # Try to decode with utf-8 first, then fallback to latin-1
    try:
        file.read().decode('utf-8')
        file.seek(0)
        return 'utf-8'
    except UnicodeDecodeError:
        file.seek(0)
        return 'latin-1'

def convert_csv(input_file):
    try:
        # Detect the file encoding
        encoding = detect_encoding(input_file)
        
        # Read the input CSV file with automatic delimiter detection
        df = pd.read_csv(input_file, encoding=encoding, sep=None, engine='python')
        
        # Convert the DataFrame to a comma-delimited CSV
        output = io.StringIO()
        df.to_csv(output, index=False, sep=',')
        return output.getvalue(), None
    except Exception as e:
        return None, str(e)

st.title("CSV Delimiter Converter")

st.markdown("Deze tool converteert een CSV-bestand naar een komma-gescheiden CSV, ongeacht het oorspronkelijke scheidingsteken.")

uploaded_file = st.file_uploader("Upload een CSV-bestand", type="csv")

if uploaded_file is not None:
    # Convert the uploaded file
    converted_csv, error = convert_csv(uploaded_file)
    
    if error:
        st.error(f"Er is een fout opgetreden: {error}")
    elif converted_csv:
        # Provide a download button for the converted CSV
        st.download_button(
            label="Download Geconverteerde CSV",
            data=converted_csv,
            file_name="converted_comma_delimited.csv",
            mime="text/csv"
        )
    else:
        st.warning("Er is iets misgegaan bij het converteren van het bestand. Probeer het opnieuw.")
