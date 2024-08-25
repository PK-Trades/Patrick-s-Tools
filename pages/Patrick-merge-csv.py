import streamlit as st
import pandas as pd
import csv
import io
import chardet
import re

def detect_encoding(file):
    raw_data = file.read()
    file.seek(0)  # Reset file pointer
    result = chardet.detect(raw_data)
    return result['encoding']

def detect_delimiter(file, encoding):
    sample = file.read(1024).decode(encoding)
    file.seek(0)  # Reset file pointer
    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(sample)
        return dialect.delimiter
    except:
        # If sniffer fails, try common delimiters
        for delimiter in [',', ';', '\t', '|']:
            try:
                pd.read_csv(io.StringIO(sample), sep=delimiter, nrows=5)
                return delimiter
            except:
                continue
    return ','  # Default to comma if no delimiter is detected

def read_csv_with_auto_detect(file):
    encoding = detect_encoding(file)
    delimiter = detect_delimiter(file, encoding)
    df = pd.read_csv(file, sep=delimiter, encoding=encoding, engine='python')
    return df

def standardize_url(url):
    url = url.lower().strip()
    url = re.sub(r'^https?://', '', url)  # Remove http:// or https://
    url = re.sub(r'^www\.', '', url)  # Remove www.
    url = url.rstrip('/')  # Remove trailing slash
    return url

def merge_csvs(file1, file2):
    df1 = read_csv_with_auto_detect(file1)
    df2 = read_csv_with_auto_detect(file2)
    
    # Strip whitespace from column names and convert to lowercase
    df1.columns = df1.columns.str.strip().str.lower()
    df2.columns = df2.columns.str.strip().str.lower()
    
    # Identify URL column (assuming it's named 'url' or contains 'url' in its name)
    url_col1 = next((col for col in df1.columns if 'url' in col), None)
    url_col2 = next((col for col in df2.columns if 'url' in col), None)
    
    if url_col1 and url_col2:
        # Standardize URLs
        df1[url_col1] = df1[url_col1].apply(standardize_url)
        df2[url_col2] = df2[url_col2].apply(standardize_url)
        
        # Merge on standardized URL column
        merged_df = pd.merge(df1, df2, left_on=url_col1, right_on=url_col2, how='outer', indicator=True)
        
        # Debug information
        st.write(f"Total rows in file 1: {len(df1)}")
        st.write(f"Total rows in file 2: {len(df2)}")
        st.write(f"Rows in merged dataframe: {len(merged_df)}")
        st.write(f"Matched rows: {len(merged_df[merged_df['_merge'] == 'both'])}")
        st.write(f"Unmatched rows from file 1: {len(merged_df[merged_df['_merge'] == 'left_only'])}")
        st.write(f"Unmatched rows from file 2: {len(merged_df[merged_df['_merge'] == 'right_only'])}")
        
        # Sample of unmatched URLs
        st.write("Sample of unmatched URLs from file 1:")
        st.write(merged_df[merged_df['_merge'] == 'left_only'][url_col1].head())
        st.write("Sample of unmatched URLs from file 2:")
        st.write(merged_df[merged_df['_merge'] == 'right_only'][url_col2].head())
        
        unmatched = merged_df[merged_df['_merge'] != 'both']
        merged_df = merged_df[merged_df['_merge'] == 'both'].drop(columns=['_merge'])
    else:
        st.error("URL column not found in one or both files.")
        return None, None

    return merged_df, unmatched

def main():
    st.title("Patrick's CSV Merger")
    st.markdown("This tool merges two CSV files based on common columns, automatically detecting delimiters and encodings.")

    file1 = st.file_uploader("Upload File 1", type="csv")
    file2 = st.file_uploader("Upload File 2", type="csv")

    if file1 and file2:
        if st.button("Merge CSVs"):
            merged_df, unmatched = merge_csvs(file1, file2)
            if merged_df is not None:
                st.success(f"Files merged successfully! Rows: {merged_df.shape[0]}, Columns: {merged_df.shape[1]}")
                st.dataframe(merged_df.head())

                csv = merged_df.to_csv(index=False)
                st.download_button(
                    label="Download merged CSV",
                    data=csv,
                    file_name="merged_csv.csv",
                    mime="text/csv"
                )

                if not unmatched.empty:
                    st.warning(f"There were {len(unmatched)} unmatched rows.")
                    unmatched_csv = unmatched.to_csv(index=False)
                    st.download_button(
                        label="Download unmatched rows",
                        data=unmatched_csv,
                        file_name="unmatched_rows.csv",
                        mime="text/csv"
                    )
    else:
        st.info("Please upload both CSV files to merge.")

if __name__ == "__main__":
    main()
