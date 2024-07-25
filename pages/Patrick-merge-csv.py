import pandas as pd
import streamlit as st
import csv
import io

def detect_delimiter(file):
    sample = file.read(1024).decode('utf-8')
    file.seek(0)
    sniffer = csv.Sniffer()
    dialect = sniffer.sniff(sample)
    return dialect.delimiter

def standardize_urls(df):
    df['URL'] = df['URL'].str.lower().str.strip()
    df['URL'] = df['URL'].str.replace('www.', '', regex=False)
    df['URL'] = df['URL'].str.rstrip('/')
    df['URL'] = df['URL'].apply(lambda x: 'https://' + x if not x.startswith('https://') else x)
    return df

def merge_csvs(file1, file2):
    # Detect delimiters
    delimiter1 = detect_delimiter(file1)
    delimiter2 = detect_delimiter(file2)

    # Read the CSV files with detected delimiters
    df1 = pd.read_csv(file1, sep=delimiter1, encoding='utf-8', index_col=False)
    df2 = pd.read_csv(file2, sep=delimiter2, encoding='utf-8', index_col=False)

    # Strip whitespace from column names
    df1.columns = df1.columns.str.strip()
    df2.columns = df2.columns.str.strip()

    # Ensure 'URL' column exists in both dataframes
    if 'URL' not in df1.columns or 'URL' not in df2.columns:
        st.error("Both CSV files must have a 'URL' column")
        return None

    # Standardize URLs
    df1 = standardize_urls(df1)
    df2 = standardize_urls(df2)

    # Merge the dataframes on the URL column
    merged_df = pd.merge(df1, df2, on='URL', how='inner')

    if merged_df.empty:
        st.warning("No matching URLs found between the two files.")
        return None

    # Drop the 'Unnamed: 3' column if it exists
    merged_df = merged_df.drop(columns=['Unnamed: 3'], errors='ignore')

    return merged_df

st.title("Patrick's CSV Merger")

file1 = st.file_uploader("Upload File 1", type="csv")
file2 = st.file_uploader("Upload File 2", type="csv")

if file1 and file2:
    if st.button("Merge CSVs"):
        merged_df = merge_csvs(file1, file2)
        if merged_df is not None:
            st.success(f"Files merged successfully! Rows: {merged_df.shape[0]}, Columns: {merged_df.shape[1]}")
            st.dataframe(merged_df.head())

st.markdown(":orange[*De tool laat na de merge slechts enkele URLs zien zodat je kunt controleren of de output zal klopt*]")

            # Provide download link for merged CSV
            csv = merged_df.to_csv(index=False)
            st.download_button(
                label="Download merged CSV",
                data=csv,
                file_name="merged_csv.csv",
                mime="text/csv"
            )
else:
    st.info("Please upload both CSV files to merge.")
